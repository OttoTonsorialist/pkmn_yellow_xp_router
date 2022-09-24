import tkinter as tk
import tkinter.font
import datetime
from typing import List

from gui import custom_tkinter
import pkmn.data_objects as data_objects
from pkmn import route_state_objects
from pkmn import route_events
from pkmn.router import Router
from utils.constants import const
from pkmn import pkmn_damage_calc
from pkmn import pkmn_db


class BattleSummary(tk.Frame):
    def __init__(self, *args, font_size=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.columnconfigure(0, weight=1)

        # these are matched lists, with the solo mon being updated for each enemy pkmn, in case of level-ups
        self._enemy_pkmn:List[data_objects.EnemyPkmn] = None
        self._solo_pkmn:List[data_objects.EnemyPkmn] = None
        self._source_state:route_state_objects.RouteState = None
        self._source_event_group:route_events.EventGroup = None
        self._stage_modifiers:data_objects.StageModifiers = data_objects.StageModifiers()

        self.setup_moves = SetupMovesSummary(self, callback=self._setup_move_callback)
        self.setup_moves.grid(row=0, column=0, sticky=tk.EW)

        self._mon_pairs:List[MonPairSummary] = []

        for idx in range(6):
            self._mon_pairs.append(MonPairSummary(self, mimic_callback=self._mimic_callback))
        
        self.error_message = tk.Label(self, text="Select a battle to see damage calculations")
        self.should_calculate = False
        self.set_team(None)
    
    def _setup_move_callback(self):
        self.set_team(self._enemy_pkmn, cur_state=self._source_state, event_group=self._source_event_group, new_setup_moves=True)
    
    def _mimic_callback(self, mimiced_move_name):
        for cur_pair in self._mon_pairs:
            cur_pair.recalc_mimic(mimiced_move_name)
    
    def allow_calculations(self):
        # trigger calculations if they were paused before
        if not self.should_calculate:
            recalc = True
        self.should_calculate = True

        if recalc:
            self.set_team(self._enemy_pkmn, cur_state=self._source_state, event_group=self._source_event_group, recalc_only=True)
    
    def get_setup_moves(self):
        return self.setup_moves._move_list.copy()

    def pause_calculations(self):
        self.should_calculate = False
        # wipe out the rendering when not calculating
        # but only recalc, so we still remember what the current state and enemy pkmn are
        self.set_team(None, recalc_only=True)
    
    def set_team(
        self,
        enemy_pkmn:List[data_objects.EnemyPkmn],
        cur_state:route_state_objects.RouteState=None,
        event_group:route_events.EventGroup=None,
        new_setup_moves:bool=False,
        recalc_only:bool=False
    ):
        # use the passed information to figure out the exact solo mon objects to use
        new_solo_pkmn = []

        if event_group is not None and len(event_group.event_items) > 0:
            cur_item_idx = 0
            if not new_setup_moves:
                self.setup_moves.set_move_list(event_group.event_definition.trainer_def.setup_moves.copy())
            self._stage_modifiers = self.setup_moves.get_stage_modifiers()
            for cur_pkmn in enemy_pkmn:
                while cur_item_idx < len(event_group.event_items):
                    try:
                        cur_event_item = event_group.event_items[cur_item_idx]
                        cur_item_pkmn_list = cur_event_item.event_definition.get_pokemon_list()
                        if not cur_item_pkmn_list:
                            cur_item_idx += 1
                            continue
                        if cur_item_pkmn_list[cur_event_item.to_defeat_idx].name == cur_pkmn.name:
                            new_solo_pkmn.append(
                                cur_event_item.init_state.solo_pkmn.get_pkmn_obj(cur_event_item.init_state.badges, stage_modifiers=self._stage_modifiers)
                            )

                            with_mods = cur_event_item.init_state.solo_pkmn.get_pkmn_obj(cur_event_item.init_state.badges, stage_modifiers=self._stage_modifiers)
                            without_mods = cur_event_item.init_state.solo_pkmn.get_pkmn_obj(cur_event_item.init_state.badges)
                            break
                        cur_item_idx += 1
                    except Exception as e:
                        print(f"Failed to extra solo mon info from event group: ({type(e)}) {e}")
                        raise e
        elif cur_state is not None:
            if not new_setup_moves:
                self.setup_moves.set_move_list([])
            self._stage_modifiers = self.setup_moves.get_stage_modifiers()
            for cur_pkmn in enemy_pkmn:
                new_solo_pkmn.append(cur_state.solo_pkmn.get_pkmn_obj(cur_state.badges, stage_modifiers=self._stage_modifiers))
                cur_state, _ = cur_state.defeat_pkmn(cur_pkmn)

        if enemy_pkmn is not None and len(enemy_pkmn) != len(new_solo_pkmn):
            raise ValueError(f"Failed to properly extract solo mon information. Mismatching mon lengths: {len(enemy_pkmn)} vs {len(new_solo_pkmn)}")

        if (
            enemy_pkmn is not None and
            enemy_pkmn == self._enemy_pkmn and
            new_solo_pkmn == self._solo_pkmn and 
            not recalc_only
        ):
            # if we're being asked to render what's already on-screen (and not forcing a refresh)
            # then we're already rendering the correct thing
            return
        
        if not recalc_only:
            # when recalcing, don't store what's being used, just render it
            self._enemy_pkmn = enemy_pkmn
            self._source_event_group = event_group
            self._source_state = cur_state
            self._solo_pkmn = new_solo_pkmn
        
        if enemy_pkmn is None or not self.should_calculate:
            enemy_pkmn = []
            self.error_message.grid(row=10, column=0)
        else:
            self.error_message.grid_forget()

        mimic_options = []
        for cur_pkmn in enemy_pkmn:
            mimic_options.extend(cur_pkmn.move_list)

        idx = -1
        enemy_stages = data_objects.StageModifiers()
        for idx, cur_pkmn in enumerate(enemy_pkmn):
            self._mon_pairs[idx].set_mons(new_solo_pkmn[idx], cur_pkmn, self._stage_modifiers, enemy_stages, mimic_options)
            self._mon_pairs[idx].grid(row=idx + 1, column=0, sticky=tk.EW)
        
        for missing_idx in range(idx+1, 6):
            self._mon_pairs[missing_idx].grid_forget()
        
        # manually trigger mimic callback once, so the initial values get calced
        if len(enemy_pkmn) >= 1:
            self._mon_pairs[0].manual_mimic_trigger()


class SetupMovesSummary(tk.Frame):
    def __init__(self, *args, font_size=None, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._callback = callback
        self._move_list = []

        self.reset_button = custom_tkinter.SimpleButton(self, text="Reset Setup Moves", command=self._reset)
        self.reset_button.grid(row=0, column=0, padx=2)

        self.setup_label = tk.Label(self, text="Move to Add:")
        self.setup_label.grid(row=0, column=1, padx=2)

        stat_modifier_moves = list(const.STAT_INCREASE_MOVES.keys())
        stat_modifier_moves += list(const.STAT_DECREASE_MOVES.keys())
        self.setup_moves = custom_tkinter.SimpleOptionMenu(self, stat_modifier_moves)
        self.setup_moves.grid(row=0, column=2, padx=2)

        self.add_button = custom_tkinter.SimpleButton(self, text="Add Setup Move", command=self._add_setup_move)
        self.add_button.grid(row=0, column=3, padx=2)

        self.extra_label = tk.Label(self, text="Current Setup Moves:")
        self.extra_label.grid(row=0, column=4, padx=2)

        self.move_list_label = tk.Label(self)
        self.move_list_label.grid(row=0, column=5, padx=2)
    
    def _reset(self, *args, **kwargs):
        self._move_list = []
        self._move_list_updated()
    
    def _add_setup_move(self, *args, **kwargs):
        self._move_list.append(self.setup_moves.get())
        self._move_list_updated()
    
    def set_move_list(self, new_moves, trigger_update=False):
        self._move_list = new_moves
        self._move_list_updated(trigger_update=trigger_update)
    
    def get_stage_modifiers(self):
        result = data_objects.StageModifiers()

        for cur_move in self._move_list:
            result = result.after_move(cur_move)
        
        return result
    
    def _move_list_updated(self, trigger_update=True):
        to_display = ", ".join(self._move_list)
        if not to_display:
            to_display = "None"

        self.move_list_label.configure(text=to_display)
        if self._callback is not None and trigger_update:
            self._callback()


class MonPairSummary(tk.Frame):
    def __init__(self, *args, font_size=None, mimic_callback=None, **kwargs):
        super().__init__(*args, **kwargs, highlightbackground="black", highlightthickness=1)

        self.mimic_callback = mimic_callback

        self.first_mon:data_objects.EnemyPkmn = None
        self.second_mon:data_objects.EnemyPkmn = None
        self.first_stages:data_objects.StageModifiers = None
        self.second_stages:data_objects.StageModifiers = None
        self.mimic_options = None

        bold_font = tkinter.font.nametofont("TkDefaultFont").copy()
        bold_font.configure(weight="bold")

        self.left_mon_label_frame = tk.Frame(self, background=const.HEADER_BG_COLOR)
        self.left_mon_label_frame.grid(row=0, column=0, columnspan=4, sticky=tk.EW, padx=2, pady=2)

        self.left_attacking_mon = tk.Label(self.left_mon_label_frame, text="", background=const.HEADER_BG_COLOR)
        self.left_attacking_mon.grid(row=0, column=1)
        self.left_verb = tk.Label(self.left_mon_label_frame, text="", background=const.HEADER_BG_COLOR, font=bold_font)
        self.left_verb.grid(row=0, column=2)
        self.left_defending_mon = tk.Label(self.left_mon_label_frame, text="", background=const.HEADER_BG_COLOR)
        self.left_defending_mon.grid(row=0, column=3)

        self.left_mon_label_frame.columnconfigure(0, weight=1, uniform="left_col_group")
        self.left_mon_label_frame.columnconfigure(4, weight=1, uniform="left_col_group")

        self.divider = tk.Frame(self, background=const.IMPORTANT_COLOR, width=4)
        self.divider.grid(row=0, column=4, rowspan=2, sticky=tk.NS)
        self.divider.grid_propagate(0)

        self.right_mon_label_frame = tk.Frame(self, background=const.HEADER_BG_COLOR)
        self.right_mon_label_frame.grid(row=0, column=5, columnspan=4, sticky=tk.EW, padx=2, pady=2)

        self.right_attacking_mon = tk.Label(self.right_mon_label_frame, text="", background=const.HEADER_BG_COLOR)
        self.right_attacking_mon.grid(row=0, column=1)
        self.right_verb = tk.Label(self.right_mon_label_frame, text="", background=const.HEADER_BG_COLOR, font=bold_font)
        self.right_verb.grid(row=0, column=2)
        self.right_defending_mon = tk.Label(self.right_mon_label_frame, text="", background=const.HEADER_BG_COLOR)
        self.right_defending_mon.grid(row=0, column=3)

        self.right_mon_label_frame.columnconfigure(0, weight=1, uniform="right_col_group")
        self.right_mon_label_frame.columnconfigure(4, weight=1, uniform="right_col_group")

        self.columnconfigure(0, weight=1, uniform="label_group")
        self.columnconfigure(1, weight=1, uniform="label_group")

        self.columnconfigure(0, weight=1, uniform="move_group")
        self.columnconfigure(1, weight=1, uniform="move_group")
        self.columnconfigure(2, weight=1, uniform="move_group")
        self.columnconfigure(3, weight=1, uniform="move_group")

        self.columnconfigure(5, weight=1, uniform="move_group")
        self.columnconfigure(6, weight=1, uniform="move_group")
        self.columnconfigure(7, weight=1, uniform="move_group")
        self.columnconfigure(8, weight=1, uniform="move_group")

        self.move_list:List[DamageSummary] = []
        for _ in range(8):
            self.move_list.append(DamageSummary(self, mimic_callback=self.mimic_callback))
    
    def recalc_mimic(self, mimiced_move_name):
        for cur_move in self.move_list:
            if cur_move.move_name == const.MIMIC_MOVE_NAME:
                cur_move.new_mimic_move_selected(mimiced_move_name)
                self._update_best_move()
                return
    
    def manual_mimic_trigger(self):
        for cur_move in self.move_list:
            if cur_move.move_name == const.MIMIC_MOVE_NAME:
                cur_move._mimic_callback()
                self._update_best_move()
                return
    
    def _update_best_move(self):
        cur_best_attack_idx = None
        cur_best_guaranteed_kill = None
        cur_best_damage_roll = None

        # NOTE: intentionally not capturing struggle damage calcs here
        # Mostly because we don't really ever want to use struggle if we can avoid it
        for idx in range(len(self.first_mon.move_list)):
            if not self.first_mon.move_list[idx]:
                break

            if self.move_list[idx].cur_guaranteed_kill is not None:
                if (
                    cur_best_guaranteed_kill is None or
                    self.move_list[idx].cur_guaranteed_kill < cur_best_guaranteed_kill or (
                        self.move_list[idx].cur_guaranteed_kill == cur_best_guaranteed_kill and
                        self.move_list[idx].cur_max_roll > cur_best_damage_roll
                    )
                ):
                    cur_best_attack_idx = idx
                    cur_best_guaranteed_kill = self.move_list[idx].cur_guaranteed_kill
                    cur_best_damage_roll = self.move_list[idx].cur_max_roll

        for idx in range(len(self.first_mon.move_list)):
            if idx == cur_best_attack_idx:
                self.move_list[idx].flag_as_best_move()
            else:
                self.move_list[idx].unflag_as_best_move()
    
    def set_mons(
        self,
        first_mon:data_objects.EnemyPkmn,
        second_mon:data_objects.EnemyPkmn,
        first_stages:data_objects.StageModifiers,
        second_stages:data_objects.StageModifiers,
        mimic_options
    ):
        self.first_mon = first_mon
        self.second_mon = second_mon
        self.first_stages = first_stages
        self.second_stages = second_stages
        self.mimic_options = mimic_options

        first_mon_speed = self.first_mon.get_battle_stats(first_stages).speed
        second_mon_speed = self.second_mon.get_battle_stats(second_stages).speed

        if first_mon_speed > second_mon_speed:
            first_mon_verb = "outspeeds"
            second_mon_verb = "underspeeds"
        elif second_mon_speed > first_mon_speed:
            second_mon_verb = "outspeeds"
            first_mon_verb = "underspeeds"
        else:
            second_mon_verb = "speed-ties"
            first_mon_verb = "speed-ties"

        self.left_attacking_mon.configure(text=f"{self.first_mon}")
        self.left_verb.configure(text=f"{first_mon_verb}")
        self.left_defending_mon.configure(text=f"{self.second_mon} ({self.second_mon.hp} HP)")

        self.right_attacking_mon.configure(text=f"{self.second_mon}")
        self.right_verb.configure(text=f"{second_mon_verb}")
        self.right_defending_mon.configure(text=f"{self.first_mon} ({self.first_mon.hp} HP)")

        # update all the moves for the first attacking the second
        struggle_set = False
        idx = -1
        for idx in range(4):
            # first mon attacking second
            cur_move = None
            if idx < len(self.first_mon.move_list):
                cur_move = self.first_mon.move_list[idx]
            
            if cur_move:
                self.move_list[idx].calc_damages(cur_move, self.first_mon, self.second_mon, self.first_stages, self.second_stages, self.mimic_options)
                self.move_list[idx].grid(row=1, column=idx, sticky=tk.NSEW)
            elif not struggle_set:
                self.move_list[idx].calc_damages(const.STRUGGLE_MOVE_NAME, self.first_mon, self.second_mon, self.first_stages, self.second_stages, self.mimic_options)
                self.move_list[idx].grid(row=1, column=idx, sticky=tk.NSEW)
                struggle_set = True
            else:
                self.move_list[idx].grid_forget()
            
            # second mon attacking first
            cur_move = None
            if idx < len(self.second_mon.move_list):
                cur_move = self.second_mon.move_list[idx]

            if cur_move:
                self.move_list[idx + 4].calc_damages(cur_move, self.second_mon, self.first_mon, self.second_stages, self.first_stages, self.mimic_options)
                self.move_list[idx + 4].grid(row=1, column=(5 + idx), sticky=tk.NSEW)
            else:
                self.move_list[idx + 4].grid_forget()
        
        self._update_best_move()


class DamageSummary(tk.Frame):
    def __init__(self, *args, font_size=None, mimic_callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.cur_guaranteed_kill = None
        self.cur_max_roll = None

        self.attacking_mon = None
        self.defending_mon = None
        self.move_name = None
        self.attacking_stage_modifiers = None
        self.defending_stage_modifiers = None
        self._propagate_mimic_update = True
        self._outer_mimic_callback = mimic_callback

        self.config(padx=2, pady=2)
        self.columnconfigure(0, weight=1)

        self.row_idx = 0

        self.header = tk.Frame(self, background=const.MOVE_BG_COLOR)
        self.header.grid(row=self.row_idx, column=0, sticky=tk.NSEW)
        self.header.columnconfigure(0, weight=1)
        self.row_idx += 1

        self.move_name_label = tk.Label(self.header, background=const.MOVE_BG_COLOR)
        self.mimic_dropdown = custom_tkinter.SimpleOptionMenu(self.header, [""], callback=self._mimic_callback, width=15)

        temp_bg_color = "white"
        self.range_frame = tk.Frame(self, background=temp_bg_color)
        self.range_frame.grid(row=self.row_idx, column=0, sticky=tk.NSEW)
        self.range_frame.columnconfigure(0, weight=1)
        self.row_idx += 1

        self.damage_range = tk.Label(self.range_frame, background=temp_bg_color)
        self.damage_range.grid(row=0, column=0, sticky=tk.W)
        self.pct_damage_range = tk.Label(self.range_frame, background=temp_bg_color)
        self.pct_damage_range.grid(row=0, column=1, sticky=tk.E)
        self.crit_damage_range = tk.Label(self.range_frame, background=temp_bg_color)
        self.crit_damage_range.grid(row=1, column=0, sticky=tk.W)
        self.crit_pct_damage_range = tk.Label(self.range_frame, background=temp_bg_color)
        self.crit_pct_damage_range.grid(row=1, column=1, sticky=tk.E)

        self.kill_frame = tk.Frame(self, background=const.STAT_BG_COLOR)
        self.kill_frame.grid(row=self.row_idx, column=0, sticky=tk.NSEW)
        self.rowconfigure(self.row_idx, weight=1)
        self.row_idx += 1

        self.num_to_kill = tk.Label(self.kill_frame, justify=tk.LEFT, background=const.STAT_BG_COLOR)
        self.num_to_kill.grid(row=0, column=0, sticky=tk.NSEW)
    
    def flag_as_best_move(self):
        self.kill_frame.configure(background=const.SPEED_WIN_COLOR)
        self.num_to_kill.configure(background=const.SPEED_WIN_COLOR)

    def unflag_as_best_move(self):
        self.kill_frame.configure(background=const.STAT_BG_COLOR)
        self.num_to_kill.configure(background=const.STAT_BG_COLOR)
    
    def _mimic_callback(self, *args, **kwargs):
        if self._propagate_mimic_update:
            mimiced_move = pkmn_db.move_db.get_move(self.mimic_dropdown.get())
            if mimiced_move is None:
                raise ValueError(f"Unknown move from mimic dropdown: {self.mimic_dropdown.get()}")

            if self._outer_mimic_callback is not None:
                self._outer_mimic_callback(mimiced_move.name)

    def new_mimic_move_selected(self, move_name):
        try:
            self._propagate_mimic_update = False
            self.mimic_dropdown.set(move_name)
            self._calc_damages_from_move(pkmn_db.move_db.get_move(move_name))
        finally:
            self._propagate_mimic_update = True

    def calc_damages(
        self,
        move_name,
        attacking_mon:data_objects.EnemyPkmn,
        defending_mon:data_objects.EnemyPkmn,
        attacking_stage_modifiers:data_objects.StageModifiers,
        defending_stage_modifiers:data_objects.StageModifiers,
        mimic_options:List,
    ):

        self.attacking_mon = attacking_mon
        self.defending_mon = defending_mon
        self.move_name = move_name
        self.attacking_stage_modifiers = attacking_stage_modifiers
        self.defending_stage_modifiers = defending_stage_modifiers

        move = pkmn_db.move_db.get_move(move_name)
        if move is None:
            raise ValueError(f"Unknown move: {move_name}")
        self.move_name_label.configure(text=move_name)

        if move_name == const.MIMIC_MOVE_NAME:
            self.move_name_label.grid_forget()
            self.move_name_label.grid(row=0, column=0)
            self._propagate_mimic_update = False
            self.mimic_dropdown.grid(row=0, column=1)
            self.mimic_dropdown.new_values(mimic_options)
            self._propagate_mimic_update = True
        else:
            self.move_name_label.grid_forget()
            self.move_name_label.grid(row=0, column=0, columnspan=2)
            self.mimic_dropdown.grid_forget()
            self._calc_damages_from_move(move)

    def _calc_damages_from_move(self, move:data_objects.Move):
        single_attack = pkmn_damage_calc.calculate_damage(
            self.attacking_mon,
            move,
            self.defending_mon,
            attacking_stage_modifiers=self.attacking_stage_modifiers,
            defending_stage_modifiers=self.defending_stage_modifiers,
        )
        crit_attack = pkmn_damage_calc.calculate_damage(
            self.attacking_mon,
            move,
            self.defending_mon,
            attacking_stage_modifiers=self.attacking_stage_modifiers,
            defending_stage_modifiers=self.defending_stage_modifiers,
            is_crit=True
        )

        if single_attack is None:
            self.cur_guaranteed_kill = None
            self.cur_max_roll = None
            self.damage_range.configure(text="")
            self.pct_damage_range.configure(text="")
            self.crit_damage_range.configure(text="")
            self.crit_pct_damage_range.configure(text="")
            self.kill_frame.configure(background=const.STAT_BG_COLOR)
            self.num_to_kill.configure(text="", background=const.STAT_BG_COLOR)
        else:
            self.damage_range.configure(text=f"{single_attack.min_damage} - {single_attack.max_damage}")
            pct_min_damage = f"{single_attack.min_damage / self.defending_mon.hp * 100:.2f}%"
            pct_max_damage = f"{single_attack.max_damage / self.defending_mon.hp * 100:.2f}%"
            self.pct_damage_range.configure(text=f"{pct_min_damage} - {pct_max_damage}")

            self.crit_damage_range.configure(text=f"{crit_attack.min_damage} - {crit_attack.max_damage}")
            crit_pct_min_damage = f"{crit_attack.min_damage / self.defending_mon.hp * 100:.2f}%"
            crit_pct_max_damage = f"{crit_attack.max_damage / self.defending_mon.hp * 100:.2f}%"
            self.crit_pct_damage_range.configure(text=f"{crit_pct_min_damage} - {crit_pct_max_damage}")

            kill_ranges = pkmn_damage_calc.find_kill(
                single_attack,
                crit_attack,
                pkmn_damage_calc.get_crit_rate(self.attacking_mon, move),
                self.defending_mon.hp
            )

            def format_message(kill_info):
                kill_pct = kill_info[1]
                if kill_pct == -1:
                    kill_pct = 100
                return f"{kill_info[0]}-hit kill: {kill_pct:.2f} %"
            
            max_num_messages = 3
            if len(kill_ranges) > max_num_messages:
                kill_ranges = kill_ranges[:max_num_messages - 1] + [kill_ranges[-1]]

            self.cur_guaranteed_kill = kill_ranges[-1][0]
            self.cur_max_roll = single_attack.max_damage

            kill_ranges = [format_message(x) for x in kill_ranges]

            self.kill_frame.configure(background=const.STAT_BG_COLOR)
            self.num_to_kill.configure(text="\n".join(kill_ranges), background=const.STAT_BG_COLOR)
