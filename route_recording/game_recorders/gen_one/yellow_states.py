from __future__ import annotations
import logging

from route_recording.game_recorders.gen_one.yellow_fsm import Machine, State, StateType
from route_recording.gamehook_client import GameHookProperty
from routing.route_events import BlackoutEventDefinition, EventDefinition, HealEventDefinition, InventoryEventDefinition, SaveEventDefinition, TrainerEventDefinition, WildPkmnEventDefinition
from route_recording.game_recorders.gen_one.yellow_gamehook_constants import gh_gen_one_const
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
        
        self.machine.update_all_cached_info()
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._seconds_delay <= 0:
                cur_battle_mode = self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_TYPE)
                if cur_battle_mode == gh_gen_one_const.WILD_BATTLE_TYPE or cur_battle_mode == gh_gen_one_const.TRAINER_BATTLE_TYPE:
                    return StateType.BATTLE
                else:
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
        self.machine._queue_new_event(EventDefinition(notes=gh_gen_one_const.RESET_FLAG))
    
    def _on_exit(self, next_state: State):
        new_player_id = self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_PLAYERID).value
        if self.machine._player_id is None:
            self.machine._player_id = new_player_id
        elif self.machine._player_id != new_player_id:
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
        self._waiting_for_init = True
        self._init_delay = 0
        self._trainer_name = ""
        self._defeated_trainer_mons = []
        self._waiting_for_moves = False
        self._move_update_delay = 0
        self._waiting_for_items = False
        self._item_update_delay = 0
        self._loss_detected = False
        self._evolution_detected = False
        self._initial_money = 0
    
    def _on_enter(self, prev_state: State):
        self._waiting_for_init = True
        self._init_delay = 0
        self._defeated_trainer_mons = []
        self._waiting_for_moves = False
        self._move_update_delay = 0
        self._waiting_for_items = False
        self._item_update_delay = 0
        self._trainer_name = ""
        self.is_trainer_battle = False
        self._loss_detected = False
        self._evolution_detected = False
        self._initial_money = self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MONEY).value
    
    def _create_initial_trainer_event(self):
        if self.is_trainer_battle:
            self._trainer_name = self.machine.gh_converter.trainer_name_convert(
                self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_TRAINER_CLASS).value,
                self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_TRAINER_NUMBER).value,
                self.machine._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value,
            )
            self.machine._queue_new_event(
                EventDefinition(trainer_def=TrainerEventDefinition(self._trainer_name))
            )

    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            if self._loss_detected:
                self.machine._queue_new_event(
                    EventDefinition(trainer_def=TrainerEventDefinition(self._trainer_name), notes=gh_gen_one_const.TRAINER_LOSS_FLAG)
                )
                # super special case. If we lost to the rocket on nugget bridge
                # He gives you the nugget before the fight, so make sure that happens
                if self._trainer_name == gh_gen_one_const.NUGGET_ROCKET:
                    self.machine._queue_new_event(EventDefinition(item_event_def=InventoryEventDefinition(gh_gen_one_const.NUGGET, 1, True, False)))
                for trainer_mon_event in self._defeated_trainer_mons:
                    self.machine._queue_new_event(trainer_mon_event)
                # second super special case. If we lose to the rival lab fight, the blackout doesn't actually happen
                if self._trainer_name not in gh_gen_one_const.RIVAL_LAB_FIGHTS:
                    self.machine._queue_new_event(EventDefinition(blackout=BlackoutEventDefinition()))
            elif self._trainer_name:
                self.machine._queue_new_event(
                    EventDefinition(
                        trainer_def=TrainerEventDefinition(
                            self._trainer_name,
                            pay_day_amount=self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MONEY).value - self._initial_money
                        ),
                        notes=gh_gen_one_const.PAY_DAY_FLAG
                    )
                )
            if self._waiting_for_moves:
                if self._evolution_detected:
                    self.machine.update_team_cache()
                self.machine._move_cache_update(levelup_source=True)
            if self._waiting_for_items:
                self.machine._item_cache_update()

    @auto_reset
    def transition(self, new_prop: GameHookProperty, prev_prop: GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_PLAYER_MON_EXPPOINTS:
            if self.is_trainer_battle:
                self._defeated_trainer_mons.append(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                    self.machine.gh_converter.pkmn_name_convert(self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_ENEMY_SPECIES).value),
                    self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_ENEMY_LEVEL).value,
                    trainer_pkmn=True
                )))
            else:
                self.machine._queue_new_event(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                    self.machine.gh_converter.pkmn_name_convert(self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_ENEMY_SPECIES).value),
                    self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_ENEMY_LEVEL).value,
                )))
        elif new_prop.path == gh_gen_one_const.KEY_BATTLE_PLAYER_MON_HP:
            if new_prop.value <= 0:
                self._loss_detected = True
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_MON_SPECIES:
            self._evolution_detected = True
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
            if self._waiting_for_init:
                if self._init_delay <= 0:
                    self._waiting_for_init = False
                    self.is_trainer_battle = self.machine._gamehook_client.get(gh_gen_one_const.KEY_BATTLE_TYPE).value == gh_gen_one_const.TRAINER_BATTLE_TYPE
                    if self.is_trainer_battle:
                        self._create_initial_trainer_event()
                else:
                    self._init_delay -= 1
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
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_MON_LEVEL:
            self.machine._solo_mon_levelup(new_prop.value)
        elif new_prop.path == gh_gen_one_const.KEY_BATTLE_TYPE:
            if new_prop.value == gh_gen_one_const.NONE_BATTLE_TYPE:
                return StateType.OVERWORLD
        
        return self.state_type


class InventoryChangeState(WatchForResetState):
    BASE_DELAY = 2
    def __init__(self, machine: Machine):
        super().__init__(StateType.INVENTORY_CHANGE, machine)
        self._seconds_delay = self.BASE_DELAY
        self._money_gained = False
        self._money_lost = False
    
    def _on_enter(self, prev_state: State):
        self._seconds_delay = self.BASE_DELAY
        self._money_gained = True if self.machine._money_cache_update() else False
        self._money_lost = False
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(sale_expected=self._money_gained, purchase_expected=self._money_lost)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_PLAYER_MONEY:
            if new_prop.value > prev_prop.value:
                self._money_gained = True
            else:
                self._money_lost = True
        elif (
            new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT or
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY or
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE
        ):
            self._seconds_delay = self.BASE_DELAY
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            # stupid hack for vending machines (listening for the rumble)
            # vending machines are the only purchase in the game that deducts your money _after_ the item is added
            # and it does it after that very long sound effect too. wait for the sound effect to finish
            # NOTE: this doesn't work 100% of the time, so we have helper code in the cache update function too
            if self.machine._gamehook_client.get(gh_gen_one_const.KEY_AUDIO_CHANNEL_7).value != 168:
                if self._seconds_delay <= 0:
                    return StateType.OVERWORLD
                else:
                    self._seconds_delay -= 1

        return self.state_type


class UseRareCandyState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.RARE_CANDY, machine)
        self._move_learned = False
        self._item_removal_detected = False

    def _on_enter(self, prev_state: State):
        self._move_learned = False
        self._item_removal_detected = False
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(candy_flag=True)
            self.machine._solo_mon_levelup(self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_MON_LEVEL).value)
            self.machine.update_team_cache()
            if self._move_learned:
                self.machine._move_cache_update(levelup_source=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path in gh_gen_one_const.ALL_KEYS_PLAYER_MOVES:
            self._move_learned = True
        elif new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT:
            self._item_removal_detected = True
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY:
            if not self._item_removal_detected:
                return StateType.OVERWORLD
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE:
            if new_prop.value is None or new_prop.value == gh_gen_one_const.END_OF_ITEM_LIST:
                return StateType.OVERWORLD

        return self.state_type


class UseTMState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.TM, machine)
        self._item_removal_detected = False

    def _on_enter(self, prev_state: State):
        self._item_removal_detected = False
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(tm_flag=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT:
            self._item_removal_detected = True
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY:
            if not self._item_removal_detected:
                return StateType.OVERWORLD
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE:
            if new_prop.value is None or new_prop.value == gh_gen_one_const.END_OF_ITEM_LIST:
                return StateType.OVERWORLD

        return self.state_type


class UseVitaminState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.VITAMIN, machine)
        self._item_removal_detected = False

    def _on_enter(self, prev_state: State):
        self._item_removal_detected = False
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(vitamin_flag=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT:
            self._item_removal_detected = True
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY:
            if not self._item_removal_detected:
                return StateType.OVERWORLD
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE:
            if new_prop.value is None or new_prop.value == gh_gen_one_const.END_OF_ITEM_LIST:
                return StateType.OVERWORLD

        return self.state_type


class OverworldState(WatchForResetState):
    def __init__(self, machine: Machine):
        super().__init__(StateType.OVERWORLD, machine)
        self._waiting_for_registration = False
        self._register_delay = 2
    
    def _on_enter(self, prev_state: State):
        self.machine._money_cache_update()
        self.machine.update_team_cache()
        self._waiting_for_registration = False
        self._register_delay = 2
        self._waiting_for_new_file = False
        self._new_file_delay = 2
        self._waiting_for_heal_completion = False
        self._heal_delay = 2

        self._waiting_for_solo_mon_in_slot_1 = False
        self._wrong_mon_delay = 2
        self._wrong_mon_in_slot_1 = False
    
    def _on_exit(self, next_state: State):
        pass
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        # intentionally ignore all updates while waiting for a new file
        if self._waiting_for_new_file or self._waiting_for_solo_mon_in_slot_1:
            if new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
                if self._new_file_delay <= 0:
                    self._waiting_for_new_file = False
                    self.machine._controller.route_restarted()
                    self.machine.update_all_cached_info()
                self._new_file_delay -= 1
            
            return self.state_type

        if new_prop.path == gh_gen_one_const.KEY_BATTLE_TYPE:
            return StateType.BATTLE
        elif new_prop.path == gh_gen_one_const.KEY_OVERWORLD_MAP:
            self.machine._controller.entered_new_area(self.machine.gh_converter.area_name_convert(new_prop.value))
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_PLAYERID:
            if prev_prop.value and self.machine._player_id != self.machine._gamehook_client.get(gh_gen_one_const.KEY_PLAYER_PLAYERID).value:
                self._waiting_for_new_file = True
        elif (
            new_prop.path == gh_gen_one_const.KEY_ITEM_COUNT or
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_QUANTITY or
            new_prop.path in gh_gen_one_const.ALL_KEYS_ITEM_TYPE
        ):
            return StateType.INVENTORY_CHANGE
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_MONEY:
            cur_location = self.machine._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value
            if new_prop.value > prev_prop.value and cur_location != gh_gen_one_const.MAP_GAME_CORNER:
                # Kinda ugly, but intentionally configuring the cached money value to be correct for the sale check
                self.machine._cached_money = prev_prop.value
                return StateType.INVENTORY_CHANGE
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_MON_SPECIES:
            if not prev_prop.value:
                self._waiting_for_registration = True
            elif self.machine._solo_mon_key.species == self.machine.gh_converter.pkmn_name_convert(prev_prop.value):
                self._wrong_mon_in_slot_1 = True
            elif self.machine._solo_mon_key.species == self.machine.gh_converter.pkmn_name_convert(new_prop.value):
                self._wrong_mon_delay = 2
                self._waiting_for_solo_mon_in_slot_1 = True
        elif new_prop.path == gh_gen_one_const.KEY_PLAYER_MON_LEVEL:
            if not self._waiting_for_registration and not self._wrong_mon_in_slot_1:
                return StateType.RARE_CANDY
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_PLAYER_MOVES:
            # This can occur if the player (for some reason, likely on accident) re-orders their party
            # let's try to prevent that from being an issue
            if not self._waiting_for_registration and not self._wrong_mon_in_slot_1:
                if self.machine.gh_converter.get_hm_name(new_prop.value) is not None:
                    self.machine._move_cache_update(hm_expected=True)
                else:
                    return StateType.TM
        elif new_prop.path in gh_gen_one_const.ALL_KEYS_STAT_EXP:
            if not self._waiting_for_registration and not self._wrong_mon_in_slot_1:
                return StateType.VITAMIN
        elif new_prop.path == gh_gen_one_const.KEY_AUDIO_CHANNEL_5:
            if new_prop.value == 158 and not self._waiting_for_heal_completion:
                self.machine._queue_new_event(EventDefinition(heal=HealEventDefinition(location=self.machine._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value)))
                self._waiting_for_heal_completion = True
                self._heal_delay = 2
            elif new_prop.value == 182:
                self.machine._queue_new_event(EventDefinition(save=SaveEventDefinition(location=self.machine._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value)))
        elif new_prop.path == gh_gen_one_const.KEY_AUDIO_CHANNEL_4:
            # channel 4 for R/B pokecenters, channel 5 for Y
            if new_prop.value == 158 and not self._waiting_for_heal_completion:
                self.machine._queue_new_event(EventDefinition(heal=HealEventDefinition(location=self.machine._gamehook_client.get(gh_gen_one_const.KEY_OVERWORLD_MAP).value)))
                self._waiting_for_heal_completion = True
                self._heal_delay = 2
        elif new_prop.path == gh_gen_one_const.KEY_GAMETIME_SECONDS:
            if self._waiting_for_registration:
                if self._register_delay <= 0:
                    self._waiting_for_registration = False
                    self.machine.update_team_cache(regenerate_move_cache=True)
                self._register_delay -= 1
            if self._waiting_for_heal_completion:
                if self._heal_delay <= 0:
                    self._waiting_for_heal_completion = False
                self._heal_delay -= 1
            if self._waiting_for_solo_mon_in_slot_1:
                if self._wrong_mon_delay <= 0:
                    self._waiting_for_solo_mon_in_slot_1 = False
                    self._wrong_mon_in_slot_1 = False
                self._wrong_mon_delay -= 1


        return self.state_type
