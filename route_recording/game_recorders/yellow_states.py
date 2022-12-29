from __future__ import annotations
import logging

from route_recording.game_recorders.yellow_fsm import Machine, State, StateType
from route_recording.gamehook_client import GameHookProperty
from routing.route_events import BlackoutEventDefinition, EventDefinition, HealEventDefinition, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, SaveEventDefinition, TrainerEventDefinition, VitaminEventDefinition, WildPkmnEventDefinition
from route_recording.game_recorders.yellow_gamehook_constants import gh_gen_one_const, gh_converter
from utils.constants import const

logger = logging.getLogger(__name__)


class WatchForResetState(State):
    def watch_for_reset(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if self.machine._player_id is not None and new_prop.path == gh_gen_one_const.KEY_PLAYER_PLAYERID and new_prop.value == 0:
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


class UninitializedState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.UNINITIALIZED, machine)
        self._is_waiting = False
        self._seconds_delay = 2
    
    def _on_enter(self, prev_state: State):
        self._is_waiting = False
        self._seconds_delay = 2
    
    def _on_exit(self, next_state: State):
        self.machine._player_id = self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_PLAYERID).value
        # Shouldn't really happen ever, but if the player connects to an active game, but then resets the emulator
        # it's possible that we exit (due to transitioning to a reset state) while the player id is 0
        # If this happens, just ignore the update, let the ResettingState handle setting the player id
        if self.machine._player_id == 0:
            self.machine._player_id = None
        
        self.machine.update_all_cached_info(include_solo_mon=True)
        logger.info(f"Registering player id for current recorded run: {self.machine._player_id}")
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._seconds_delay <= 0:
                return StateType.OVERWORLD
            elif not self._is_waiting and self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_PLAYERID).value != 0:
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
        # TODO: ugly, but wtv. Revisit later maybe. Send an object that's basically just a flag to reset
        self.machine._queue_new_event(EventDefinition(notes=gh_gen_one_const.RESET_FLAG))
    
    def _on_exit(self, next_state: State):
        new_player_id = self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_PLAYERID).value
        if self.machine._player_id is None:
            self.machine._player_id = new_player_id
        elif self.machine._player_id != new_player_id:
            self.machine._solo_mon_species = None
            self.machine._controller.route_restarted()

        self.machine.update_all_cached_info()

    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_PLAYER_PLAYERID:
            if prev_prop.value == 0 and new_prop.value != 0:
                self._is_waiting = True
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
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
        self._defeated_trainer_mons = []
        self._waiting_for_moves = False
        self._move_update_delay = 0
        self._waiting_for_items = False
        self._item_update_delay = 0
        self._loss_detected = False
    
    def _on_enter(self, prev_state: State):
        self._defeated_trainer_mons = []
        self._waiting_for_moves = False
        self._move_update_delay = 0
        self._waiting_for_items = False
        self._item_update_delay = 0
        self.is_trainer_battle = self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_TYPE).value == gh_gen_one_const.TRAINER_BATTLE_TYPE
        self._loss_detected = False

        if self.is_trainer_battle:
            self._trainer_name = gh_converter.trainer_name_convert(
                self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_TRAINER_CLASS).value,
                self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_TRAINER_NUMBER).value,
                self.machine._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value,
            )
            self.machine._queue_new_event(
                EventDefinition(trainer_def=TrainerEventDefinition(self._trainer_name))
            )
        else:
            self._trainer_name = ""
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            if self._loss_detected:
                self.machine._queue_new_event(
                    EventDefinition(trainer_def=TrainerEventDefinition(self._trainer_name), notes=gh_gen_one_const.TRAINER_LOSS_FLAG)
                )
                for trainer_mon_event in self._defeated_trainer_mons:
                    self.machine._queue_new_event(trainer_mon_event)
                self.machine._queue_new_event(EventDefinition(blackout=BlackoutEventDefinition()))
            if self._waiting_for_items:
                self.machine._item_cache_update()

    @auto_reset
    def transition(self, new_prop: GameHookProperty, prev_prop: GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_PLAYER_MON_EXPPOINTS:
            if self.is_trainer_battle:
                self._defeated_trainer_mons.append(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                    self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_ENEMY_SPECIES).value,
                    self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_ENEMY_LEVEL).value,
                    trainer_pkmn=True
                )))
            else:
                self.machine._queue_new_event(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                    self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_ENEMY_SPECIES).value,
                    self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_ENEMY_LEVEL).value,
                )))
        elif new_prop.path == gh_gen_one_const.KEY_BATTLE_PLAYER_MON_HP:
            if new_prop.value <= 0:
                self._loss_detected = True
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_PLAYER_MOVES:
            if not self._waiting_for_moves:
                self._move_update_delay = 2
                self._waiting_for_moves = True
        elif (
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY or
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE or
            new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT
        ):
            if not self._waiting_for_items:
                self._item_update_delay = 2
                self._waiting_for_items = True
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._waiting_for_moves:
                if self._move_update_delay <= 0:
                    self._waiting_for_moves = False
                    self.machine._move_cache_update(levelup_source=True)
                else:
                    self._move_update_delay -= 1
            if self._waiting_for_items:
                if self._item_update_delay <= 0:
                    self._waiting_for_items = False
                    self.machine._item_cache_update()
                else:
                    self._item_update_delay -= 1
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_MON_LEVEL:
            self.machine._solo_mon_levelup(new_prop.value)
        elif new_prop.path == gh_gen_one_const.KEY_BATTLE_TYPE:
            if new_prop.value == gh_gen_one_const.NONE_BATTLE_TYPE:
                return StateType.OVERWORLD
        
        return self.state_type


class ItemGainState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.GAIN_ITEM, machine)
        self._seconds_delay = None
        self._money_lost = False
    
    def _on_enter(self, prev_state: State):
        self._seconds_delay = 2
        self._money_lost = False
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(purchase_expected=self._money_lost)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_PLAYER_MONEY:
            if new_prop.value < prev_prop.value:
                self._money_lost = True
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._seconds_delay <= 0:
                return StateType.OVERWORLD
            else:
                self._seconds_delay -= 1

        return self.state_type


class ItemLoseState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.LOSE_ITEM, machine)
        self._seconds_delay = None
        self._money_gained = False
    
    def _on_enter(self, prev_state: State):
        self._seconds_delay = 2
        self._money_gained = True if self.machine._money_cache_update() else False
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(sale_expected=self._money_gained)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_PLAYER_MONEY:
            if new_prop.value > prev_prop.value:
                self._money_gained = True
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._seconds_delay <= 0:
                return StateType.OVERWORLD
            else:
                self._seconds_delay -= 1

        return self.state_type


class UseRareCandyState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.RARE_CANDY, machine)
        self._move_learned = False
        self._waiting_flag = False
        self._delay = 2

    def _on_enter(self, prev_state: State):
        self._move_learned = True
        self._waiting_flag = False
        self._delay = 2
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(candy_flag=True)
            self.machine._solo_mon_levelup(self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_LEVEL).value)
            if self._move_learned:
                self.machine._move_cache_update(levelup_source=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path in gh_gen_one_const.ALL_KEYS_PLAYER_MOVES:
            self._move_learned = True
        elif (
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY or
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE or
            new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT
        ):
            self._waiting_flag = True
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._waiting_flag:
                if self._delay <= 0:
                    return StateType.OVERWORLD
                self._delay -= 1

        return self.state_type


class UseTMState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.TM, machine)
        self._waiting_flag = False
        self._delay = 2

    def _on_enter(self, prev_state: State):
        self._waiting_flag = False
        self._delay = 2
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(tm_flag=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if (
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY or
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE or
            new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT
        ):
            self._waiting_flag = True
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._waiting_flag:
                if self._delay <= 0:
                    return StateType.OVERWORLD
                self._delay -= 1

        return self.state_type


class UseVitaminState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.VITAMIN, machine)
        self._waiting_flag = False
        self._delay = 2

    def _on_enter(self, prev_state: State):
        self._waiting_flag = False
        self._delay = 2
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(vitamin_flag=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if (
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY or
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE or
            new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT
        ):
            self._waiting_flag = True
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._waiting_flag:
                if self._delay <= 0:
                    return StateType.OVERWORLD
                self._delay -= 1

        return self.state_type


class OverworldState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.OVERWORLD, machine)
        self._waiting_for_registration = False
        self._register_delay = 2
    
    def _on_enter(self, prev_state: State):
        self.machine._money_cache_update()
        self._waiting_for_registration = False
        self._register_delay = 2
        self._waiting_for_new_file = False
        self._new_file_delay = 2
    
    def _on_exit(self, next_state: State):
        pass
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        # intentionally ignore all updates while waiting for a new file
        if self._waiting_for_new_file:
            if new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
                if self._new_file_delay <= 0:
                    self._waiting_for_new_file = False
                    self.machine._controller.route_restarted()
                    self.machine.update_all_cached_info(include_solo_mon=True)
                self._new_file_delay -= 1
            
            return self.state_type

        if new_prop.path == gh_gen_one_const.KEY_BATTLE_TYPE:
            return StateType.BATTLE
        elif new_prop.path == gh_gen_one_const.KEY_OVERWORLD_MAP:
            self.machine._controller.entered_new_area(gh_converter.area_name_convert(new_prop.value))
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_PLAYERID:
            if prev_prop.value and self.machine._player_id != self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_PLAYERID).value:
                self._waiting_for_new_file = True
        elif new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT:
            if new_prop.value > prev_prop.value:
                return StateType.GAIN_ITEM
            else:
                return StateType.LOSE_ITEM
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY:
            if new_prop.value > prev_prop.value:
                return StateType.GAIN_ITEM
            else:
                return StateType.LOSE_ITEM
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE:
            # Kinda weird, but if type changes (AND count did not change first) this actually suggests someone messing around via gamehook
            # as a result, we still want to try and handle it. Sending this case to lose_item *should* still accurately cover most cases
            return StateType.LOSE_ITEM
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_MONEY:
            cur_location = self.machine._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value
            if new_prop.value > prev_prop.value and cur_location != gh_gen_one_const.MAP_GAME_CORNER:
                # Kinda ugly, but intentionally configuring the cached money value to be correct for the sale check
                self.machine._cached_money = prev_prop.value
                return StateType.LOSE_ITEM
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_MON_SPECIES:
            if not prev_prop.value:
                self._waiting_for_registration = True
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_MON_LEVEL:
            if (
                not self._waiting_for_registration and 
                self.machine._solo_mon_species == gh_converter.pkmn_name_convert(self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_SPECIES).value)
            ):
                return StateType.RARE_CANDY
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_PLAYER_MOVES:
            # This can occur if the player (for some reason, likely on accident) re-orders their party
            # let's try to prevent that from being an issue
            if (
                not self._waiting_for_registration and 
                self.machine._solo_mon_species == gh_converter.pkmn_name_convert(self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_SPECIES).value)
            ):
                if gh_converter.get_hm_name(new_prop.value) is not None:
                    self.machine._move_cache_update(hm_expected=True)
                else:
                    return StateType.TM
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_STAT_EXP:
            if (
                not self._waiting_for_registration and 
                self.machine._solo_mon_species == gh_converter.pkmn_name_convert(self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_SPECIES).value)
            ):
                return StateType.VITAMIN
        elif new_prop.path == gh_gen_one_const.KEY_AUDIO_CHANNEL_5:
            if new_prop.value == 158:
                self.machine._queue_new_event(EventDefinition(heal=HealEventDefinition(location=self.machine._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value)))
            elif new_prop.value == 182:
                self.machine._queue_new_event(EventDefinition(save=SaveEventDefinition(location=self.machine._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value)))
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._waiting_for_registration:
                if self._register_delay <= 0:
                    self._waiting_for_registration = False
                    self.machine.register_solo_mon(self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_SPECIES).value)
                self._register_delay -= 1


        return self.state_type
