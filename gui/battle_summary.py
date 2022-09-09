import tkinter as tk
import datetime

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

        self._enemy_pkmn = None
        self._cur_state = None
        self._mon_pairs = []

        for idx in range(6):
            self._mon_pairs.append(MonPairSummary(self))
        
        self.error_message = tk.Label(self, text="Select a battle to see damage calculations")
        self.should_calculate = False
        self.set_team(None)
    
    def allow_calculations(self):
        # trigger calculations if they were paused before
        if not self.should_calculate:
            recalc = True
        self.should_calculate = True

        if recalc:
            self.set_team(self._enemy_pkmn, self._cur_state, recalc_only=True)

    def pause_calculations(self):
        self.should_calculate = False
        # wipe out the rendering when not calculating
        # but only recalc, so we still remember what the current state and enemy pkmn are
        self.set_team(None, cur_state=None, recalc_only=True)
    
    def set_team(self, enemy_pkmn, cur_state:route_state_objects.RouteState=None, recalc_only:bool=False):
        if enemy_pkmn is not None and enemy_pkmn == self._enemy_pkmn and cur_state == self._cur_state and not recalc_only:
            return

        if not recalc_only:
            self._enemy_pkmn = enemy_pkmn
            self._cur_state = cur_state

            if not self.should_calculate and enemy_pkmn is not None:
                # update the data, but don't actually update the UI or any elements unless we want to
                # since these calculations are actually expensive
                return
        
        time_start = datetime.datetime.now()
        if enemy_pkmn is None:
            enemy_pkmn = []
            self.error_message.grid(row=10, column=0)
        else:
            self.error_message.grid_forget()

        idx = -1
        for idx, cur_pkmn in enumerate(enemy_pkmn):
            self._mon_pairs[idx].set_mons(cur_state.solo_pkmn.get_pkmn_obj(cur_state.badges), cur_pkmn)
            self._mon_pairs[idx].grid(row=idx, column=0, sticky=tk.EW)
            
            # update so we account for mid-battle level ups
            cur_state, _ = cur_state.defeat_pkmn(cur_pkmn)
        
        for missing_idx in range(idx+1, 6):
            self._mon_pairs[missing_idx].grid_forget()

        if enemy_pkmn is not None:
            print(f"{datetime.datetime.now() - time_start}s to render battle")


class MonPairSummary(tk.Frame):
    def __init__(self, *args, font_size=None, **kwargs):
        super().__init__(*args, **kwargs, highlightbackground="black", highlightthickness=1)

        self.first_mon = None
        self.second_mon = None

        self.left_mon_label = tk.Label(self, text="", background=const.HEADER_BG_COLOR)
        self.left_mon_label.grid(row=0, column=0, columnspan=4, sticky=tk.EW, padx=2, pady=2)

        self.divider = tk.Frame(self, background=const.IMPORTANT_COLOR, width=4)
        self.divider.grid(row=0, column=4, rowspan=2, sticky=tk.NS)
        self.divider.grid_propagate(0)

        self.right_mon_label = tk.Label(self, text="", background=const.HEADER_BG_COLOR)
        self.right_mon_label.grid(row=0, column=5, columnspan=4, sticky=tk.EW, padx=2, pady=2)

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

        self.move_list = []
        for _ in range(8):
            self.move_list.append(DamageSummary(self))

    def set_mons(self, first_mon, second_mon):
        self.first_mon = first_mon
        self.second_mon = second_mon

        self.left_mon_label.configure(text=f"{self.first_mon} attacking {self.second_mon} ({self.second_mon.hp} HP)")
        self.right_mon_label.configure(text=f"{self.second_mon} attacking {self.first_mon} ({self.first_mon.hp} HP)")

        cur_best_attack_idx = None
        cur_best_guaranteed_kill = None
        cur_best_damage_roll = None

        # update all the moves for the first attacking the second
        idx = -1
        for idx in range(4):
            # first mon attacking second
            cur_move = None
            if idx < len(self.first_mon.move_list):
                cur_move = self.first_mon.move_list[idx]
            
            # doing this because the solo mon has all moves populated, just with empty values when not full
            if cur_move:
                self.move_list[idx].calc_damages(cur_move, self.first_mon, self.second_mon)
                self.move_list[idx].grid(row=1, column=idx, sticky=tk.NSEW)

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
            else:
                self.move_list[idx].grid_forget()
            
            # second mon attacking first
            cur_move = None
            if idx < len(self.second_mon.move_list):
                cur_move = self.second_mon.move_list[idx]

            if cur_move:
                self.move_list[idx + 4].calc_damages(cur_move, self.second_mon, self.first_mon)
                self.move_list[idx + 4].grid(row=1, column=(5 + idx), sticky=tk.NSEW)
            else:
                self.move_list[idx + 4].grid_forget()

        if cur_best_attack_idx is not None:
            self.move_list[cur_best_attack_idx].flag_as_best_move()


class DamageSummary(tk.Frame):
    def __init__(self, *args, font_size=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.cur_guaranteed_kill = None
        self.cur_max_roll = None

        self.config(padx=2, pady=2)
        self.columnconfigure(0, weight=1)

        self.row_idx = 0

        self.header = tk.Frame(self, background=const.MOVE_BG_COLOR)
        self.header.grid(row=self.row_idx, column=0, sticky=tk.NSEW)
        self.header.columnconfigure(0, weight=1)
        self.row_idx += 1

        self.move_name = tk.Label(self.header, background=const.MOVE_BG_COLOR)
        self.move_name.grid(row=0, column=0, columnspan=2)

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

    def calc_damages(
        self,
        move_name,
        attacking_mon:data_objects.EnemyPkmn,
        defending_mon:data_objects.EnemyPkmn,
    ):

        move = pkmn_db.move_db.get_move(move_name)
        if move is None:
            raise ValueError(f"Unknown move: {move_name}")
        self.move_name.configure(text=move_name)

        single_attack = pkmn_damage_calc.calculate_damage(attacking_mon, move, defending_mon)
        crit_attack = pkmn_damage_calc.calculate_damage(attacking_mon, move, defending_mon, is_crit=True)

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
            pct_min_damage = f"{single_attack.min_damage / defending_mon.hp * 100:.2f}%"
            pct_max_damage = f"{single_attack.max_damage / defending_mon.hp * 100:.2f}%"
            self.pct_damage_range.configure(text=f"{pct_min_damage} - {pct_max_damage}")

            self.crit_damage_range.configure(text=f"{crit_attack.min_damage} - {crit_attack.max_damage}")
            crit_pct_min_damage = f"{crit_attack.min_damage / defending_mon.hp * 100:.2f}%"
            crit_pct_max_damage = f"{crit_attack.max_damage / defending_mon.hp * 100:.2f}%"
            self.crit_pct_damage_range.configure(text=f"{crit_pct_min_damage} - {crit_pct_max_damage}")

            kill_ranges = pkmn_damage_calc.find_kill(
                single_attack,
                crit_attack,
                pkmn_damage_calc.get_crit_rate(attacking_mon, move),
                defending_mon.hp
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
