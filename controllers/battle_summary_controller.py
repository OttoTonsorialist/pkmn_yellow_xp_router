from __future__ import annotations
from dataclasses import dataclass
import copy
import logging
from typing import Dict, List, Tuple
from controllers.main_controller import MainController
from pkmn.damage_calc import DamageRange, find_kill
from pkmn.universal_data_objects import BadgeList, EnemyPkmn, Move, StageModifiers
from routing.full_route_state import RouteState
from routing.state_objects import SoloPokemon
from utils.config_manager import config

from utils.constants import const
from routing.route_events import EventDefinition, EventGroup, RareCandyEventDefinition, TrainerEventDefinition
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


@dataclass
class MoveRenderInfo:
    name:str
    attack_flavor:List[str]
    damage_ranges:DamageRange
    crit_damage_ranges:DamageRange
    defending_mon_hp:int
    kill_ranges:List[Tuple[int, float]]
    mimic_data:str
    mimic_options:List[str]
    custom_data_options:List[str]
    custom_data_selection:str
    is_best_move:bool=False

@dataclass
class PkmnRenderInfo:
    attacking_mon_name:str
    attacking_mon_level:int
    attacking_mon_speed:int
    defending_mon_name:str
    defending_mon_level:int
    defending_mon_speed:int
    defending_mon_hp:int

    def __str__(self) -> str:
        if self.attacking_mon_speed > self.defending_mon_speed:
            verb = "outspeeds"
        elif self.defending_mon_speed > self.attacking_mon_speed:
            verb = "underspeeds"
        else:
            verb = "speed-ties"
        
        return f"Lv {self.attacking_mon_level}: {self.attacking_mon_name} {verb} Lv {self.defending_mon_level}: {self.defending_mon_name} ({self.defending_mon_hp} HP)"


class BattleSummaryController:
    def __init__(self, main_controller:MainController):
        self._main_controller = main_controller
        self._refresh_events = []
        self._nonload_change_events = []

        # trainer object data that we don't actually use, but need to hang on to to properly re-create events
        self._trainer_name = None
        self._event_group_id = None

        # actual state used to calculate battle stats
        self._original_player_mon_list:List[EnemyPkmn] = []
        self._player_setup_move_list:List[str] = []
        self._original_enemy_mon_list:List[EnemyPkmn] = []
        self._enemy_setup_move_list:List[str] = []

        self._mimic_options:List[str] = []
        self._player_mimic_selection:str = ""
        self._custom_move_data:List[Dict[str, Dict[str, str]]] = []
        self._cached_definition_order = []
        self._weather = None

        # NOTE: all of the state above this comment is considered the "true" state
        # The below state is all calculated based on values from the above state
        self._player_stage_modifier:StageModifiers = None
        self._enemy_stage_modifier:StageModifiers = None

        # NOTE: and finally, the actual display information
        # first idx: idx of pkmn in team
        # second idx: idx of move for pkmn pair
        self._player_move_data:List[List[MoveRenderInfo]] = []
        self._enemy_move_data:List[List[MoveRenderInfo]] = []
        # first idx: idx of pkmn in team
        self._player_pkmn_matchup_data:List[PkmnRenderInfo] = []
        self._enemy_pkmn_matchup_data:List[PkmnRenderInfo] = []

        self.load_empty()

    
    #####
    # Registration methods
    #####

    def register_nonload_change(self, tk_obj):
        new_event_name = const.EVENT_BATTLE_SUMMARY_NONLOAD_CHANGE.format(len(self._nonload_change_events))
        self._nonload_change_events.append((tk_obj, new_event_name))
        return new_event_name

    def register_refresh(self, tk_obj):
        new_event_name = const.EVENT_BATTLE_SUMMARY_REFRESH.format(len(self._refresh_events))
        self._refresh_events.append((tk_obj, new_event_name))
        return new_event_name

    #####
    # Event callbacks
    #####
    
    def _on_refresh(self):
        for tk_obj, cur_event_name in self._refresh_events:
            tk_obj.event_generate(cur_event_name, when="tail")
    
    def _on_nonload_change(self):
        for tk_obj, cur_event_name in self._nonload_change_events:
            tk_obj.event_generate(cur_event_name, when="tail")
    
    ######
    # Methods that induce a state change
    ######

    def update_mimic_selection(self, new_value):
        self._mimic_selection = new_value
        target_found = False
        for mon_idx in range(len(self._original_enemy_mon_list)):
            if not target_found:
                if new_value in self._original_enemy_mon_list[mon_idx].move_list:
                    target_found = True
            
            if not target_found:
                move_name = "Leer"
            else:
                move_name = self._mimic_selection
            
            if const.MIMIC_MOVE_NAME in self._original_player_mon_list[mon_idx].move_list:
                cur_mimic_idx = self._original_player_mon_list[mon_idx].move_list.index(const.MIMIC_MOVE_NAME)
                self._player_move_data[mon_idx][cur_mimic_idx] = self._recalculate_single_move(mon_idx, True, move_name, move_display_name=const.MIMIC_MOVE_NAME)
                self._update_best_move_inplace(mon_idx, True)

        self._on_refresh()
        self._on_nonload_change()

    def update_custom_move_data(self, pkmn_idx, move_idx, is_player_mon, new_value):
        try:
            if is_player_mon:
                move_data = self._player_move_data
                lookup_key = const.PLAYER_KEY
            else:
                move_data = self._enemy_move_data
                lookup_key = const.ENEMY_KEY

            move_name = move_data[pkmn_idx][move_idx].name
            self._custom_move_data[pkmn_idx][lookup_key][move_name] = new_value

            move_data[pkmn_idx][move_idx] = self._recalculate_single_move(pkmn_idx, is_player_mon, move_name)
            self._update_best_move_inplace(pkmn_idx, is_player_mon)

            self._on_refresh()
            self._on_nonload_change()
        except Exception as e:
            logger.error(f"encountered error updating custom move data: {pkmn_idx, move_idx, is_player_mon, new_value}")

    def update_weather(self, new_weather):
        self._weather = new_weather
        self._full_refresh()

    def update_enemy_setup_moves(self, new_setup_moves):
        self._enemy_setup_move_list = new_setup_moves
        self._full_refresh()

    def update_player_setup_moves(self, new_setup_moves):
        self._player_setup_move_list = new_setup_moves
        self._full_refresh()
    
    def update_prefight_candies(self, num_candies):
        if self._event_group_id is None:
            return
        
        prev_event = self._main_controller.get_previous_event(self._event_group_id, enabled_only=True)
        if prev_event is None or prev_event.event_definition is None or prev_event.event_definition.rare_candy is None:
            # If num_candies is 0 and we don't have a number to update, don't create a pointless "use 0 candies" event
            if num_candies <= 0:
                return
            self._main_controller.new_event(
                EventDefinition(rare_candy=RareCandyEventDefinition(amount=num_candies)),
                insert_before=self._event_group_id,
                do_select=False
            )
        else:
            self._main_controller.update_existing_event(
                prev_event.group_id,
                EventDefinition(rare_candy=RareCandyEventDefinition(amount=num_candies)),
            )
        
        self._full_refresh()
    
    def update_player_strategy(self, strat):
        config.set_player_highlight_strategy(strat)
        self._full_refresh()
    
    def update_enemy_strategy(self, strat):
        config.set_enemy_highlight_strategy(strat)
        self._full_refresh()
    
    def update_consistent_threshold(self, threshold:int):
        config.set_consistent_threshold(threshold)
        self._full_refresh()
    
    def _update_best_move_inplace(self, pkmn_idx, is_player_mon):
        # NOTE: this is a helper function that induces a state change, but does not directly (or indirectly) trigger any events
        # If you call this function, it is your responsibility to properly trigger an appropriate event independently
        if is_player_mon:
            move_data = self._player_move_data
            mon_data = self._player_pkmn_matchup_data[pkmn_idx]
        else:
            move_data = self._enemy_move_data
            mon_data = self._enemy_pkmn_matchup_data[pkmn_idx]

        best_move = None
        best_move_idx = None
        for idx, cur_move in enumerate(move_data[pkmn_idx]):
            if cur_move is None or cur_move.name == const.STRUGGLE_MOVE_NAME:
                continue

            if self._is_move_better(
                cur_move,
                best_move,
                config.get_player_highlight_strategy() if is_player_mon else config.get_enemy_highlight_strategy(),
                mon_data
            ):
                best_move = cur_move
                best_move_idx = idx
        
        for idx, cur_move in enumerate(move_data[pkmn_idx]):
            if cur_move is None:
                continue

            cur_move.is_best_move = idx == best_move_idx


    def _full_refresh(self, is_load=False):
        # Once the "true" state of the current battle has been updated, recalculate all the derived properties
        self._player_stage_modifier = self._calc_stage_modifier(self._player_setup_move_list)
        self._enemy_stage_modifier = self._calc_stage_modifier(self._enemy_setup_move_list)
        self._player_pkmn_matchup_data = []
        self._enemy_pkmn_matchup_data = []
        self._player_move_data = []
        self._enemy_move_data = []
        self._mimic_options = []

        can_mimic_yet = False
        for mon_idx in range(len(self._original_player_mon_list)):
            player_mon = self._original_player_mon_list[mon_idx]
            player_stats = player_mon.get_battle_stats(self._player_stage_modifier)
            enemy_mon = self._original_enemy_mon_list[mon_idx]
            enemy_stats = enemy_mon.get_battle_stats(self._enemy_stage_modifier)

            self._player_pkmn_matchup_data.append(
                PkmnRenderInfo(player_mon.name, player_mon.level, player_stats.speed, enemy_mon.name, enemy_mon.level, enemy_stats.speed, enemy_mon.cur_stats.hp)
            )
            self._enemy_pkmn_matchup_data.append(
                PkmnRenderInfo(enemy_mon.name, enemy_mon.level, enemy_stats.speed, player_mon.name, player_mon.level, player_stats.speed, player_mon.cur_stats.hp)
            )
            self._player_move_data.append([])
            self._enemy_move_data.append([])

            struggle_set = False
            for move_idx in range(4):
                # Handle the player move calculation
                if move_idx < len(player_mon.move_list):
                    move_name = player_mon.move_list[move_idx]
                    move_display_name = move_name
                    if move_name == const.MIMIC_MOVE_NAME:
                        if can_mimic_yet:
                            move_name = self._mimic_selection
                        elif self._mimic_selection and (self._mimic_selection in enemy_mon.move_list):
                            move_name = self._mimic_selection
                            can_mimic_yet = True
                        else:
                            move_name = "Leer"
                    
                    if not move_name and not struggle_set:
                        struggle_set = True
                        move_name = const.STRUGGLE_MOVE_NAME
                    
                    cur_player_move_data = self._recalculate_single_move(mon_idx, True, move_name, move_display_name=move_display_name)
                else:
                    cur_player_move_data = None

                # Now handle the enemy move calculation
                if move_idx < len(enemy_mon.move_list):
                    move_name = enemy_mon.move_list[move_idx]
                    if move_name and move_name not in self._mimic_options:
                        self._mimic_options.append(move_name)
                    cur_enemy_move_data = self._recalculate_single_move(mon_idx, False, move_name)
                else:
                    cur_enemy_move_data = None
                

                #####
                # Now the info has been generated for both sides of the fight. Add to the data structure, if appropriate
                #####
                self._player_move_data[mon_idx].append(cur_player_move_data)
                self._enemy_move_data[mon_idx].append(cur_enemy_move_data)

            #####
            # Finally out of move data loop. Update best moves
            #####
            self._update_best_move_inplace(mon_idx, True)
            self._update_best_move_inplace(mon_idx, False)
        
        # finally done calculating everything. Refresh and exit
        self._on_refresh()
        if not is_load:
            self._on_nonload_change()

    def _recalculate_single_move(
        self,
        mon_idx:int,
        is_player_mon:bool,
        move_name:str,
        move_display_name:str=None,
    ):
        if is_player_mon:
            attacking_mon = self._original_player_mon_list[mon_idx]
            attacking_stage_modifiers = self._player_stage_modifier
            defending_mon = self._original_enemy_mon_list[mon_idx]
            defending_stage_modifiers = self._enemy_stage_modifier
            custom_lookup_key = const.PLAYER_KEY
        else:
            attacking_mon = self._original_enemy_mon_list[mon_idx]
            attacking_stage_modifiers = self._enemy_stage_modifier
            defending_mon = self._original_player_mon_list[mon_idx]
            defending_stage_modifiers = self._player_stage_modifier
            custom_lookup_key = const.ENEMY_KEY

        if not move_name:
            return None
        move = current_gen_info().move_db().get_move(move_name)
        if move is None:
            logger.error(f"invalid move encountered during battle summary calculations: {move_name}")
            return None
        if move.name == const.HIDDEN_POWER_MOVE_NAME:
            hidden_power_type, hidden_power_base_power = current_gen_info().get_hidden_power(attacking_mon.dvs)
            move_display_name = f"{move.name} ({hidden_power_type}: {hidden_power_base_power})"
        
        if move_display_name is None:
            move_display_name = move.name

        custom_data_selection = self._custom_move_data[mon_idx][custom_lookup_key].get(move_name)
        custom_data_options = current_gen_info().get_move_custom_data(move.name)
        if custom_data_options is None and const.FLAVOR_MULTI_HIT in move.attack_flavor:
            custom_data_options = const.MULTI_HIT_CUSTOM_DATA
        
        if custom_data_options is None:
            custom_data_selection = None
        elif custom_data_selection not in custom_data_options:
            custom_data_selection = custom_data_options[0]

        normal_ranges = current_gen_info().calculate_damage(
            attacking_mon,
            move,
            defending_mon,
            attacking_stage_modifiers=attacking_stage_modifiers,
            defending_stage_modifiers=defending_stage_modifiers,
            custom_move_data=custom_data_selection,
            weather=self._weather
        )
        crit_ranges = current_gen_info().calculate_damage(
            attacking_mon,
            move,
            defending_mon,
            attacking_stage_modifiers=attacking_stage_modifiers,
            defending_stage_modifiers=defending_stage_modifiers,
            custom_move_data=custom_data_selection,
            is_crit=True,
            weather=self._weather
        )
        if normal_ranges is not None and crit_ranges is not None:
            if config.do_ignore_accuracy():
                accuracy = 100
            else:
                accuracy = move.accuracy
                if accuracy is None:
                    accuracy = 100

            accuracy = float(accuracy) / 100.0

            kill_ranges = find_kill(
                normal_ranges,
                crit_ranges,
                current_gen_info().get_crit_rate(attacking_mon, move),
                accuracy,
                defending_mon.cur_stats.hp,
                attack_depth=config.get_damage_search_depth()
            )
        else:
            kill_ranges = []

        return MoveRenderInfo(
            move_display_name,
            move.attack_flavor,
            normal_ranges,
            crit_ranges,
            defending_mon.cur_stats.hp,
            kill_ranges,
            self._mimic_selection,
            self._mimic_options,
            custom_data_options,
            custom_data_selection
        )

    def load_from_event(self, event_group:EventGroup):
        if event_group is None or event_group.event_definition is None or event_group.event_definition.trainer_def is None:
            self.load_empty()
            return

        self._event_group_id = event_group.group_id
        trainer_def = event_group.event_definition.trainer_def
        trainer_obj = event_group.event_definition.get_trainer_obj()

        self._trainer_name = trainer_def.trainer_name
        self._weather = trainer_def.weather
        self._mimic_selection = trainer_def.mimic_selection
        self._player_setup_move_list = trainer_def.setup_moves.copy()
        self._player_stage_modifier = self._calc_stage_modifier(self._player_setup_move_list)
        self._enemy_setup_move_list = trainer_def.enemy_setup_moves.copy()
        self._enemy_stage_modifier = self._calc_stage_modifier(self._enemy_setup_move_list)
        self._cached_definition_order = [x.mon_order - 1 for x in event_group.event_definition.get_pokemon_list(definition_order=True)]
        if not trainer_def.custom_move_data:
            self._custom_move_data = []
            for _ in range(len(trainer_obj.pkmn)):
                self._custom_move_data.append({const.PLAYER_KEY: {}, const.ENEMY_KEY: {}})
        else:
            self._custom_move_data = [copy.deepcopy(x.custom_move_data) for x in event_group.event_definition.get_pokemon_list()]

        self._original_player_mon_list = []
        self._original_enemy_mon_list = []

        # NOTE: kind of weird, but basically we want to iterate over all the pokemon we want to fight, and then get the appropriate
        # event item for fighting that pokemon. This allows us to pull learned moves/levelups/etc automatically
        cur_item_idx = 0
        for cur_pkmn in event_group.event_definition.get_pokemon_list():
            while cur_item_idx < len(event_group.event_items):
                cur_event_item = event_group.event_items[cur_item_idx]
                cur_item_pkmn_list = cur_event_item.event_definition.get_pokemon_list()

                # skip level-up events mid-fight
                if not cur_item_pkmn_list:
                    cur_item_idx += 1
                    continue

                if cur_item_pkmn_list[cur_event_item.to_defeat_idx].name == cur_pkmn.name:
                    self._original_enemy_mon_list.append(cur_pkmn)
                    self._original_player_mon_list.append(
                        cur_event_item.init_state.solo_pkmn.get_pkmn_obj(
                            cur_event_item.init_state.badges,
                            stage_modifiers=self._player_stage_modifier
                        )
                    )
                    break
                cur_item_idx += 1
        
        self._full_refresh(is_load=True)

    def load_from_state(self, init_state:RouteState, enemy_mons:List[EnemyPkmn], trainer_name:str=None):
        if init_state is None or not enemy_mons:
            self.load_empty()
            return

        self._event_group_id = None
        self._trainer_name = trainer_name
        self._weather = const.WEATHER_NONE
        self._mimic_selection = ""
        self._player_setup_move_list = []
        self._enemy_setup_move_list = []
        self._custom_move_data = []
        self._cached_definition_order = list(range(len(enemy_mons)))
        for _ in range(len(enemy_mons)):
            self._custom_move_data.append({const.PLAYER_KEY: {}, const.ENEMY_KEY: {}})

        self._original_player_mon_list = []
        self._original_enemy_mon_list = []

        cur_state = init_state
        for cur_enemy in enemy_mons:
            self._original_enemy_mon_list.append(cur_enemy)
            self._original_player_mon_list.append(cur_state.solo_pkmn.get_pkmn_obj(cur_state.badges))

            cur_state = cur_state.defeat_pkmn(cur_enemy)[0]

        self._full_refresh(is_load=True)
    
    def load_empty(self):
        self._event_group_id = None
        self._trainer_name = ""
        self._weather = const.WEATHER_NONE
        self._mimic_selection = ""
        self._player_setup_move_list = []
        self._enemy_setup_move_list = []
        self._custom_move_data = []
        self._original_player_mon_list = []
        self._original_enemy_mon_list = []
        self._cached_definition_order = []
        self._full_refresh(is_load=True)

    ######
    # Methods that do not induce a state change
    ######

    def get_trainer_definition(self) -> TrainerEventDefinition:
        if not self._trainer_name:
            return None

        is_custom_move_data_present = False
        for cur_test in self._custom_move_data:
            if len(cur_test[const.PLAYER_KEY]) > 0 or len(cur_test[const.ENEMY_KEY]) > 0:
                is_custom_move_data_present = True
                break
        
        if is_custom_move_data_present:
            final_custom_move_data = [self._custom_move_data[x] for x in self._cached_definition_order]
        else:
            final_custom_move_data = None

        return TrainerEventDefinition(
            self._trainer_name,
            setup_moves=self._player_setup_move_list,
            enemy_setup_moves=self._enemy_setup_move_list,
            mimic_selection=self._mimic_selection,
            custom_move_data=final_custom_move_data,
            weather=self._weather
        )
    
    def get_pkmn_info(self, pkmn_idx, is_player_mon) -> PkmnRenderInfo:
        if is_player_mon:
            cur_data = self._player_pkmn_matchup_data
        else:
            cur_data = self._enemy_pkmn_matchup_data
        
        if pkmn_idx < 0 or pkmn_idx >= len(cur_data):
            return None
        
        return cur_data[pkmn_idx]

    def get_move_info(self, pkmn_idx, move_idx, is_player_mon) -> MoveRenderInfo:
        if is_player_mon:
            cur_move_data = self._player_move_data
        else:
            cur_move_data = self._enemy_move_data

        if pkmn_idx < 0 or pkmn_idx >= len(cur_move_data) or move_idx < 0 or move_idx >= 4:
            return None
        
        return cur_move_data[pkmn_idx][move_idx]

    def get_weather(self) -> str:
        return self._weather

    def get_player_setup_moves(self) -> List[str]:
        return self._player_setup_move_list

    def get_enemy_setup_moves(self) -> List[str]:
        return self._enemy_setup_move_list

    @staticmethod
    def _is_move_better(new_move:MoveRenderInfo, prev_move:MoveRenderInfo, strat:str, other_mon:PkmnRenderInfo) -> bool:
        if (
            strat is None or
            not isinstance(strat, str) or
            strat == const.HIGHLIGHT_NONE or
            strat not in const.ALL_HIGHLIGHT_STRATS
        ):
            return False

        if new_move is None or new_move.damage_ranges is None:
            return False

        if prev_move is None or prev_move.damage_ranges is None:
            return True

        # special case for recharge moves (e.g. Hyper Beam)
        # If a one-hit is not possible without a crit, always prefer other damage dealing moves
        if const.FLAVOR_RECHARGE in new_move.attack_flavor and new_move.damage_ranges.max_damage < other_mon.defending_mon_hp:
            return False
        elif const.FLAVOR_RECHARGE in prev_move.attack_flavor and prev_move.damage_ranges.max_damage < other_mon.defending_mon_hp:
            return True
        
        new_fastest_kill = 1000000
        new_accuracy = -2
        if len(new_move.kill_ranges) > 0:
            if strat == const.HIGHLIGHT_GUARANTEED_KILL:
                # if the last slot has a -1 % to kill, then that means it was auto-calculated
                if config.do_ignore_accuracy() or new_move.kill_ranges[-1][1] != -1:
                    new_fastest_kill, new_accuracy = new_move.kill_ranges[-1]

            elif strat == const.HIGHLIGHT_FASTEST_KILL:
                new_fastest_kill, new_accuracy = new_move.kill_ranges[0]
            elif strat == const.HIGHLIGHT_CONSISTENT_KILL:
                for test_kill in new_move.kill_ranges:
                    if test_kill[1] >= config.get_consistent_threshold():
                        new_fastest_kill, new_accuracy = test_kill
                        break
        
        prev_fastest_kill = new_fastest_kill + 1
        prev_accuracy = -2
        if len(prev_move.kill_ranges) > 0:
            if strat == const.HIGHLIGHT_GUARANTEED_KILL:
                prev_fastest_kill, prev_accuracy = prev_move.kill_ranges[-1]
            elif strat == const.HIGHLIGHT_FASTEST_KILL:
                prev_fastest_kill, prev_accuracy = prev_move.kill_ranges[0]
            elif strat == const.HIGHLIGHT_CONSISTENT_KILL:
                for test_kill in prev_move.kill_ranges:
                    if test_kill[1] >= config.get_consistent_threshold():
                        prev_fastest_kill, prev_accuracy = test_kill
                        break

        
        # always prefer lower number of turns
        if new_fastest_kill < prev_fastest_kill:
            return True
        elif prev_fastest_kill < new_fastest_kill:
            return False
        
        # if number of turns is tied, then prefer higher accuracy
        # note that accuracy might be "-1" in the case of auto-calculated kills
        # but that's fine, because we want higher accuracy, so it will always "lose", which is desirable
        if new_accuracy > prev_accuracy:
            return True
        elif prev_accuracy > new_accuracy:
            return False

        # if number of turns and accuracy is tied, punish moves that take more than one turn
        if (
            const.FLAVOR_TWO_TURN in prev_move.attack_flavor or
            const.FLAVOR_TWO_TURN_INVULN in prev_move.attack_flavor
        ):
            return True
        elif (
            const.FLAVOR_TWO_TURN in new_move.attack_flavor or
            const.FLAVOR_TWO_TURN_INVULN in new_move.attack_flavor
        ):
            return False
        
        # Only rely on damage for tie breakers
        return new_move.damage_ranges.max_damage > prev_move.damage_ranges.max_damage

    @staticmethod
    def _calc_stage_modifier(move_list) -> StageModifiers:
        result = StageModifiers()

        for cur_move in move_list:
            result = result.apply_stat_mod(current_gen_info().move_db().get_stat_mod(cur_move))
        
        return result
    
    def can_support_prefight_candies(self):
        return self._event_group_id is not None
    
    def get_prefight_candy_count(self):
        if self._event_group_id is None:
            return 0
        
        prev_event = self._main_controller.get_previous_event(self._event_group_id, enabled_only=True)
        if prev_event is None or prev_event.event_definition.rare_candy is None:
            return 0
        
        return prev_event.event_definition.rare_candy.amount
        
