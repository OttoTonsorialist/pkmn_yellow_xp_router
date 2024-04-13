from __future__ import annotations
import logging
import time
import threading
from typing import List, Dict, Tuple
from enum import Enum, auto

from pkmn.universal_data_objects import PokemonSpecies
import route_recording.recorder
from route_recording.gamehook_client import GameHookProperty
from routing.route_events import EventDefinition, EvolutionEventDefinition, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, VitaminEventDefinition
from route_recording.game_recorders.gen_one.yellow_gamehook_constants import GameHookConstantConverter, gh_gen_one_const
from pkmn.gen_1.gen_one_constants import gen_one_const
from utils.config_manager import config
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


class _MonKey:
    def __init__(self, species, attack, defense, speed, special_attack, level):
        self.species = species
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.special_attack = special_attack
        self.level = level

    def get_key(self):
        return (
            self.species,
            self.get_dvs(),
        )

    def get_dvs(self):
        return (
            self.attack,
            self.defense,
            self.speed,
            self.special_attack,
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, _MonKey):
            return False
        
        return self.get_key() == other.get_key()
    
    def __hash__(self) -> int:
        return hash(self.get_key())
    
    def __repr__(self) -> str:
        return f"_MonKey: {self.get_key()}"


class Machine:
    def __init__(self, controller:route_recording.recorder.RecorderController, gamehook_client:route_recording.recorder.RecorderGameHookClient, gh_converter:GameHookConstantConverter):
        self._controller = controller
        self._gamehook_client = gamehook_client
        self.gh_converter = gh_converter
        self.debug_mode = config.is_debug_mode()

        self._player_id = None
        self.valid_solo_mon = False
        self._cached_team = []
        self._cached_items = {}
        self._level_up_moves = {}
        self._mons_level_up_loaded = set()
        self._cached_moves = [None, None, None, None]
        self._cached_money = 0

        self._cur_state:State = None
        self._registered_states:Dict[StateType, State] = {}
        self._events_to_generate:List[EventDefinition] = []
        self._last_processed_event = None
        self._active = False

        self._solo_mon_key:_MonKey = self._get_route_defined_mon_key()

        self._processing_thread = threading.Thread(target=self._process_events)
        self._processing_thread.setDaemon(True)
    

    def _get_route_defined_mon_key(self) -> _MonKey:
        cur_dvs = self._controller._controller.get_dvs()
        return _MonKey(
            self._controller._controller.get_final_state().solo_pkmn.species_def.name,
            cur_dvs.attack,
            cur_dvs.defense,
            cur_dvs.speed,
            cur_dvs.special_attack,
            None,
        )

    def _get_mon_key(self, mon_idx) -> _MonKey:
        species_val = self.gh_converter.pkmn_name_convert(
            self._gamehook_client.get(gh_gen_one_const.ALL_KEYS_PLAYER_TEAM_SPECIES[mon_idx]).value
        )
        return _MonKey(
            species_val,
            self._gamehook_client.get(gh_gen_one_const.ALL_KEYS_PLAYER_TEAM_DV_ATTACK[mon_idx]).value,
            self._gamehook_client.get(gh_gen_one_const.ALL_KEYS_PLAYER_TEAM_DV_DEFENSE[mon_idx]).value,
            self._gamehook_client.get(gh_gen_one_const.ALL_KEYS_PLAYER_TEAM_DV_SPEED[mon_idx]).value,
            self._gamehook_client.get(gh_gen_one_const.ALL_KEYS_PLAYER_TEAM_DV_SPECIAL[mon_idx]).value,
            self._gamehook_client.get(gh_gen_one_const.ALL_KEYS_PLAYER_TEAM_LEVEL[mon_idx]).value,
        )
    
    def _load_level_up_moves(self):
        new_mon:PokemonSpecies = current_gen_info().pkmn_db().get_pkmn(self._solo_mon_key.species)
        if not new_mon:
            logger.info(f"Couldn't load level up moves from invalid mon: {self._solo_mon_key.species}")
            return

        for [move_level, move_name] in new_mon.levelup_moves:
            move_level = int(move_level)
            if move_level not in self._level_up_moves:
                self._level_up_moves[(new_mon.name, move_level)] = []
            
            self._level_up_moves[(new_mon.name, move_level)].append(move_name)
    
    def update_team_cache(self, generate_events=True, regenerate_move_cache=False):
        if not generate_events:
            self.valid_solo_mon = False
            self._solo_mon_key = self._get_route_defined_mon_key()
            self._cached_team = []

        new_cache:List[_MonKey] = [self._get_mon_key(i) for i in range(6)]
        # filter out empty mons
        new_cache:List[_MonKey] = [x for x in new_cache if x.species]

        gained_mons = {}
        lost_mons = {}
        for mon_idx in range(len(new_cache)):
            if mon_idx >= len(self._cached_team):
                gained_mons[new_cache[mon_idx]] = gained_mons.get(new_cache[mon_idx], 0) + 1
            elif new_cache[mon_idx] != self._cached_team[mon_idx]:
                gained_mons[new_cache[mon_idx]] = gained_mons.get(new_cache[mon_idx], 0) + 1
                lost_mons[self._cached_team[mon_idx]] = lost_mons.get(self._cached_team[mon_idx], 0) + 1
        
        # account for re-orderings. Any re-ordered mons will have keys present in both dicts
        for cur_mon in gained_mons:
            if cur_mon in lost_mons:
                match_count = min(gained_mons[cur_mon], lost_mons[cur_mon])
                gained_mons[cur_mon] -= match_count
                lost_mons[cur_mon] -= match_count
        
        # drop any mons that have 0 instances, after accounting for reordering
        gained_mons:Dict[_MonKey, int] = dict(filter(lambda x:x[1] > 0, gained_mons.items()))
        lost_mons:Dict[_MonKey, int] = dict(filter(lambda x:x[1] > 0, lost_mons.items()))

        if lost_mons or gained_mons:
            logger.info(f"Team change detected")
            logger.info(f"Losing mons: {lost_mons}")
            logger.info(f"Gaining mons: {gained_mons}")
            logger.info(f"New team: {new_cache}")

        if self.valid_solo_mon and self._solo_mon_key in lost_mons:
            found_evolutions = []
            for test_mon in gained_mons:
                if (
                    test_mon.get_dvs() == self._solo_mon_key.get_dvs() and
                    self._controller._controller.can_evolve_into(test_mon.species)
                ):
                    found_evolutions.append(test_mon)
            
            if len(found_evolutions) >= 1:
                if len(found_evolutions) > 1:
                    err_msg = f"Found multiple new valid solo mons, just taking the first one from the list: {found_evolutions}"
                    logger.error(err_msg)
                    self._queue_new_event(EventDefinition(notes=const.RECORDING_ERROR_FRAGMENT + err_msg))
                self._trigger_evolution(found_evolutions[0])
            else:
                self.valid_solo_mon = False
        elif not self.valid_solo_mon and new_cache:
            logger.info(f"looking for solo mon species: {self._solo_mon_key.species}")
            if len(self._cached_team) == 0:
                # special case: if we had no data previously, then look specifically for the solo mon
                logger.info(f"Creating mons from empty cache. Prioritizing slot 0: {new_cache[0]}")
                if self._solo_mon_key.species == new_cache[0].species:
                    # If this is our first pokemon and the species matches, then allow the DVs to be incorrect
                    # this is just an attempt to avoid burdening the player unnecessarily if their DVs are wrong in the route file
                    if self._solo_mon_key != new_cache[0]:
                        err_msg = f"Expected DV spread: {self._solo_mon_key}, but found solo mon with this DV spread: {new_cache[0]}"
                        logger.error(err_msg)
                        #self._queue_new_event(EventDefinition(notes=const.RECORDING_ERROR_FRAGMENT + err_msg))
                    
                    self.valid_solo_mon = True
                    self._solo_mon_key = new_cache[0]
                    self._load_level_up_moves()

            if not self.valid_solo_mon:
                found_matches = []
                found_evolutions = []
                for test_mon in gained_mons:
                    if test_mon.get_dvs() == self._solo_mon_key.get_dvs():
                        cur_mon_obj = current_gen_info().pkmn_db().get_pkmn(test_mon[0])
                        if not cur_mon_obj is None and cur_mon_obj.name == self._solo_mon_key.species:
                            found_matches.append(test_mon)
                        elif self._controller._controller.can_evolve_into(test_mon[0]):
                            found_evolutions.append(test_mon)
                
                if len(found_matches) >= 1:
                    if len(found_matches) > 1:
                        err_msg = f"Found multiple new valid solo mons, just taking the first one from the list: {found_matches}"
                        logger.error(err_msg)
                        self._queue_new_event(EventDefinition(notes=const.RECORDING_ERROR_FRAGMENT + err_msg))
                    self.valid_solo_mon = True
                    self._load_level_up_moves()
                    self._solo_mon_key = found_matches[0]
                elif len(found_evolutions) >= 1:
                    if len(found_evolutions) > 1:
                        err_msg = f"Found multiple new valid solo mons, just taking the first one from the list: {found_evolutions}"
                        logger.error(err_msg)
                        self._queue_new_event(EventDefinition(notes=const.RECORDING_ERROR_FRAGMENT + err_msg))
                    self.valid_solo_mon = True
                    self._solo_mon_key = found_evolutions[0]
                    self._trigger_evolution(found_evolutions[0])

        if regenerate_move_cache:
            if not self.valid_solo_mon:
                logger.error(f"skipping regeneration of move cache, as no valid solo mon is present")
            else:
                self._move_cache_update(generate_events=False)
        
        logger.info(f"after team cache update, valid_solo_mon: {self.valid_solo_mon}")
        self._cached_team = new_cache
    
    def update_all_cached_info(self):
        # Updates all the info cached in the machine WITHOUT generating events for it
        self.update_team_cache(generate_events=False, regenerate_move_cache=True)
        self._item_cache_update(generate_events=False)
        self._money_cache_update()
        self._controller.entered_new_area(
            self.gh_converter.area_name_convert(self._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value)
        )
    
    def _solo_mon_levelup(self, new_level):
        logger.info(f"levelup detected. {self._solo_mon_key.species} leveling up to {new_level}")
        for move_name in self._level_up_moves.get((self._solo_mon_key.species, new_level), []):
            logger.info(f"queueing up ignore event of move: {move_name}")
            self._queue_new_event(
                EventDefinition(learn_move=LearnMoveEventDefinition(move_name, None, const.MOVE_SOURCE_LEVELUP, level=new_level, mon=self._solo_mon_key.species))
            )
    
    def _trigger_evolution(self, new_mon_key:_MonKey):
        logger.info(f"Evolving into: {new_mon_key.species}")
        self._solo_mon_key = new_mon_key
        self._load_level_up_moves()
        self._queue_new_event(
            EventDefinition(evolution=EvolutionEventDefinition(new_mon_key.species))
        )
        self._solo_mon_levelup(new_mon_key.level)
    
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
                            level=level,
                            mon=self._solo_mon_key.species,
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
                                cur_event.item_event_def.item_name == current_gen_info().get_fight_reward(prev_event.event_definition.get_first_trainer_obj().name)
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