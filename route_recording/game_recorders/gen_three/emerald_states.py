from __future__ import annotations
import logging

from route_recording.game_recorders.gen_three.emerald_fsm import Machine, State, StateType
from route_recording.gamehook_client import GameHookProperty
from routing.route_events import BlackoutEventDefinition, EventDefinition, HealEventDefinition, HoldItemEventDefinition, LearnMoveEventDefinition, SaveEventDefinition, TrainerEventDefinition, WildPkmnEventDefinition
from route_recording.game_recorders.gen_three.emerald_gamehook_constants import gh_gen_three_const
from pkmn.gen_3.gen_three_constants import gen_three_const
from utils.constants import const

logger = logging.getLogger(__name__)


class WatchForResetState(State):
    def watch_for_reset(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path != gh_gen_three_const.KEY_GAMETIME_SECONDS and 'audio' not in new_prop.path:
            frame_val = self.machine._gamehook_client.get(gh_gen_three_const.KEY_GAMETIME_FRAMES).value
            logger.info(f"On Frame {frame_val:02} Changing {new_prop.path} from {prev_prop.value} to {new_prop.value}({type(new_prop.value)})")

        if self.machine._player_id is not None and new_prop.path == gh_gen_three_const.KEY_PLAYER_PLAYERID and new_prop.value == 0:
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
        if new_prop.path != gh_gen_three_const.KEY_GAMETIME_SECONDS:
            frame_val = self.machine._gamehook_client.get(gh_gen_three_const.KEY_GAMETIME_FRAMES).value
            logger.info(f"On Frame {frame_val:02} Changing {new_prop.path} from {prev_prop.value} to {new_prop.value}({type(new_prop.value)})")

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
        self.machine._player_id = self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_PLAYERID).value
        # Shouldn't really happen ever, but if the player connects to an active game, but then resets the emulator
        # it's possible that we exit (due to transitioning to a reset state) while the player id is 0
        # If this happens, just ignore the update, let the ResettingState handle setting the player id
        if self.machine._player_id == 0:
            self.machine._player_id = None
        
        self.machine.update_all_cached_info(include_solo_mon=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_three_const.KEY_GAMETIME_SECONDS:
            if self._seconds_delay <= 0:
                if (
                    self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_OUTCOME).value is None and
                    self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FLAG).value
                ):
                    return StateType.BATTLE
                else:
                    return StateType.OVERWORLD
            elif not self._is_waiting and self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_PLAYERID).value != 0:
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
        self.machine._queue_new_event(EventDefinition(notes=gh_gen_three_const.RESET_FLAG))
    
    def _on_exit(self, next_state: State):
        new_player_id = self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_PLAYERID).value
        if self.machine._player_id is None:
            self.machine._player_id = new_player_id
        elif self.machine._player_id != new_player_id:
            self.machine._solo_mon_species = None
            self.machine._controller.route_restarted()

        self.machine.update_all_cached_info()

    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_three_const.KEY_PLAYER_PLAYERID:
            if prev_prop.value == 0 and new_prop.value != 0:
                self._is_waiting = True
        elif new_prop.path == gh_gen_three_const.KEY_GAMETIME_SECONDS:
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
        self._second_trainer_name = ""
        self._enemy_pos_lookup = {}
        self._trainer_event_created = False
        self._defeated_trainer_mons = []
        self._waiting_for_moves = False
        self._move_update_delay = 0
        self._waiting_for_items = False
        self._item_update_delay = 0
        self._loss_detected = False
        self._held_item_consumed = False
        self._cached_first_mon_species = ""
        self._cached_first_mon_level = 0
        self._cached_second_mon_species = ""
        self._cached_second_mon_level = 0
        self._exp_split = []
        self._enemy_mon_order = []
        self._friendship_data = []
        self._battle_started = False
        self._battle_finished = False
        self._is_double_battle = False
        self._initial_money = 0
    
    def _on_enter(self, prev_state: State):
        self._defeated_trainer_mons = []
        self._waiting_for_moves = False
        self._move_update_delay = 0
        self._waiting_for_items = False
        self._item_update_delay = 0
        self.is_trainer_battle = False
        self._trainer_event_created = False
        self._loss_detected = False
        self._held_item_consumed = False
        self._cached_first_mon_species = ""
        self._cached_first_mon_level = 0
        self._cached_second_mon_species = ""
        self._cached_second_mon_level = 0
        self._trainer_name = ""
        self._second_trainer_name = ""
        self._enemy_pos_lookup = {}
        self._exp_split = []
        self._enemy_mon_order = []
        self._friendship_data = []
        self._battle_started = False
        self._battle_finished = False
        self._is_double_battle = False
        self._initial_money = self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_MONEY).value

        if self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FLAG).value:
            self._battle_ready()
        
    
    def _get_num_enemy_trainer_pokemon(self):
        # Ideally, this should be pulled from a single property. However that mapped property doesn't work currently
        # so, for now, just iterate over enemy pokemon team species, and figure out how many non-empty team members are loaded
        result = 0
        for cur_key in gh_gen_three_const.ALL_KEYS_ENEMY_TEAM_SPECIES:
            if self.machine._gamehook_client.get(cur_key).value:
                result += 1
        return result

    def _get_enemy_pos_lookup(self):
        # because we have a weird default mon order for multi battles, need to create this to make sure we handle things appropriately
        if not self._second_trainer_name:
            # single trainer battles (single or double) are trivial. just create all 6 lookups
            return {x: x for x in range(6)}
        
        # just statically define the "real" order. Alternating between 2 trainers, taking their mons in order
        # however, there's no guarantee we need all of them, so calculate the ones we actually need
        real_order = [0, 3, 1, 4, 2, 5]
        result = {}
        next_pos_idx = 0
        for cur_key_idx in real_order:
            if self.machine._gamehook_client.get(gh_gen_three_const.ALL_KEYS_ENEMY_TEAM_SPECIES[cur_key_idx]).value:
                result[cur_key_idx] = next_pos_idx
                next_pos_idx += 1

        logger.info(f"completed pos lookup for trainer: {result}")
        return result

    def _battle_ready(self):
        # to be called after battle is actually initialized
        self._battle_started = True
        self._is_double_battle = self.machine._gamehook_client.get(gh_gen_three_const.KEY_DOUBLE_BATTLE_FLAG).value
        self.is_trainer_battle = self.machine._gamehook_client.get(gh_gen_three_const.KEY_TRAINER_BATTLE_FLAG).value

        if self.is_trainer_battle:
            self._trainer_name = self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_TRAINER_A_NUMBER).value
            self._second_trainer_name = self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_TRAINER_B_NUMBER).value
            if self._second_trainer_name is None or not self._is_double_battle:
                self._second_trainer_name = ""

            num_enemy_pokemon = self._get_num_enemy_trainer_pokemon()
            self._enemy_pos_lookup = self._get_enemy_pos_lookup()
            if self._is_double_battle:
                ally_mon_pos = self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_ALLY_MON_PARTY_POS).value
                self._exp_split = [set([0, ally_mon_pos]) for _ in range(num_enemy_pokemon)]
                self._enemy_mon_order = [0, 1]
            else:
                self._exp_split = [set([0]) for _ in range(num_enemy_pokemon)]
                self._enemy_mon_order = [0]

            return_custom_move_data = None
            if gen_three_const.RETURN_MOVE_NAME in self.machine._cached_moves:
                return_custom_move_data = []
                cur_friendship = self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_MON_FRIENDSHIP).value
                for _ in range(6):
                    return_custom_move_data.append({
                        const.PLAYER_KEY: {gen_three_const.RETURN_MOVE_NAME: str(int(cur_friendship / 2.5))},
                        const.ENEMY_KEY: {}
                    })

            self.machine._queue_new_event(
                EventDefinition(
                    trainer_def=TrainerEventDefinition(
                        self._trainer_name,
                        second_trainer_name=self._second_trainer_name,
                        custom_move_data=return_custom_move_data,
                        exp_split=[len(x) for x in self._exp_split]
                    )
                )
            )
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            if self.is_trainer_battle:
                logger.info(f"final exp split (before simplification): {self._exp_split}")
                final_exp_split = [len(x) for x in self._exp_split]
                if not any([True for x in final_exp_split if x > 1]):
                    final_exp_split = None
                
                final_mon_order = [self._enemy_mon_order.index(x) + 1 for x in sorted(self._enemy_mon_order)]
                logger.info(f"final mon order: {final_mon_order}")

                return_custom_move_data = None
                if gen_three_const.RETURN_MOVE_NAME in self.machine._cached_moves:
                    return_custom_move_data = []
                    for cur_friendship in self._friendship_data:
                        return_custom_move_data.append({
                            const.PLAYER_KEY: {gen_three_const.RETURN_MOVE_NAME: str(int(cur_friendship / 2.5))},
                            const.ENEMY_KEY: {}
                        })

                self.machine._queue_new_event(
                    EventDefinition(
                        trainer_def=TrainerEventDefinition(
                            self._trainer_name,
                            second_trainer_name=self._second_trainer_name,
                            exp_split=final_exp_split,
                            mon_order=final_mon_order,
                            custom_move_data=return_custom_move_data,
                            pay_day_amount=self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_MONEY).value - self._initial_money,
                        ),
                        notes=gh_gen_three_const.ROAR_FLAG
                    )
                )
            if self._loss_detected:
                if self.is_trainer_battle:
                    self.machine._queue_new_event(
                        EventDefinition(trainer_def=TrainerEventDefinition(self._trainer_name), notes=gh_gen_three_const.TRAINER_LOSS_FLAG)
                    )
                    for trainer_mon_event in self._defeated_trainer_mons:
                        self.machine._queue_new_event(trainer_mon_event)
                self.machine._queue_new_event(EventDefinition(blackout=BlackoutEventDefinition()))
            elif self.is_trainer_battle:
                # TODO: is this relevant for emerald? if we won a trainer battle, check for special case of beating the champion
                if False:
                    self.machine._queue_new_event(EventDefinition(save=SaveEventDefinition(location="Post-Champion Autosave")))
            if self._waiting_for_moves:
                self.machine._move_cache_update(levelup_source=True)
            if self._waiting_for_items:
                self.machine._item_cache_update()
            if self._held_item_consumed:
                self.machine._queue_new_event(EventDefinition(hold_item=HoldItemEventDefinition(None, True)))
    
    def _get_first_enemy_mon_pos(self, value=None):
        if value is None:
            value = self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FIRST_ENEMY_PARTY_POS).value
        return self._enemy_pos_lookup[value]

    def _get_second_enemy_mon_pos(self, value=None):
        if value is None:
            value = self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_SECOND_ENEMY_PARTY_POS).value
        return self._enemy_pos_lookup[value]

    @auto_reset
    def transition(self, new_prop: GameHookProperty, prev_prop: GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_three_const.KEY_PLAYER_MON_EXPPOINTS:
            if self._cached_first_mon_species or self._cached_first_mon_level:
                if self.is_trainer_battle:
                    self._defeated_trainer_mons.append(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                        self._cached_first_mon_species,
                        self._cached_first_mon_level,
                        trainer_pkmn=True
                    )))
                else:
                    self.machine._queue_new_event(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                        self._cached_first_mon_species,
                        self._cached_first_mon_level,
                    )))
                self._cached_first_mon_species = ""
                self._cached_first_mon_level = 0
            elif self._cached_second_mon_species or self._cached_second_mon_level:
                if self.is_trainer_battle:
                    self._defeated_trainer_mons.append(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                        self._cached_second_mon_species,
                        self._cached_second_mon_level,
                        trainer_pkmn=True
                    )))
                else:
                    self.machine._queue_new_event(EventDefinition(wild_pkmn_info=WildPkmnEventDefinition(
                        self._cached_second_mon_species,
                        self._cached_second_mon_level,
                    )))
                self._cached_second_mon_species = ""
                self._cached_second_mon_level = 0
            else:
                logger.error(f"Solo mon gained experience, but we didn't properly cache which enemy mon was defeated...")

        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_FLAG:
            if new_prop.value and not self._battle_started:
                self._battle_ready()
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_FIRST_ENEMY_HP:
            if new_prop.value == 0:
                self._cached_first_mon_species = self.machine.gh_converter.pkmn_name_convert(self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FIRST_ENEMY_SPECIES).value)
                self._cached_first_mon_level = self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FIRST_ENEMY_LEVEL).value
                self._friendship_data.append(self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_MON_FRIENDSHIP).value)
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_SECOND_ENEMY_HP:
            if new_prop.value == 0:
                self._cached_second_mon_species = self.machine.gh_converter.pkmn_name_convert(self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_SECOND_ENEMY_SPECIES).value)
                self._cached_second_mon_level = self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_SECOND_ENEMY_LEVEL).value
                self._friendship_data.append(self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_MON_FRIENDSHIP).value)
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_PLAYER_MON_HP:
            player_mon_pos = self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_PLAYER_MON_PARTY_POS).value
            if player_mon_pos == 0 and new_prop.value <= 0:
                if self._battle_started:
                    self._loss_detected = True
            elif new_prop.value <= 0:
                enemy_mon_pos = self._get_first_enemy_mon_pos()
                if player_mon_pos in self._exp_split[enemy_mon_pos]:
                    self._exp_split[enemy_mon_pos].remove(player_mon_pos)
                if self._is_double_battle:
                    second_enemy_mon_pos = self._get_second_enemy_mon_pos()
                    if player_mon_pos in self._exp_split[second_enemy_mon_pos]:
                        self._exp_split[second_enemy_mon_pos].remove(player_mon_pos)
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_ALLY_MON_HP:
            if self._is_double_battle and new_prop.value <= 0:
                # for each of these we want to remove the ally from exp split if the enemy mon is still alive
                # additionally, we also want to remove from the exp split if the enemy is cached, as this means they died on the same turn (e.g. earthquake)
                # if the enemy has no HP *AND* is not cached for exp distribution, then they have died and enemy trainer has no further mons
                #   In that case, leave the ally in the exp split, as they did participate already
                ally_mon_pos = self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_ALLY_MON_PARTY_POS).value
                enemy_mon_pos = self._get_first_enemy_mon_pos()
                if (
                    ally_mon_pos in self._exp_split[enemy_mon_pos] and (
                        self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FIRST_ENEMY_HP).value > 0 or
                        self._cached_first_mon_species
                    )
                ):
                    self._exp_split[enemy_mon_pos].remove(ally_mon_pos)

                # do the same checks for second enemy mon
                second_enemy_mon_pos = self._get_second_enemy_mon_pos()
                if (
                    ally_mon_pos in self._exp_split[second_enemy_mon_pos] and (
                        self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_SECOND_ENEMY_HP).value > 0 or
                        self._cached_second_mon_species
                    )
                ):
                    self._exp_split[second_enemy_mon_pos].remove(ally_mon_pos)

        elif new_prop.path in gh_gen_three_const.ALL_KEYS_PLAYER_MOVES:
            if not self._waiting_for_moves:
                self._move_update_delay = 2
                self._waiting_for_moves = True
        elif new_prop.path in gh_gen_three_const.ALL_KEYS_ALL_ITEM_FIELDS:
            if not self._waiting_for_items:
                self._item_update_delay = 2
                self._waiting_for_items = True
        elif new_prop.path == gh_gen_three_const.KEY_GAMETIME_SECONDS:
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
        elif new_prop.path == gh_gen_three_const.KEY_PLAYER_MON_LEVEL:
            self.machine._solo_mon_levelup(new_prop.value)
        elif new_prop.path == gh_gen_three_const.KEY_PLAYER_MON_HELD_ITEM:
            self._held_item_consumed = True
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_PLAYER_MON_PARTY_POS:
            if new_prop.value >= 0 and new_prop.value < 6:
                if self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FIRST_ENEMY_HP).value > 0:
                    self._exp_split[self._get_first_enemy_mon_pos()].add(new_prop.value)
                if self._is_double_battle:
                    if self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_SECOND_ENEMY_HP).value > 0:
                        self._exp_split[self._get_second_enemy_mon_pos()].add(new_prop.value)
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_ALLY_MON_PARTY_POS:
            if self._is_double_battle and new_prop.value >= 0 and new_prop.value < 6:
                if self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FIRST_ENEMY_HP).value > 0:
                    self._exp_split[self._get_first_enemy_mon_pos()].add(new_prop.value)
                if self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_SECOND_ENEMY_HP).value > 0:
                    self._exp_split[self._get_second_enemy_mon_pos()].add(new_prop.value)
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_FIRST_ENEMY_PARTY_POS:
            real_new_value = self._get_first_enemy_mon_pos(value=new_prop.value)
            if real_new_value >= 0 and real_new_value < len(self._exp_split):
                if self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_PLAYER_MON_HP).value > 0:
                    self._exp_split[real_new_value] = set([self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_PLAYER_MON_PARTY_POS).value])
                if self._is_double_battle and self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_ALLY_MON_HP).value > 0:
                    self._exp_split[real_new_value].add(self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_ALLY_MON_PARTY_POS).value)

                # NOTE: this logic won't perfectly reflect things if the player uses roar/whirlwind
                # or if the enemy trainer switches pokemon (and doesn't only send out new mons on previous death)
                if real_new_value not in self._enemy_mon_order:
                    self._enemy_mon_order.append(real_new_value)
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_SECOND_ENEMY_PARTY_POS:
            real_new_value = self._get_second_enemy_mon_pos(value=new_prop.value)
            if self._is_double_battle and real_new_value >= 0 and real_new_value < len(self._exp_split):
                if self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_PLAYER_MON_HP).value > 0:
                    self._exp_split[real_new_value] = set([self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_PLAYER_MON_PARTY_POS).value])
                if self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_ALLY_MON_HP).value > 0:
                    self._exp_split[real_new_value].add(self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_ALLY_MON_PARTY_POS).value)

                # NOTE: this logic won't perfectly reflect things if the player uses roar/whirlwind
                # or if the enemy trainer switches pokemon (and doesn't only send out new mons on previous death)
                if real_new_value not in self._enemy_mon_order:
                    self._enemy_mon_order.append(real_new_value)
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_OUTCOME:
            # Kind of stupid, but the money update happens in between the outcome being set and the reload of the overworld
            # so the easiest thing to do for cleanly exiting the battle state is to flag when the outcome is set
            # that signifies that the battle is over. Once we know the battle is over, the next dma pointer update
            # should be caused by the game reloading the overworld. Transition when that occurs
            if new_prop.value is not None:
                self._battle_finished = True
        elif new_prop.path == gh_gen_three_const.KEY_DMA_A or new_prop.path == gh_gen_three_const.KEY_PLAYER_MONEY:
            if self._battle_finished:
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
        self.external_held_item_flag = False
    
    def _on_enter(self, prev_state: State):
        self._seconds_delay = self.BASE_DELAY
        self._money_gained = True if self.machine._money_cache_update() else False
        self._money_lost = False

        # Set it to True if we are getting flagged for it externally. Otherwise set it to False
        self._held_item_changed = self.external_held_item_flag
        self.external_held_item_flag = False
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            logger.info(f"after inventory change, held_item_changed? {self._held_item_changed}")
            self.machine._item_cache_update(
                sale_expected=self._money_gained,
                purchase_expected=self._money_lost,
                held_item_changed=self._held_item_changed
            )
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path == gh_gen_three_const.KEY_PLAYER_MONEY:
            if new_prop.value > prev_prop.value:
                self._money_gained = True
            else:
                self._money_lost = True
        elif new_prop.path in gh_gen_three_const.ALL_KEYS_ALL_ITEM_FIELDS:
            self._seconds_delay = self.BASE_DELAY
        elif new_prop.path == gh_gen_three_const.KEY_PLAYER_MON_HELD_ITEM:
            self._held_item_changed = True
        elif new_prop.path == gh_gen_three_const.KEY_GAMETIME_SECONDS:
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
            self.machine._solo_mon_levelup(self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_MON_LEVEL).value)
            if self._move_learned:
                self.machine._move_cache_update(levelup_source=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path in gh_gen_three_const.ALL_KEYS_PLAYER_MOVES:
            self._move_learned = True
        elif new_prop.path in gh_gen_three_const.ALL_KEYS_ITEM_QUANTITY:
            if not self._item_removal_detected:
                return StateType.OVERWORLD
        elif new_prop.path in gh_gen_three_const.ALL_KEYS_ITEM_TYPE:
            self._item_removal_detected = True
            if new_prop.value is None:
                return StateType.OVERWORLD
        elif new_prop.path in gh_gen_three_const.KEY_GAMETIME_SECONDS:
            if self._item_removal_detected:
                if self._cur_delay <= 0:
                    return StateType.OVERWORLD
                else:
                    self._cur_delay -= 1

        return self.state_type


class UseTMState(WatchForResetState):
    BASE_DELAY = 2
    def __init__(self, machine: Machine):
        super().__init__(StateType.TM, machine)

    def _on_enter(self, prev_state: State):
        pass
    
    def _on_exit(self, next_state: State):
        if next_state.state_type != StateType.RESETTING:
            self.machine._item_cache_update(tm_flag=True)
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        if new_prop.path in gh_gen_three_const.ALL_KEYS_ALL_ITEM_FIELDS:
            self._seconds_delay = self.BASE_DELAY
        elif new_prop.path == gh_gen_three_const.KEY_PLAYER_MON_HELD_ITEM:
            self._held_item_changed = True
        elif new_prop.path == gh_gen_three_const.KEY_GAMETIME_SECONDS:
            if self._seconds_delay <= 0:
                return StateType.OVERWORLD
            else:
                self._seconds_delay -= 1

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
        if new_prop.path == gh_gen_three_const.KEY_GAMETIME_SECONDS:
            if self._cur_delay <= 0:
                return StateType.OVERWORLD
            else:
                self._cur_delay -= 1
        elif new_prop.path in gh_gen_three_const.ALL_KEYS_PLAYER_MOVES:
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
        if new_prop.path in gh_gen_three_const.ALL_KEYS_ITEM_QUANTITY:
            if not self._item_removal_detected:
                return StateType.OVERWORLD
        elif new_prop.path in gh_gen_three_const.ALL_KEYS_ITEM_TYPE:
            self._item_removal_detected = True
            if new_prop.value is None:
                return StateType.OVERWORLD
        elif new_prop.path == gh_gen_three_const.KEY_GAMETIME_SECONDS:
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
        self._propagate_held_item_flag = False
    
    def _on_enter(self, prev_state: State):
        self.machine._money_cache_update()
        self._waiting_for_registration = False
        self._register_delay = self.BASE_DELAY
        self._waiting_for_new_file = False
        self._new_file_delay = self.BASE_DELAY

        self._wrong_mon_delay = self.BASE_DELAY
        if self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_MON_SPECIES).value == None:
            self._waiting_for_solo_mon_in_slot_1 = True
            self._wrong_mon_in_slot_1 = False
        elif self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_MON_SPECIES).value != self.machine._solo_mon_species:
            self._waiting_for_solo_mon_in_slot_1 = False
            self._wrong_mon_in_slot_1 = True
        else:
            self._waiting_for_solo_mon_in_slot_1 = False
            self._wrong_mon_in_slot_1 = False
    
    def _on_exit(self, next_state: State):
        if isinstance(next_state, InventoryChangeState):
            next_state.external_held_item_flag = self._propagate_held_item_flag
        
        self._propagate_held_item_flag = False
    
    @auto_reset
    def transition(self, new_prop:GameHookProperty, prev_prop:GameHookProperty) -> StateType:
        # intentionally ignore all updates while waiting for a new file
        if self._waiting_for_new_file or self._waiting_for_solo_mon_in_slot_1:
            check_for_battle = False
            if new_prop.path == gh_gen_three_const.KEY_GAMETIME_SECONDS:
                if self._wrong_mon_delay <= 0:
                    self._waiting_for_solo_mon_in_slot_1 = False
                    self._wrong_mon_in_slot_1 = False
                    check_for_battle = True
                if self._new_file_delay <= 0:
                    self._waiting_for_new_file = False
                    self.machine._controller.route_restarted()
                    self.machine.update_all_cached_info(include_solo_mon=True)
                    check_for_battle = True
                self._new_file_delay -= 1
                self._wrong_mon_delay -= 1
            
            if (
                check_for_battle and
                self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FLAG).value and
                self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_OUTCOME).value is None
            ):
                return StateType.BATTLE
            return self.state_type

        ######
        # next two are the same condition check, just making sure we can handle them in either order
        ######
        if new_prop.path == gh_gen_three_const.KEY_BATTLE_OUTCOME:
            if new_prop.value is None and self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FLAG):
                return StateType.BATTLE
        elif new_prop.path == gh_gen_three_const.KEY_BATTLE_FLAG:
            if new_prop.value and self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_OUTCOME) is None:
                return StateType.BATTLE
        ######
        # end identical checks
        ######
        elif new_prop.path == gh_gen_three_const.KEY_OVERWORLD_MAP:
            self.machine._controller.entered_new_area(
                f"{self.machine._gamehook_client.get(gh_gen_three_const.KEY_OVERWORLD_MAP).value}"
            )
        elif new_prop.path == gh_gen_three_const.KEY_PLAYER_PLAYERID:
            if prev_prop.value and self.machine._player_id != self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_PLAYERID).value:
                self._waiting_for_new_file = True
        elif new_prop.path == gh_gen_three_const.KEY_PLAYER_MON_HELD_ITEM:
            self._propagate_held_item_flag = True
            if False:
                self.machine._queue_new_event(
                    EventDefinition(
                        hold_item=HoldItemEventDefinition(self.machine.gh_converter.item_name_convert(new_prop.value)),
                        notes=gh_gen_three_const.HELD_CHECK_FLAG
                    )
                )
        elif new_prop.path in gh_gen_three_const.ALL_KEYS_ALL_ITEM_FIELDS:
            return StateType.INVENTORY_CHANGE
        elif new_prop.path == gh_gen_three_const.KEY_PLAYER_MON_SPECIES:
            if not prev_prop.value:
                self._waiting_for_registration = True
            elif self.machine._solo_mon_species == self.machine.gh_converter.pkmn_name_convert(prev_prop.value):
                self._wrong_mon_in_slot_1 = True
            elif self.machine._solo_mon_species == self.machine.gh_converter.pkmn_name_convert(new_prop.value):
                self._wrong_mon_delay = self.BASE_DELAY
                self._waiting_for_solo_mon_in_slot_1 = True
        elif new_prop.path == gh_gen_three_const.KEY_PLAYER_MON_LEVEL:
            if not self._waiting_for_registration and not self._wrong_mon_in_slot_1:
                return StateType.RARE_CANDY
        elif new_prop.path in gh_gen_three_const.ALL_KEYS_PLAYER_MOVES:
            if not self._waiting_for_registration and not self._wrong_mon_in_slot_1:
                all_cur_moves = []
                for move_path in gh_gen_three_const.ALL_KEYS_PLAYER_MOVES:
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
        elif new_prop.path in gh_gen_three_const.ALL_KEYS_STAT_EXP:
            if not self._waiting_for_registration and not self._wrong_mon_in_slot_1:
                return StateType.VITAMIN
        elif new_prop.path == gh_gen_three_const.KEY_AUDIO_SOUND_EFFECT_1:
            # NOTE: this points to the currently loaded sound effect. If a single sound effect gets played multiple times in a row
            # then this won't change. Theoretically, there's another field, soundEffect1Played that we could hook into, to allow us to detect
            # when the actual changes occur. However, this is gets left on by default, and flickers between off/on so quickly that it sometimes gets
            # missed by gamehook. In practice, this approximation should cover all known edge cases
            if new_prop.bytes_value == gh_gen_three_const.SAVE_SOUND_EFFECT_BYTES_VALUE:
                self.machine._queue_new_event(EventDefinition(save=SaveEventDefinition(location=self.machine._gamehook_client.get(gh_gen_three_const.KEY_OVERWORLD_MAP).value)))
        elif new_prop.path == gh_gen_three_const.KEY_AUDIO_SOUND_EFFECT_2:
            # NOTE: same limitations as above
            if new_prop.bytes_value == gh_gen_three_const.HEAL_SOUND_EFFECT_BYTES_VALUE:
                self.machine._queue_new_event(EventDefinition(heal=HealEventDefinition(location=self.machine._gamehook_client.get(gh_gen_three_const.KEY_OVERWORLD_MAP).value)))
        elif new_prop.path == gh_gen_three_const.KEY_GAMETIME_SECONDS:
            if self._waiting_for_registration:
                if self._register_delay <= 0:
                    self._waiting_for_registration = False
                    self.machine.register_solo_mon(self.machine._gamehook_client.get(gh_gen_three_const.KEY_PLAYER_MON_SPECIES).value)
                self._register_delay -= 1

            if (
                self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_FLAG).value and
                self.machine._gamehook_client.get(gh_gen_three_const.KEY_BATTLE_OUTCOME).value is None
            ):
                return StateType.BATTLE


        return self.state_type
