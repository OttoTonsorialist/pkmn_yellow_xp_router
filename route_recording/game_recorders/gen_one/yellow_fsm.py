from __future__ import annotations
import logging
import time
import threading
from typing import List, Dict
from enum import Enum, auto

import route_recording.recorder
from route_recording.gamehook_client import GameHookProperty
from routing.route_events import EventDefinition, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, VitaminEventDefinition
from route_recording.game_recorders.gen_one.yellow_gamehook_constants import GameHookConstantConverter, gh_gen_one_const
from pkmn.gen_1.gen_one_constants import gen_one_const
from utils.constants import const
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


class StateType(Enum):
    UNINITIALIZED = auto()
    RESETTING = auto()
    OVERWORLD = auto()
    BATTLE = auto()
    INVENTORY_CHANGE = auto()
    RARE_CANDY = auto()
    TM = auto()
    VITAMIN = auto()


class State:
    def __init__(self, state_type:StateType, machine:Machine):
        self.state_type = state_type
        self.machine = machine

    def _on_enter(self, prev_state:State):
        pass

    def _on_exit(self, next_state:State):
        pass
    
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        return self.state_type


class Machine:
    def __init__(self, controller:route_recording.recorder.RecorderController, gamehook_client:route_recording.recorder.RecorderGameHookClient, gh_converter:GameHookConstantConverter):
        self._controller = controller
        self._gamehook_client = gamehook_client
        self.gh_converter = gh_converter
        self.debug_mode = const.DEBUG_RECORDING_MODE

        self._player_id = None
        self._solo_mon_species = None
        self._level_up_moves = {}
        self._cached_items = {}
        self._cached_moves = [None, None, None, None]
        self._cached_money = 0

        self._cur_state:State = None
        self._registered_states:Dict[StateType, State] = {}
        self._events_to_generate:List[EventDefinition] = []
        self._last_processed_event = None
        self._active = False

        self._processing_thread = threading.Thread(target=self._process_events)
        self._processing_thread.setDaemon(True)
    
    def register_solo_mon(self, mon_name=None):
        if mon_name is None:
            mon_name = self._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_SPECIES).value

        logger.info(f"Registering solo mon: {mon_name}")
        if self._solo_mon_species is not None:
            logger.error(f"Trying to register solo mon when one is already registered: {self._solo_mon_species}")
        
        self._solo_mon_species = self.gh_converter.pkmn_name_convert(mon_name)
        if self._solo_mon_species is None:
            self._move_cache_update(generate_events=False)
            return

        solo_mon = current_gen_info().pkmn_db().get_pkmn(self._solo_mon_species)
        if solo_mon is None:
            self._controller._controller.trigger_exception(f"Identified solo mon was invalid: {mon_name} from GameHook, converted to {self._solo_mon_species}")
            self._solo_mon_species = None
            self._controller._controller.set_record_mode(False)
            return
        elif solo_mon.name != self._controller._controller.get_init_state().solo_pkmn.name:
            self._controller._controller.trigger_exception(f"Identified solo mon {self._solo_mon_species} from GameHook did not match route solo mon: {self._controller._controller.get_init_state().solo_pkmn.name}")
            self._solo_mon_species = None
            self._controller._controller.set_record_mode(False)
            return

        self._level_up_moves = {}
        for [move_level, move_name] in solo_mon.levelup_moves:
            move_level = int(move_level)
            if move_level not in self._level_up_moves:
                self._level_up_moves[move_level] = []
            
            self._level_up_moves[move_level].append(move_name)
        
        self._move_cache_update(generate_events=False)
    
    def update_all_cached_info(self, include_solo_mon=False):
        # Updates all the info cached in the machine WITHOUT generating events for it
        if include_solo_mon:
            self.register_solo_mon()
        else:
            self._move_cache_update(generate_events=False)
        self._item_cache_update(generate_events=False)
        self._money_cache_update()
        self._controller.entered_new_area(
            self.gh_converter.area_name_convert(self._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value)
        )
    
    def _solo_mon_levelup(self, new_level):
        for move_name in self._level_up_moves.get(new_level, []):
            self._queue_new_event(
                EventDefinition(learn_move=LearnMoveEventDefinition(move_name, None, const.MOVE_SOURCE_LEVELUP, level=new_level))
            )
    
    def _money_cache_update(self):
        new_cache = self._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MONEY).value
        if new_cache == self._cached_money:
            return None
        
        result = new_cache > self._cached_money
        self._cached_money = new_cache
        return result
    
    def _move_cache_update(self, generate_events=True, tm_name=None, hm_expected=False, levelup_source=False):
        new_cache = []
        new_cache.append(self.gh_converter.move_name_convert(self._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_MOVE_1).value))
        new_cache.append(self.gh_converter.move_name_convert(self._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_MOVE_2).value))
        new_cache.append(self.gh_converter.move_name_convert(self._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_MOVE_3).value))
        new_cache.append(self.gh_converter.move_name_convert(self._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_MOVE_4).value))

        if generate_events:
            old_moves = set([x for x in self._cached_moves if x is not None])
            new_moves = set([x for x in new_cache if x is not None])

            deleted_moves = old_moves - new_moves
            to_delete_move = None
            if len(deleted_moves) == 1:
                to_delete_move = list(deleted_moves)[0]
            elif len(deleted_moves) > 1:
                logger.error(f"Got multiple deleted moves..? {deleted_moves}, from {self._cached_moves} to {new_cache}")
                to_delete_move = list(deleted_moves)[0]
            
            learned_moves = new_moves - old_moves
            to_learn_move = None
            if len(learned_moves) == 1:
                to_learn_move = list(learned_moves)[0]
            elif len(learned_moves) > 1:
                logger.error(f"Got multiple learned moves..? {learned_moves}, from {self._cached_moves} to {new_cache}")
                to_learn_move = list(learned_moves)[0]
            
            if to_learn_move is None and to_delete_move is not None:
                logger.error(f"Move deleted but no move learned? That seems impossible... from {self._cached_moves} to {new_cache}")
            elif to_learn_move is not None:
                if levelup_source:
                    source = const.MOVE_SOURCE_LEVELUP
                    level = self._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_LEVEL).value
                else:
                    if hm_expected:
                        tm_name = self.gh_converter.get_hm_name(to_learn_move)
                    source = tm_name
                    level = const.LEVEL_ANY

                self._queue_new_event(
                    EventDefinition(
                        learn_move=LearnMoveEventDefinition(
                            self.gh_converter.move_name_convert(to_learn_move),
                            self.gh_converter.move_name_convert(to_delete_move),
                            source,
                            level=level
                        )
                    )
                )
        
        self._cached_moves = new_cache
        

    def _item_cache_update(self, generate_events=True, purchase_expected=False, sale_expected=False, vitamin_flag=False, candy_flag=False, tm_flag=False):
        new_cache = {}
        for i in range(0, 20):
            item_type = self._gamehook_client.get(gh_gen_one_const.ALL_KEYS_ITEM_TYPE[i]).value
            if item_type is None:
                break
            
            new_cache[item_type] = self._gamehook_client.get(gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY[i]).value
        
        compared = set()
        gained_items = {}
        lost_items = {}
        for cur_item, cur_count in self._cached_items.items():
            new_count = new_cache.get(cur_item, 0)
            if new_count > cur_count:
                gained_items[cur_item] = new_count - cur_count
            elif cur_count > new_count:
                lost_items[cur_item] = cur_count - new_count
            compared.add(cur_item)

        for new_item, new_count in new_cache.items():
            if new_item in compared:
                continue
            cur_count = 0
            if new_count > cur_count:
                gained_items[new_item] = new_count - cur_count
            elif cur_count > new_count:
                lost_items[new_item] = cur_count - new_count

        self._cached_items = new_cache
        if generate_events:
            if len(gained_items) > 0 and sale_expected:
                logger.error(f"Gained the following items when expecting to be losing items to selling... {gained_items}")
            for cur_gained_item, cur_gain_num in gained_items.items():
                app_item_name = self.gh_converter.item_name_convert(cur_gained_item)
                if app_item_name == gh_gen_one_const.OAKS_PARCEL:
                    continue
                elif app_item_name in gh_gen_one_const.VENDING_MACHINE_DRINKS:
                    # vending machines have a dumb delay between giving you the item, and the actual money being given to the player
                    # Just force any "pickups" of vending machine drinks to be purchases, since the only way to acquire these is by purchasing them
                    self._queue_new_event(
                        EventDefinition(
                            item_event_def=InventoryEventDefinition(app_item_name, cur_gain_num, True, True)
                        )
                    )
                else:
                    self._queue_new_event(
                        EventDefinition(
                            item_event_def=InventoryEventDefinition(app_item_name, cur_gain_num, True, purchase_expected)
                        )
                    )
                    
            if len(lost_items) > 0 and purchase_expected:
                logger.error(f"Lost the following items when expecting to be gain items to purchasing... {lost_items}")
            for cur_lost_item, cur_lost_num in lost_items.items():
                app_item_name = self.gh_converter.item_name_convert(cur_lost_item)
                if app_item_name == gh_gen_one_const.OAKS_PARCEL:
                    continue
                if vitamin_flag and self.gh_converter.is_game_vitamin(cur_lost_item):
                    if sale_expected:
                        logger.error("Expected sale, but looks like vitamins were used too???")
                    self._queue_new_event(
                        EventDefinition(vitamin=VitaminEventDefinition(app_item_name, cur_lost_num))
                    )
                elif candy_flag and self.gh_converter.is_game_rare_candy(cur_lost_item):
                    if sale_expected:
                        logger.error("Expected sale, but looks like rare candy was used too???")
                    self._queue_new_event(
                        EventDefinition(rare_candy=RareCandyEventDefinition(cur_lost_num))
                    )
                elif tm_flag and self.gh_converter.is_game_tm(cur_lost_item):
                    if sale_expected:
                        logger.error("Expected sale, but looks like TM was used too???")
                    self._move_cache_update(tm_name=app_item_name)
                else:
                    self._queue_new_event(
                        EventDefinition(
                            item_event_def=InventoryEventDefinition(app_item_name, cur_lost_num, False, sale_expected)
                        )
                    )
    
    def register(self, state:State):
        if state.state_type in self._registered_states:
            raise ValueError(f"Cannot have multiple states of type {state.state_type}")
        self._registered_states[state.state_type] = state
    
    def startup(self):
        self._active = True
        self._cur_state = self._registered_states[StateType.UNINITIALIZED]
        self._cur_state._on_enter(None)
        self._controller.set_game_state(self._cur_state.state_type)
        self._processing_thread.start()
    
    def handle_event(self, new_prop:GameHookProperty, prev_prop:GameHookProperty):
        if (
            self.debug_mode and
            new_prop.path != gh_gen_one_const.KEY_AUDIO_CHANNEL_4 and
            new_prop.path != gh_gen_one_const.KEY_AUDIO_CHANNEL_5 and
            new_prop.path != gh_gen_one_const.KEY_AUDIO_CHANNEL_7 and
            new_prop.path != gh_gen_one_const.KEY_GAMETIME_SECONDS
        ):
            logger.info(f"Change of {new_prop.path} from {prev_prop.value} to {new_prop.value} for state {self._cur_state.state_type}")
        result = self._cur_state.transition(new_prop, prev_prop)
        if result != self._cur_state.state_type:
            new_state = self._registered_states.get(result)
            if new_state is None:
                raise ValueError(f"Illegal transition from {self._cur_state.state_type} to unknown state {result}")

            logger.info(f"Moving from {self._cur_state.state_type} state to {new_state.state_type} due to change {new_prop.path}, from {prev_prop.value} to {new_prop.value}")
            self._cur_state._on_exit(new_state)
            new_state._on_enter(self._cur_state)
            self._cur_state = new_state
            self._controller.set_game_state(self._cur_state.state_type)
    
    def shutdown(self):
        logger.info("Shutting down Yellow recording FSM")
        self._active = False
        if self._processing_thread.is_alive():
            self._processing_thread.join()
    
    def _queue_new_event(self, event_def:EventDefinition):
        self._events_to_generate.append(event_def)
    
    def _process_events(self):
        # Converts all in-game data to app data, then sends the events to the main app

        # This is all done in a background thread so that the threads responding to the gamehook events
        # can react and update their time-sensitive state asap without blocking on any extra processing
        while self._active or len(self._events_to_generate) != 0:
            if len(self._events_to_generate) != 0:
                cur_event = self._events_to_generate.pop(0)
                try:
                    if cur_event.notes == gh_gen_one_const.RESET_FLAG:
                        logger.info(f"Resetting to last save...")
                        self._controller.game_reset()
                        continue
                    elif None is not cur_event.trainer_def:
                        trainer = current_gen_info().trainer_db().get_trainer(cur_event.trainer_def.trainer_name)
                        if trainer is None:
                            msg = f"Failed to find trainer from GameHook: {cur_event.trainer_def.trainer_name}"
                            logger.error(msg)
                            self._controller.add_event(
                                EventDefinition(notes=const.RECORDING_ERROR_FRAGMENT + msg)
                            )
                            continue
                        if cur_event.notes == gh_gen_one_const.TRAINER_LOSS_FLAG:
                            logger.info(f"Handling trainer loss: {cur_event.trainer_def.trainer_name}")
                            self._controller.lost_trainer_battle(cur_event.trainer_def.trainer_name)
                            continue
                        elif cur_event.notes == gh_gen_one_const.PAY_DAY_FLAG:
                            test_obj = self._controller._controller.get_previous_event()
                            while not self._controller.is_trainer_event(test_obj, cur_event.trainer_def.trainer_name):
                                if test_obj is None:
                                    break
                                test_obj = self._controller._controller.get_previous_event(test_obj.group_id)
                            
                            if test_obj is None:
                                logger.error(f"Failed to find trainer fight to update for exp split behavior")
                            else:
                                cur_event.notes = ""
                                cur_event.trainer_def.pay_day_amount -= trainer.money
                                logger.info(f"Updating pay day for trainer {cur_event.trainer_def.trainer_name} to {cur_event.trainer_def.pay_day_amount}")
                                self._controller._controller.update_existing_event(test_obj.group_id, cur_event)
                            
                            continue
                    elif None is not cur_event.item_event_def:
                        item = current_gen_info().item_db().get_item(cur_event.item_event_def.item_name)
                        if item is None:
                            msg = f"Failed to find item from GameHook: {cur_event.item_event_def.item_name} for event {cur_event}"
                            logger.error(msg)
                            self._controller.add_event(
                                EventDefinition(notes=const.RECORDING_ERROR_FRAGMENT + msg)
                            )
                            continue

                        if cur_event.item_event_def.is_acquire:
                            prev_event = self._controller._controller.get_previous_event()
                            if (
                                prev_event is not None and
                                prev_event.event_definition.trainer_def is not None and
                                cur_event.item_event_def.item_name == current_gen_info().get_fight_reward(prev_event.event_definition.get_trainer_obj().name)
                            ):
                                logger.info(f"Intentionally ignoring item add for battle reward: {cur_event.item_event_def.item_name}")
                                continue
                            elif item.is_key_item and self._controller._controller.get_final_state().inventory._item_lookup.get(item.name) != None:
                                logger.info(f"Intentionally ignoring item add for duplicate key item: {cur_event.item_event_def.item_name}")
                                continue
                    elif None is not cur_event.learn_move:
                        to_learn = current_gen_info().move_db().get_move(cur_event.learn_move.move_to_learn)
                        to_forget = current_gen_info().move_db().get_move(cur_event.learn_move.destination)
                        if to_learn is None:
                            msg = f"Failed to find move from GameHook: {cur_event.learn_move.move_to_learn} for event {cur_event}"
                            logger.error(msg)
                            self._controller.add_event(
                                EventDefinition(notes=const.RECORDING_ERROR_FRAGMENT + msg)
                            )
                            continue
                        elif cur_event.learn_move.destination is not None and to_forget is None:
                            msg = f"Failed to find move from GameHook: {cur_event.learn_move.destination} for event {cur_event}"
                            logger.error(msg)
                            self._controller.add_event(
                                EventDefinition(notes=const.RECORDING_ERROR_FRAGMENT + msg)
                            )
                            continue
                    elif None is not cur_event.wild_pkmn_info:
                        if current_gen_info().pkmn_db().get_pkmn(cur_event.wild_pkmn_info.name) is None:
                            msg = f"Failed to find wild pokemon from GameHook: {cur_event.wild_pkmn_info.name} for event {cur_event}"
                            logger.error(msg)
                            self._controller.add_event(
                                EventDefinition(notes=const.RECORDING_ERROR_FRAGMENT + msg)
                            )
                            continue

                    logger.info(f"adding new event: {cur_event}")
                    self._controller.add_event(cur_event)
                except Exception as e:
                    logger.error(f"Exception occurred trying to process event: {cur_event}")
                    logger.exception(e)
                    self._controller._controller.trigger_exception(e)

            elif self._active:
                time.sleep(0.1)