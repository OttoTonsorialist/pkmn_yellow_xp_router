from __future__ import annotations
import logging

from route_recording.game_recorders.gen_two.crystal_fsm import Machine, State, StateType
from route_recording.gamehook_client import GameHookProperty
from routing.route_events import BlackoutEventDefinition, EventDefinition, HealEventDefinition, HoldItemEventDefinition, SaveEventDefinition, TrainerEventDefinition, WildPkmnEventDefinition
from route_recording.game_recorders.gen_two.crystal_gamehook_constants import gh_gen_two_const
from pkmn.gen_2.gen_two_constants import gen_two_const
from utils.constants import const

logger = logging.getLogger(__name__)


class WatchForResetState(State):
    def watch_for_reset(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if self.machine._player_id is not None and new_prop.path == gh_gen_two_const.KEY_PLAYER_PLAYERID and new_prop.value == 0:
            return StateType.RESETTING
        return None


def auto_reset(transition_fn):
    def wrapper(*args, **kwargs):
        obj:WatchForResetState = args[0]
        result = obj.watch_for_reset(*args[1:], **kwargs)
        if result is not None:
            return result
        
        return transition_fn(*args, **kwargs)
    return wrapper


class WatchState(State):
    def __init__(self, machine: Machine):
        super().__init__(StateType.UNINITIALIZED, machine)
        self._is_waiting = False
        self._seconds_delay = 2
    
    def _on_enter(self, prev_state: State):
        self._is_waiting = False
        self._seconds_delay = 2
    
    def _on_exit(self, next_state: State):
        pass

    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path != gh_gen_two_const.KEY_GAMETIME_SECONDS:
            logger.info(f"Changing {new_prop.path} from {prev_prop.value} to {new_prop.value}({type(new_prop.value)})")
        return self.state_type


class UninitializedState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.UNINITIALIZED, machine)
        self._is_waiting = False
        self._seconds_delay = 2
    
    def _on_enter(self, prev_state: State):
        self._is_waiting = False
        self._seconds_delay = 2
    
    def _on_exit(self, next_state: State):
        self.machine._player_id = self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_PLAYERID).value
        # Shouldn't really happen ever, but if the player connects to an active game, but then resets the emulator
        # it's possible that we exit (due to transitioning to a reset state) while the player id is 0
        # If this happens, just ignore the update, let the ResettingState handle setting the player id
        if self.machine._player_id == 0:
            self.machine._player_id = None
        
        self.machine.update_all_cached_info()
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_two_const.KEY_GAMETIME_SECONDS:
            if self._seconds_delay <= 0:
                cur_battle_mode = self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_MODE)
                if cur_battle_mode == gh_gen_two_const.WILD_BATTLE_TYPE or cur_battle_mode == gh_gen_two_const.TRAINER_BATTLE_TYPE:
                    return StateType.BATTLE
                else:
                    return StateType.OVERWORLD
            elif not self._is_waiting and self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_PLAYERID).value != 0:
                self._is_waiting = True

            if self._is_waiting:
                self._seconds_delay -= 1

        return self.state_type


class ResettingState(State):
    def __init__(self, machine: Machine):
        super().__init__(StateType.RESETTING, machine)
        self._is_waiting = False
        self._seconds_delay = None
    
    def _on_enter(self, prev_state: State):
        self._is_waiting = False
        self._seconds_delay = 2
        self.machine._queue_new_event(EventDefinition(notes=gh_gen_two_const.RESET_FLAG))
    
    def _on_exit(self, next_state: State):
        new_player_id = self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_PLAYERID).value
        if self.machine._player_id is None:
            self.machine._player_id = new_player_id
        elif self.machine._player_id != new_player_id:
            self.machine._controller.route_restarted()

        self.machine.update_all_cached_info()

    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_two_const.KEY_PLAYER_PLAYERID:
            if prev_prop.value == 0 and new_prop.value != 0:
                self._is_waiting = True
        elif new_prop.path == gh_gen_two_const.KEY_GAMETIME_SECONDS:
            if not self._is_waiting:
                self._is_waiting = True
            elif self._seconds_delay <= 0:
                return StateType.OVERWORLD
            else:
                self._seconds_delay -= 1

        return self.state_type


class BattleState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.BATTLE, machine)
        self.is_trainer_battle = False
        self._trainer_name = ""
        self._trainer_event_created = False
        self._defeated_trainer_mons = []
        self._waiting_for_moves = False
        self._move_update_delay = 0
        self._waiting_for_items = False
        self._item_update_delay = 0
        self._loss_detected = False
        self._evolution_detected = False
        self._held_item_consumed = False
        self._cached_mon_species = ""
        self._cached_mon_level = 0
        self._exp_split = []
        self._enemy_mon_order = []
        self._friendship_data = []
        self._battle_started = False
        self._initial_money = 0
    
    def _on_enter(self, prev_state: State):
        self._defeated_trainer_mons = []
        self._waiting_for_moves = False
        self._move_update_delay = 0
        self._waiting_for_items = False
        self._item_update_delay = 0
        self.is_trainer_battle = self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_MODE).value == gh_gen_two_const.TRAINER_BATTLE_TYPE
        self._trainer_event_created = False
        self._loss_detected = False
        self._evolution_detected = False
        self._held_item_consumed = False
        self._cached_mon_species = ""
        self._cached_mon_level = 0
        self._trainer_name = ""
        self._exp_split = [set([0])]
        self._enemy_mon_order = []
        self._friendship_data = []
        self._battle_started = False
        self._initial_money = self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_MONEY).value
        
        logger.info(f"Entered battle. With trainer initially? {self.is_trainer_battle}")
    

    def _create_initial_trainer_event(self):

        if self.is_trainer_battle:
            self._exp_split = [set([0]) for _ in range(self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_TRAINER_TOTAL_POKEMON).value)]
            self._trainer_name = self.machine.gh_converter.trainer_name_convert(
                self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_TRAINER_CLASS).value,
                self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_TRAINER_NUMBER).value,
            )

            return_custom_move_data = None
            if gen_two_const.RETURN_MOVE_NAME in self.machine._cached_moves:
                return_custom_move_data = []
                cur_friendship = self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_MON_FRIENDSHIP).value
                for _ in range(6):
                    return_custom_move_data.append({
                        const.PLAYER_KEY: {gen_two_const.RETURN_MOVE_NAME: str(int(cur_friendship / 2.5))},
                        const.ENEMY_KEY: {}
                    })

            self.machine._queue_new_event(
                EventDefinition(trainer_def=TrainerEventDefinition(self._trainer_name, custom_move_data=return_custom_move_data))
            )
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            if self.is_trainer_battle:
                final_exp_split = [len(x) for x in self._exp_split]
                if not any([True for x in final_exp_split if x > 1]):
                    final_exp_split = None
                
                final_mon_order = [self._enemy_mon_order.index(x) for x in sorted(self._enemy_mon_order)]

                return_custom_move_data = None
                if gen_two_const.RETURN_MOVE_NAME in self.machine._cached_moves:
                    return_custom_move_data = []
                    for cur_friendship in self._friendship_data:
                        return_custom_move_data.append({
                            const.PLAYER_KEY: {gen_two_const.RETURN_MOVE_NAME: str(int(cur_friendship / 2.5))},
                            const.ENEMY_KEY: {}
                        })

                self.machine._queue_new_event(
                    EventDefinition(
                        trainer_def=TrainerEventDefinition(
                            self._trainer_name,
                            exp_split=final_exp_split,
                            mon_order=final_mon_order,
                            custom_move_data=return_custom_move_data,
                            pay_day_amount=self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_MONEY).value - self._initial_money,
                        ),
                        notes=gh_gen_two_const.ROAR_FLAG
                    )
                )
            if self._loss_detected:
                if self.is_trainer_battle:
                    self.machine._queue_new_event(
                        EventDefinition(trainer_def=TrainerEventDefinition(self._trainer_name), notes=gh_gen_two_const.TRAINER_LOSS_FLAG)
                    )
                    for trainer_mon_event in self._defeated_trainer_mons:
                        self.machine._queue_new_event(trainer_mon_event)
                self.machine._queue_new_event(EventDefinition(blackout=BlackoutEventDefinition()))
            elif self.is_trainer_battle:
                # if we won a trainer battle, check for special case of beating lance
                if self._trainer_name.startswith("Champion"):
                    self.machine._queue_new_event(EventDefinition(save=SaveEventDefinition(location="Post-Champion Autosave")))
            if self._waiting_for_moves:
                if self._evolution_detected:
                    self.machine.update_team_cache()
                self.machine._move_cache_update(levelup_source=True)
            if self._waiting_for_items:
                self.machine._item_cache_update()
            if self._held_item_consumed:
                self.machine._queue_new_event(EventDefinition(hold_item=HoldItemEventDefinition(None, True)))

    @auto_reset
    def transition(self, new_prop: GameHookProperty, prev_prop: GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_two_const.KEY_PLAYER_MON_EXPPOINTS:
            if not self._cached_mon_species or not self._cached_mon_level:
                logger.error(f"Solo mon gained experience, but we didn't properly cache which enemy mon was defeated...")
            else:
                if self.is_trainer_battle:
                    self._defeated_trainer_mons.append(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                        self._cached_mon_species,
                        self._cached_mon_level,
                        trainer_pkmn=True
                    )))
                else:
                    self.machine._queue_new_event(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                        self._cached_mon_species,
                        self._cached_mon_level,
                    )))
                self._cached_mon_species = ""
                self._cached_mon_level = 0
        elif new_prop.path == gh_gen_two_const.KEY_BATTLE_START:
            if prev_prop.value == 1 and new_prop.value == 0:
                # when the battle start flag goes from ON (meaning setup is happening, I think) to OFF (meaning setup is now done)
                # that's when we know the battle has started
                self._battle_started = True
        elif new_prop.path == gh_gen_two_const.KEY_BATTLE_ENEMY_HP:
            if new_prop.value == 0:
                self._cached_mon_species = self.machine.gh_converter.pkmn_name_convert(self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_ENEMY_SPECIES).value)
                self._cached_mon_level = self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_ENEMY_LEVEL).value
                self._friendship_data.append(self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_MON_FRIENDSHIP).value)
        elif new_prop.path == gh_gen_two_const.KEY_BATTLE_TEXT_BUFFER:
            if self._trainer_name == "":
                self.is_trainer_battle = self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_MODE).value == gh_gen_two_const.TRAINER_BATTLE_TYPE
                if self.is_trainer_battle:
                    self._create_initial_trainer_event()
                else:
                    # Just fill it with junk so we stop querying this
                    self._trainer_name = "WildMon"
        elif new_prop.path == gh_gen_two_const.KEY_BATTLE_PLAYER_MON_HP:
            player_mon_pos = self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_PLAYER_MON_PARTY_POS).value
            if player_mon_pos == 0 and new_prop.value <= 0:
                if self._battle_started:
                    self._loss_detected = True
            elif new_prop.value <= 0:
                enemy_mon_pos = self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_ENEMY_MON_PARTY_POS).value
                if player_mon_pos in self._exp_split[enemy_mon_pos]:
                    self._exp_split[enemy_mon_pos].remove(player_mon_pos)

        elif new_prop.path in gh_gen_two_const.KEY_PLAYER_MON_SPECIES:
            self._evolution_detected = True
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_PLAYER_MOVES:
            if not self._waiting_for_moves:
                self._move_update_delay = 2
                self._waiting_for_moves = True
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_ALL_ITEM_FIELDS:
            if not self._waiting_for_items:
                self._item_update_delay = 2
                self._waiting_for_items = True
        elif new_prop.path == gh_gen_two_const.KEY_GAMETIME_SECONDS:
            if self._waiting_for_moves:
                if self._move_update_delay <= 0:
                    self._waiting_for_moves = False
                    if self._evolution_detected:
                        self.machine.update_team_cache()
                    self.machine._move_cache_update(levelup_source=True)
                else:
                    self._move_update_delay -= 1
            if self._waiting_for_items:
                if self._item_update_delay <= 0:
                    self._waiting_for_items = False
                    self.machine._item_cache_update()
                else:
                    self._item_update_delay -= 1
        elif new_prop.path == gh_gen_two_const.KEY_PLAYER_MON_LEVEL:
            self.machine._solo_mon_levelup(new_prop.value)
        elif new_prop.path == gh_gen_two_const.KEY_PLAYER_MON_HELD_ITEM:
            self._held_item_consumed = True
        elif new_prop.path == gh_gen_two_const.KEY_BATTLE_PLAYER_MON_PARTY_POS:
            enemy_mon_pos = self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_ENEMY_MON_PARTY_POS).value
            if (
                (new_prop.value >= 0 and new_prop.value < 6) and
                (enemy_mon_pos >= 0 and enemy_mon_pos < 6)
            ):
                self._exp_split[enemy_mon_pos].add(new_prop.value)
        elif new_prop.path == gh_gen_two_const.KEY_BATTLE_ENEMY_MON_PARTY_POS:
            if new_prop.value >= 0 and new_prop.value < len(self._exp_split):
                self._exp_split[new_prop.value] = set([self.machine._gamehook_client.get(gh_gen_two_const.KEY_BATTLE_PLAYER_MON_PARTY_POS).value])
            # NOTE: this logic won't perfectly reflect things if the player uses roar/whirlwind
            # or if the enemy trainer switches pokemon (and doesn't only send out new mons on previous death)
            if new_prop.value not in self._enemy_mon_order:
                self._enemy_mon_order.append(new_prop.value)
        elif new_prop.path == gh_gen_two_const.KEY_BATTLE_MODE:
            if new_prop.value is None:
                return StateType.OVERWORLD
        
        return self.state_type


class InventoryChangeState(WatchForResetState):
    BASE_DELAY = 2
    def __init__(self, machine: Machine):
        super().__init__(StateType.INVENTORY_CHANGE, machine)
        self._seconds_delay = self.BASE_DELAY
        self._money_gained = False
        self._money_lost = False
        self._held_item_changed = False
    
    def _on_enter(self, prev_state: State):
        self._seconds_delay = self.BASE_DELAY
        self._money_gained = True if self.machine._money_cache_update() else False
        self._money_lost = False
        self._held_item_changed = False
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(
                sale_expected=self._money_gained,
                purchase_expected=self._money_lost,
                held_item_changed=self._held_item_changed
            )
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_two_const.KEY_PLAYER_MONEY:
            if new_prop.value > prev_prop.value:
                self._money_gained = True
            else:
                self._money_lost = True
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_ALL_ITEM_FIELDS:
            self._seconds_delay = self.BASE_DELAY
        elif new_prop.path == gh_gen_two_const.KEY_PLAYER_MON_HELD_ITEM:
            if self.machine._solo_mon_key.species == self.machine.gh_converter.pkmn_name_convert(self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_MON_SPECIES).value):
                self._held_item_changed = True
                logger.info(f"gotem: {self._held_item_changed}")
        elif new_prop.path == gh_gen_two_const.KEY_GAMETIME_SECONDS:
            if self._seconds_delay <= 0:
                return StateType.OVERWORLD
            else:
                self._seconds_delay -= 1

        return self.state_type


class UseRareCandyState(WatchForResetState):
    BASE_DELAY = 2
    def __init__(self, machine: Machine):
        super().__init__(StateType.RARE_CANDY, machine)
        self._move_learned = False
        self._item_removal_detected = False
        self._cur_delay = self.BASE_DELAY

    def _on_enter(self, prev_state: State):
        self._move_learned = False
        self._item_removal_detected = False
        self._cur_delay = self.BASE_DELAY
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(candy_flag=True)
            self.machine._solo_mon_levelup(self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_MON_LEVEL).value)
            self.machine.update_team_cache()
            if self._move_learned:
                self.machine._move_cache_update(levelup_source=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path in gh_gen_two_const.ALL_KEYS_PLAYER_MOVES:
            self._move_learned = True
        elif new_prop.path == gh_gen_two_const.KEY_ITEM_COUNT:
            self._item_removal_detected = True
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_ITEM_QUANTITY:
            if not self._item_removal_detected:
                return StateType.OVERWORLD
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_ITEM_TYPE:
            if new_prop.value is None:
                return StateType.OVERWORLD
        elif new_prop.path in gh_gen_two_const.KEY_GAMETIME_SECONDS:
            if self._item_removal_detected:
                if self._cur_delay <= 0:
                    return StateType.OVERWORLD
                else:
                    self._cur_delay -= 1
        elif new_prop.path in [gh_gen_two_const.KEY_OVERWORLD_X_POS, gh_gen_two_const.KEY_OVERWORLD_Y_POS]:
            # fail-safe. If the player is moving around, rare candy is definitely over. Just give up
            return StateType.OVERWORLD

        return self.state_type


class UseTMState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.TM, machine)

    def _on_enter(self, prev_state: State):
        pass
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(tm_flag=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_two_const.KEY_ITEM_COUNT:
            self._item_removal_detected = True
        elif new_prop.path in gh_gen_two_const.ALL_TM_KEYS:
            return StateType.OVERWORLD

        return self.state_type


class MoveDeleteState(WatchForResetState):
    BASE_DELAY = 2
    def __init__(self, machine: Machine):
        super().__init__(StateType.MOVE_DELETE, machine)
        self._cur_delay = self.BASE_DELAY

    def _on_enter(self, prev_state: State):
        self._cur_delay = self.BASE_DELAY
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._move_cache_update(tutor_expected=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_two_const.KEY_GAMETIME_SECONDS:
            if self._cur_delay <= 0:
                return StateType.OVERWORLD
            else:
                self._cur_delay -= 1
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_PLAYER_MOVES:
            self._cur_delay = self.BASE_DELAY

        return self.state_type


class UseVitaminState(WatchForResetState):
    BASE_DELAY = 2
    def __init__(self, machine: Machine):
        super().__init__(StateType.VITAMIN, machine)
        self._item_removal_detected = False
        self._cur_delay = self.BASE_DELAY

    def _on_enter(self, prev_state: State):
        self._item_removal_detected = False
        self._cur_delay = self.BASE_DELAY
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(vitamin_flag=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_two_const.KEY_ITEM_COUNT:
            self._item_removal_detected = True
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_ITEM_QUANTITY:
            if not self._item_removal_detected:
                return StateType.OVERWORLD
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_ITEM_TYPE:
            if new_prop.value is None:
                return StateType.OVERWORLD
        elif new_prop.path == gh_gen_two_const.KEY_GAMETIME_SECONDS:
            if self._item_removal_detected:
                if self._cur_delay <= 0:
                    return StateType.OVERWORLD
                else:
                    self._cur_delay -= 1

        return self.state_type


class OverworldState(WatchForResetState):
    BASE_DELAY = 2
    def __init__(self, machine: Machine):
        super().__init__(StateType.OVERWORLD, machine)
        self._waiting_for_registration = False
        self._register_delay = self.BASE_DELAY
    
    def _on_enter(self, prev_state: State):
        self.machine._money_cache_update()
        self.machine.update_team_cache()
        self._waiting_for_registration = False
        self._register_delay = self.BASE_DELAY
        self._waiting_for_new_file = False
        self._new_file_delay = self.BASE_DELAY

        self._waiting_for_solo_mon_in_slot_1 = False
        self._wrong_mon_delay = self.BASE_DELAY
        self._wrong_mon_in_slot_1 = False
    
    def _on_exit(self, next_state: State):
        pass
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        # intentionally ignore all updates while waiting for a new file
        if self._waiting_for_new_file or self._waiting_for_solo_mon_in_slot_1:
            if new_prop.path == gh_gen_two_const.KEY_GAMETIME_SECONDS:
                if self._wrong_mon_delay <= 0:
                    self._waiting_for_solo_mon_in_slot_1 = False
                    self._wrong_mon_in_slot_1 = False
                if self._new_file_delay <= 0:
                    self._waiting_for_new_file = False
                    self.machine._controller.route_restarted()
                    self.machine.update_all_cached_info()
                self._new_file_delay -= 1
                self._wrong_mon_delay -= 1
            
            return self.state_type

        if new_prop.path == gh_gen_two_const.KEY_BATTLE_MODE:
            return StateType.BATTLE
        elif new_prop.path == gh_gen_two_const.KEY_OVERWORLD_MAP or new_prop.path == gh_gen_two_const.KEY_OVERWORLD_MAP_NUM:
            self.machine._controller.entered_new_area(
                f"{self.machine._gamehook_client.get(gh_gen_two_const.KEY_OVERWORLD_MAP).value} Map "
                f"{self.machine._gamehook_client.get(gh_gen_two_const.KEY_OVERWORLD_MAP_NUM).value}"
            )
        elif new_prop.path == gh_gen_two_const.KEY_PLAYER_PLAYERID:
            if prev_prop.value and self.machine._player_id != self.machine._gamehook_client.get(gh_gen_two_const.KEY_PLAYER_PLAYERID).value:
                self._waiting_for_new_file = True
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_ALL_ITEM_FIELDS:
            return StateType.INVENTORY_CHANGE
        elif new_prop.path == gh_gen_two_const.KEY_PLAYER_MON_HELD_ITEM:
            if not self._wrong_mon_in_slot_1:
                self.machine._queue_new_event(
                    EventDefinition(
                        hold_item=HoldItemEventDefinition(self.machine.gh_converter.item_name_convert(new_prop.value)),
                        notes=gh_gen_two_const.HELD_CHECK_FLAG
                    )
                )
        elif new_prop.path == gh_gen_two_const.KEY_PLAYER_MON_SPECIES:
            if not prev_prop.value:
                self._waiting_for_registration = True
            elif self.machine._solo_mon_key.species == self.machine.gh_converter.pkmn_name_convert(prev_prop.value):
                self._wrong_mon_in_slot_1 = True
            elif self.machine._solo_mon_key.species == self.machine.gh_converter.pkmn_name_convert(new_prop.value):
                self._wrong_mon_delay = self.BASE_DELAY
                self._waiting_for_solo_mon_in_slot_1 = True
        elif new_prop.path == gh_gen_two_const.KEY_PLAYER_MON_LEVEL:
            if not self._waiting_for_registration and not self._wrong_mon_in_slot_1:
                if new_prop.value == prev_prop.value + 1:
                    return StateType.RARE_CANDY
                logger.warning(f"Ignoring level change event that seems impossible, transitioning from: {prev_prop.value} to {new_prop.value}")
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_PLAYER_MOVES:
            if not self._waiting_for_registration and not self._wrong_mon_in_slot_1:
                all_cur_moves = []
                for move_path in gh_gen_two_const.ALL_KEYS_PLAYER_MOVES:
                    if move_path == prev_prop.path:
                        all_cur_moves.append(prev_prop.value)
                    else:
                        all_cur_moves.append(self.machine._gamehook_client.get(move_path).value)
                if new_prop.value is None or new_prop.value in all_cur_moves:
                    return StateType.MOVE_DELETE
                elif self.machine.gh_converter.get_hm_name(new_prop.value) is not None:
                    self.machine._move_cache_update(hm_expected=True)
                elif self.machine.gh_converter.is_tutor_move(new_prop.value):
                    self.machine._move_cache_update(tutor_expected=True)
                else:
                    return StateType.TM
        elif new_prop.path in gh_gen_two_const.ALL_KEYS_STAT_EXP:
            if not self._waiting_for_registration and not self._wrong_mon_in_slot_1:
                return StateType.VITAMIN
        elif new_prop.path == gh_gen_two_const.KEY_AUDIO_CURRENT_SOUND:
            if new_prop.value == gh_gen_two_const.PKMN_CENTER_HEAL_SOUND_ID:
                self.machine._queue_new_event(EventDefinition(heal=HealEventDefinition(location=self.machine._gamehook_client.get(gh_gen_two_const.KEY_OVERWORLD_MAP).value)))
            elif new_prop.value == gh_gen_two_const.SAVE_HEAL_SOUND_ID:
                self.machine._queue_new_event(EventDefinition(save=SaveEventDefinition(location=self.machine._gamehook_client.get(gh_gen_two_const.KEY_OVERWORLD_MAP).value)))
        elif new_prop.path == gh_gen_two_const.KEY_GAMETIME_SECONDS:
            if self._waiting_for_registration:
                if self._register_delay <= 0:
                    self._waiting_for_registration = False
                    self.machine.update_team_cache(regenerate_move_cache=True)
                self._register_delay -= 1


        return self.state_type
