import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font
from typing import Dict, List
import logging
from controllers.battle_summary_controller import BattleSummaryController, MoveRenderInfo

from gui import custom_components
from gui.popups.battle_config_popup import BattleConfigWindow
from pkmn import damage_calc, universal_data_objects
from routing import full_route_state
from routing import route_events
from utils.config_manager import config
from utils.constants import const
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


class BattleSummary(ttk.Frame):
    def __init__(self, controller:BattleSummaryController, *args, **kwargs):
        self._controller = controller
        super().__init__(*args, **kwargs)

        self.columnconfigure(0, weight=1)

        # these are matched lists, with the solo mon being updated for each enemy pkmn, in case of level-ups
        self._enemy_pkmn:List[universal_data_objects.EnemyPkmn] = None
        self._solo_pkmn:List[universal_data_objects.EnemyPkmn] = None
        self._source_state:full_route_state.RouteState = None
        self._source_event_group:route_events.EventGroup = None
        self._player_stage_modifiers:universal_data_objects.StageModifiers = universal_data_objects.StageModifiers()
        self._enemy_stage_modifiers:universal_data_objects.StageModifiers = universal_data_objects.StageModifiers()
        self._mimic_selection = ""
        self._custom_move_data = None

        self._top_bar = ttk.Frame(self)
        self._top_bar.grid(row=0, column=0, sticky=tk.EW)

        self._setup_half = ttk.Frame(self._top_bar)
        self._setup_half.grid(row=0, column=0, sticky=tk.EW)
        self._weather_half = ttk.Frame(self._top_bar)
        self._weather_half.grid(row=0, column=1, sticky=tk.EW)

        self._top_bar.columnconfigure(0, weight=1)

        self.setup_moves = SetupMovesSummary(self._setup_half, callback=self._player_setup_move_callback)
        self.setup_moves.grid(row=0, column=0, sticky=tk.EW, pady=(0, 2))

        self.enemy_setup_moves = SetupMovesSummary(self._setup_half, callback=self._enemy_setup_move_callback, is_player=False)
        self.enemy_setup_moves.grid(row=1, column=0, sticky=tk.EW)

        self.config_button = custom_components.SimpleButton(self._weather_half, text="Configure/Help", command=self._launch_config_popup)
        self.config_button.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=(0, 2))

        self.double_label = ttk.Label(self._weather_half, text="Single Battle")
        self.double_label.grid(row=1, column=0, sticky=tk.EW, padx=10, pady=(0, 2))

        self.weather_status = WeatherSummary(self._weather_half, callback=self._weather_callback)
        self.weather_status.grid(row=0, column=1, sticky=tk.EW, padx=2, pady=(0, 2))

        self.candy_summary = PrefightCandySummary(self._weather_half, callback=self._candy_callback)
        self.candy_summary.grid(row=1, column=1, sticky=tk.EW, padx=2, pady=(0, 2))

        self._mon_pairs:List[MonPairSummary] = []

        for idx in range(6):
            self._mon_pairs.append(MonPairSummary(self._controller, idx, self))
        
        self.error_message = tk.Label(self, text="Select a battle to see damage calculations")
        self.should_render = False
        self.bind(self._controller.register_refresh(self), self._on_full_refresh)
        self.set_team(None)
    
    def configure_weather(self, possible_weather_vals):
        self.weather_status.configure_weather(possible_weather_vals)

    def configure_setup_moves(self, possible_setup_moves):
        self.setup_moves.configure_moves(possible_setup_moves)
        self.enemy_setup_moves.configure_moves(possible_setup_moves)
    
    def hide_contents(self):
        self.should_render = False
        for cur_mon_pair in self._mon_pairs:
            cur_mon_pair.grid_forget()
    
    def show_contents(self):
        self.should_render = True
        self._on_full_refresh()
    
    def _launch_config_popup(self, *args, **kwargs):
        BattleConfigWindow(self.winfo_toplevel(), battle_controller=self._controller)
    
    def _weather_callback(self, *args, **kwargs):
        self._controller.update_weather(self.weather_status.get_weather())
        
    def _candy_callback(self, *args, **kwargs):
        self._controller.update_prefight_candies(self.candy_summary.get_prefight_candy_count())
        
    def _player_setup_move_callback(self, *args, **kwargs):
        self._controller.update_player_setup_moves(self.setup_moves._move_list.copy())

    def _enemy_setup_move_callback(self, *args, **kwargs):
        self._controller.update_enemy_setup_moves(self.enemy_setup_moves._move_list.copy())
    
    def set_team(
        self,
        enemy_pkmn:List[universal_data_objects.EnemyPkmn],
        cur_state:full_route_state.RouteState=None,
        event_group:route_events.EventGroup=None,
    ):
        if event_group is not None:
            self._controller.load_from_event(event_group)
        elif cur_state is not None and enemy_pkmn is not None:
            self._controller.load_from_state(cur_state, enemy_pkmn)
        else:
            self._controller.load_empty()

    def _on_full_refresh(self, *args, **kwargs):
        if not self.should_render:
            return

        self.candy_summary.set_candy_count(self._controller.get_prefight_candy_count())
        if not self._controller.can_support_prefight_candies():
            self.candy_summary.disable()
        else:
            self.candy_summary.enable()

        if self._controller.is_double_battle():
            self.double_label.configure(text="Double Battle")
        else:
            self.double_label.configure(text="Single Battle")

        self.weather_status.set_weather(self._controller.get_weather())
        self.setup_moves.set_move_list(self._controller.get_player_setup_moves())
        self.enemy_setup_moves.set_move_list(self._controller.get_enemy_setup_moves())
        for idx in range(6):
            player_info = self._controller.get_pkmn_info(idx, True)
            enemy_info = self._controller.get_pkmn_info(idx, False)

            if player_info is None and enemy_info is None:
                self._mon_pairs[idx].grid_forget()
                if idx == 0:
                    pass
            
            else:
                self._mon_pairs[idx].grid(row=idx + 2, column=0, sticky=tk.EW)
                self._mon_pairs[idx].update_rendering()


class SetupMovesSummary(ttk.Frame):
    def __init__(self, *args, callback=None, is_player=True, **kwargs):
        super().__init__(*args, **kwargs)

        self._callback = callback
        self._move_list = []

        self.reset_button = custom_components.SimpleButton(self, text="Reset Setup", command=self._reset)
        self.reset_button.grid(row=0, column=0, padx=2)

        self.setup_label = ttk.Label(self, text="Move:")
        self.setup_label.grid(row=0, column=1, padx=2)

        self.setup_moves = custom_components.SimpleOptionMenu(self, ["N/A"])
        self.setup_moves.grid(row=0, column=2, padx=2)

        self.add_button = custom_components.SimpleButton(self, text="Apply Move", command=self._add_setup_move)
        self.add_button.grid(row=0, column=3, padx=2)

        if is_player:
            label_text = "Player Setup:"
        else:
            label_text = "Enemy Setup:"
        self.extra_label = ttk.Label(self, text=label_text)
        self.extra_label.grid(row=0, column=4, padx=2)

        self.move_list_label = ttk.Label(self)
        self.move_list_label.grid(row=0, column=5, padx=2)
    
    def _reset(self, *args, **kwargs):
        self._move_list = []
        self._move_list_updated()
    
    def _add_setup_move(self, *args, **kwargs):
        self._move_list.append(self.setup_moves.get())
        self._move_list_updated()
    
    def configure_moves(self, new_moves):
        self.setup_moves.new_values(new_moves)
    
    def set_move_list(self, new_moves, trigger_update=False):
        self._move_list = new_moves
        self._move_list_updated(trigger_update=trigger_update)
    
    def get_stage_modifiers(self):
        result = universal_data_objects.StageModifiers()

        for cur_move in self._move_list:
            result = result.apply_stat_mod(current_gen_info().move_db().get_stat_mod(cur_move))
        
        return result
    
    def _move_list_updated(self, trigger_update=True):
        to_display = ", ".join(self._move_list)
        if not to_display:
            to_display = "None"

        self.move_list_label.configure(text=to_display)
        if self._callback is not None and trigger_update:
            self._callback()


class WeatherSummary(ttk.Frame):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._outer_callback = callback
        self._loading = False

        self.label = ttk.Label(self, text="Weather:")
        self.label.grid(row=0, column=0, padx=2)

        self.weather_dropdown = custom_components.SimpleOptionMenu(self, [const.WEATHER_NONE], callback=self._callback)
        self.weather_dropdown.grid(row=0, column=1, padx=2)
    
    def _callback(self, *args, **kwargs):
        if self._loading:
            return
        
        if self._outer_callback is not None:
            self._outer_callback()
    
    def set_weather(self, new_weather):
        self._loading = True
        self.weather_dropdown.set(new_weather)
        self._loading = False
    
    def configure_weather(self, weather_vals):
        self.weather_dropdown.new_values(weather_vals)
    
    def get_weather(self):
        return self.weather_dropdown.get()


class PrefightCandySummary(ttk.Frame):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._outer_callback = callback
        self._loading = False

        self.label = ttk.Label(self, text="Prefight Candies:")
        self.label.grid(row=0, column=0, padx=2)

        self.candy_count = custom_components.AmountEntry(self, min_val=0, init_val=0, callback=self._callback, width=5)
        self.candy_count.grid(row=0, column=1, padx=2)
    
    def _callback(self, *args, **kwargs):
        if self._loading:
            return
        
        if self._outer_callback is not None:
            self._outer_callback()
    
    def set_candy_count(self, new_amount):
        self._loading = True
        self.candy_count.set(new_amount)
        self._loading = False
    
    def get_prefight_candy_count(self):
        try:
            return int(self.candy_count.get())
        except Exception:
            return 0
    
    def disable(self):
        self.candy_count.disable()
    
    def enable(self):
        self.candy_count.enable()


class MonPairSummary(ttk.Frame):
    def __init__(self, controller:BattleSummaryController, mon_idx, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._controller = controller
        self._mon_idx = mon_idx

        bold_font = tkinter.font.nametofont("TkDefaultFont").copy()
        bold_font.configure(weight="bold")

        self.left_mon_label_frame = ttk.Frame(self, style="Header.TFrame")
        self.left_mon_label_frame.grid(row=0, column=0, columnspan=4, sticky=tk.EW, padx=2, pady=2)

        self.left_label = ttk.Label(self.left_mon_label_frame, text="", style="Header.TLabel")
        self.left_label.grid(row=0, column=1)

        self.left_mon_label_frame.columnconfigure(0, weight=1, uniform="left_col_group")
        self.left_mon_label_frame.columnconfigure(2, weight=1, uniform="left_col_group")

        self.divider = ttk.Frame(self, width=4, style="Divider.TFrame")
        self.divider.grid(row=0, column=4, rowspan=2, sticky=tk.NS)
        self.divider.grid_propagate(0)

        self.right_mon_label_frame = ttk.Frame(self, style="Header.TFrame")
        self.right_mon_label_frame.grid(row=0, column=5, columnspan=4, sticky=tk.EW, padx=2, pady=2)

        self.right_label = ttk.Label(self.right_mon_label_frame, text="", style="Header.TLabel")
        self.right_label.grid(row=0, column=1)

        self.right_mon_label_frame.columnconfigure(0, weight=1, uniform="right_col_group")
        self.right_mon_label_frame.columnconfigure(2, weight=1, uniform="right_col_group")

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
        for cur_idx in range(8):
            self.move_list.append(DamageSummary(self._controller, self._mon_idx, cur_idx % 4, cur_idx < 4, self))
    
    def update_rendering(self):
        player_rendering_info = self._controller.get_pkmn_info(self._mon_idx, True)
        enemy_rendering_info = self._controller.get_pkmn_info(self._mon_idx, False)

        self.left_label.configure(text=f"{player_rendering_info}")
        self.right_label.configure(text=f"{enemy_rendering_info}")

        for cur_idx, cur_move in enumerate(self.move_list):
            column_idx = cur_idx
            if column_idx >= 4:
                column_idx += 1

            if self._controller.get_move_info(cur_move._mon_idx, cur_move._move_idx, cur_move._is_player_mon) is not None:
                cur_move.grid(row=1, column=column_idx, sticky=tk.NSEW)
            else:
                cur_move.grid_forget()

            cur_move.update_rendering()


class DamageSummary(ttk.Frame):
    def __init__(self, controller:BattleSummaryController, mon_idx, move_idx, is_player_mon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._controller = controller
        self._mon_idx = mon_idx
        self._move_idx = move_idx
        self._is_player_mon = is_player_mon
        self._move_name = None
        self._is_loading = False

        self.columnconfigure(0, weight=1)

        self.padx = 2
        self.pady = 0
        self.row_idx = 0

        self.header = ttk.Frame(self, style="Primary.TFrame")
        self.header.grid(row=self.row_idx, column=0, sticky=tk.NSEW, padx=self.padx, pady=self.pady)
        self.header.columnconfigure(0, weight=1)
        self.row_idx += 1

        self.move_name_label = ttk.Label(self.header, style="BattleMovePrimary.TLabel")
        self.custom_data_dropdown = custom_components.SimpleOptionMenu(self.header, [""], callback=self._custom_data_callback, width=14)

        self.range_frame = ttk.Frame(self, style="Contrast.TFrame")
        self.range_frame.grid(row=self.row_idx, column=0, sticky=tk.NSEW, padx=self.padx, pady=self.pady)
        self.range_frame.columnconfigure(0, weight=1)
        self.row_idx += 1

        self.damage_range = ttk.Label(self.range_frame, style="Contrast.TLabel")
        self.damage_range.grid(row=0, column=0, sticky=tk.W)
        self.pct_damage_range = ttk.Label(self.range_frame, style="Contrast.TLabel")
        self.pct_damage_range.grid(row=0, column=1, sticky=tk.E)
        self.crit_damage_range = ttk.Label(self.range_frame, style="Contrast.TLabel")
        self.crit_damage_range.grid(row=1, column=0, sticky=tk.W)
        self.crit_pct_damage_range = ttk.Label(self.range_frame, style="Contrast.TLabel")
        self.crit_pct_damage_range.grid(row=1, column=1, sticky=tk.E)

        self.kill_frame = ttk.Frame(self, style="Secondary.TFrame")
        self.kill_frame.grid(row=self.row_idx, column=0, sticky=tk.NSEW, padx=self.padx, pady=self.pady)
        self.rowconfigure(self.row_idx, weight=1)
        self.row_idx += 1

        self.num_to_kill = ttk.Label(self.kill_frame, justify=tk.LEFT, style="Secondary.TLabel")
        self.num_to_kill.grid(row=0, column=0, sticky=tk.NSEW)
    
    def flag_as_best_move(self):
        if self._is_player_mon:
            style = "Success"
        else:
            style = "Failure"

        self.kill_frame.configure(style=f"{style}.TFrame")
        self.num_to_kill.configure(style=f"{style}.TLabel")

    def unflag_as_best_move(self):
        self.kill_frame.configure(style="Secondary.TFrame")
        self.num_to_kill.configure(style="Secondary.TLabel")
    
    def _custom_data_callback(self, *args, **kwargs):
        if self._is_loading:
            return
        if self._move_name == const.MIMIC_MOVE_NAME:
            self._controller.update_mimic_selection(self.custom_data_dropdown.get())
        else:
            self._controller.update_custom_move_data(self._mon_idx, self._move_idx, self._is_player_mon, self.custom_data_dropdown.get())

    @staticmethod
    def format_message(kill_info):
        kill_pct = kill_info[1]
        if kill_pct == -1:
            if config.do_ignore_accuracy():
                return f"{kill_info[0]}-hit kill: 100 %"
            else:
                return f"{kill_info[0]}-hit kill, IGNORING ACC"

        if round(kill_pct, 1) == int(kill_pct):
            rendered_kill_pct = f"{kill_pct:02}"
        else:
            rendered_kill_pct = f"{kill_pct:.1f}"
        if config.do_ignore_accuracy():
            return f"{kill_info[0]}-hit kill: {rendered_kill_pct} %"
        return f"{kill_info[0]}-turn kill: {rendered_kill_pct} %"

    def update_rendering(self):
        move = self._controller.get_move_info(self._mon_idx, self._move_idx, self._is_player_mon)
        self._move_name = None if move is None else move.name

        self._is_loading = True
        if move is None or not move.is_best_move:
            self.unflag_as_best_move()
        else:
            self.flag_as_best_move()
        
        custom_data_options = None
        custom_data_selection = None
        if move is not None:
            custom_data_options = move.custom_data_options
            custom_data_selection = move.custom_data_selection
        if self._move_name == const.MIMIC_MOVE_NAME:
            custom_data_options = move.mimic_options
            custom_data_selection = move.mimic_data

        if custom_data_options:
            self.move_name_label.grid_forget()
            self.move_name_label.grid(row=0, column=0)
            self.custom_data_dropdown.grid(row=0, column=1)
            self.custom_data_dropdown.new_values(custom_data_options, default_val=custom_data_selection)
        else:
            self.move_name_label.grid_forget()
            self.move_name_label.grid(row=0, column=0, columnspan=2)
            self.custom_data_dropdown.grid_forget()


        if move is None:
            self.move_name_label.configure(text="")
            self.damage_range.configure(text="")
            self.pct_damage_range.configure(text="")
            self.crit_damage_range.configure(text="")
            self.crit_pct_damage_range.configure(text="")
        else:
            self.move_name_label.configure(text=f"{move.name}")
            if move.damage_ranges is None:
                self.damage_range.configure(text="")
                self.pct_damage_range.configure(text="")
                self.crit_damage_range.configure(text="")
                self.crit_pct_damage_range.configure(text="")
            
            else:
                self.damage_range.configure(text=f"{move.damage_ranges.min_damage} - {move.damage_ranges.max_damage}")
                pct_min_damage = f"{round(move.damage_ranges.min_damage / move.defending_mon_hp * 100)}%"
                pct_max_damage = f"{round(move.damage_ranges.max_damage / move.defending_mon_hp * 100)}%"
                self.pct_damage_range.configure(text=f"{pct_min_damage} - {pct_max_damage}")

                self.crit_damage_range.configure(text=f"{move.crit_damage_ranges.min_damage} - {move.crit_damage_ranges.max_damage}")
                crit_pct_min_damage = f"{round(move.crit_damage_ranges.min_damage / move.defending_mon_hp * 100)}%"
                crit_pct_max_damage = f"{round(move.crit_damage_ranges.max_damage / move.defending_mon_hp * 100)}%"
                self.crit_pct_damage_range.configure(text=f"{crit_pct_min_damage} - {crit_pct_max_damage}")

            
            max_num_messages = 3
            kill_ranges = move.kill_ranges
            if len(kill_ranges) > max_num_messages:
                kill_ranges = kill_ranges[:max_num_messages - 1] + [kill_ranges[-1]]

            kill_ranges = [self.format_message(x) for x in kill_ranges]
            self.num_to_kill.configure(text="\n".join(kill_ranges))

        self._is_loading = False
