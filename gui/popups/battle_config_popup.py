import os

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from controllers.battle_summary_controller import BattleSummaryController

from gui import custom_components
from gui.popups.base_popup import Popup
from utils.constants import const
from utils.config_manager import config
from utils import io_utils, auto_update

class BattleConfigWindow(Popup):
    def __init__(self, main_window, *args, battle_controller:BattleSummaryController = None,**kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._battle_controller = battle_controller
        self.padx = 5
        self.pady = 5

        self.damage_notes_frame = ttk.Frame(self)
        self.damage_notes_frame.pack(padx=self.padx, pady=(4 * self.pady, 2 * self.pady))

        self.damage_notes_title = tk.Label(self.damage_notes_frame, text="Battle calcs limitations and edge cases")
        self.damage_notes_title.grid(row=0, column=0, padx=self.padx, pady=(4 * self.pady, self.pady))
        self.damage_notes = tk.Label(self.damage_notes_frame, text="Possible kills with less than 0.1% chance are not reported.\nFor each move, a full search for kill percents is done, up to a certain # of turns (configurable below).\nUp to 3 ranges are reported: 2 fastest kills, if applicable. The number required for a guaranteed kill is always given as the last range\nFor weaker moves, the maximum number of HITS (assumes attack lands every time) needed to guarantee a kill are given instead\nWith respect to accuracy calculations, Gen 1 misses are ignored\nThe crit damage ranges for multi-hit moves in Gen 2 assume exactly one of the multi-hits crit\n")
        self.damage_notes.grid(row=1, column=0,padx=self.padx, pady=self.pady)

        self.input_frame = ttk.Frame(self)
        self.input_frame.pack(padx=self.padx, pady=(2 * self.pady))

        self.search_depth_label = ttk.Label(self.input_frame, text="Damage Calc Search Depth:")
        self.search_depth_label.grid(row=0, column=0, pady=self.pady, padx=self.padx)
        self.search_depth_val = custom_components.AmountEntry(self.input_frame, init_val=config.get_damage_search_depth(), callback=self._update_damage_search_depth, min_val=1, max_val=99)
        self.search_depth_val.grid(row=0, column=1, pady=self.pady, padx=self.padx)
        self.search_depth_details = ttk.Label(self.input_frame, text="\n# Of turns to search damage ranges to find kill %'s\nLarger gets more accurate guaranteed kills, but may take longer, especially on slower computers")
        self.search_depth_details.grid(row=1, column=0, columnspan=2, pady=self.pady, padx=self.padx)

        self.accuracy_label = custom_components.CheckboxLabel(self.input_frame, text="Ignore Accuracy in Kill Ranges:", toggle_command=self._toggle_accuracy, flip=True)
        self.accuracy_label.grid(row=11, column=0, columnspan=2, pady=self.pady, padx=self.padx)
        self.accuracy_label.set_checked(config.do_ignore_accuracy())

        self.player_strat_label = ttk.Label(self.input_frame, text="Player Highlight Strategy:")
        self.player_strat_label.grid(row=12, column=0, pady=self.pady, padx=self.padx)
        self.player_strat_val = custom_components.SimpleOptionMenu(self.input_frame, const.ALL_HIGHLIGHT_STRATS, default_val=config.get_player_highlight_strategy(), callback=self._update_player_strat)
        self.player_strat_val.grid(row=12, column=1, pady=self.pady, padx=self.padx)

        self.enemy_strat_label = ttk.Label(self.input_frame, text="Enemy Highlight Strategy:")
        self.enemy_strat_label.grid(row=13, column=0, pady=self.pady, padx=self.padx)
        self.enemy_strat_val = custom_components.SimpleOptionMenu(self.input_frame, const.ALL_HIGHLIGHT_STRATS, default_val=config.get_enemy_highlight_strategy(), callback=self._update_enemy_strat)
        self.enemy_strat_val.grid(row=13, column=1, pady=self.pady, padx=self.padx)

        self.consistent_threshold_label = ttk.Label(self.input_frame, text="Consistency Threshold:")
        self.consistent_threshold_label.grid(row=14, column=0, pady=self.pady, padx=self.padx)
        self.consistent_threshold_val = custom_components.AmountEntry(self.input_frame, init_val=config.get_consistent_threshold(), callback=self._update_consistent_threshold, min_val=1, max_val=99)
        self.consistent_threshold_val.grid(row=14, column=1, pady=self.pady, padx=self.padx)

        self.explanation_frame = ttk.Frame(self)
        self.explanation_frame.pack(padx=self.padx, pady=(4 * self.pady, 2 * self.pady))

        self.strat_header = tk.Label(self.explanation_frame, text="Highlighting Strategies")
        self.strat_header.grid(row=0, column=0, padx=self.padx, pady=(4 * self.pady, self.pady - 4))

        self.guaranteed_kill_title = tk.Label(self.explanation_frame, text="Guaranteed Kill")
        self.guaranteed_kill_title.grid(row=1, column=0, padx=self.padx, pady=(4 * self.pady, self.pady - 4))
        self.guaranteed_kill_explanation = tk.Label(self.explanation_frame, text="This will highlight the move that has the lowest number of turns for a 'guaranteed' kill.\n'Guaranteed' is if the move has a 99% chance or higher to kill.")
        self.guaranteed_kill_explanation.grid(row=2, column=0,padx=self.padx, pady=self.pady - 4)

        self.fastest_kill_title = tk.Label(self.explanation_frame, text="Fastest Kill")
        self.fastest_kill_title.grid(row=3, column=0, padx=self.padx, pady=(4 * self.pady, self.pady - 4))
        self.fastest_kill_explanation = tk.Label(self.explanation_frame, text="This will highlight the move that has the lowest number of turns for any possible kill.\nKills that have a less than 0.1% chance of occuring are ignored by the damage calcs, but if the move has at least a 1% chance of killing,\nit will be reported")
        self.fastest_kill_explanation.grid(row=4, column=0, padx=self.padx, pady=self.pady - 4)

        self.guaranteed_kill_title = tk.Label(self.explanation_frame, text="Consistent Kill")
        self.guaranteed_kill_title.grid(row=5, column=0, padx=self.padx, pady=(4 * self.pady, self.pady - 4))
        self.guaranteed_kill_explanation = tk.Label(self.explanation_frame, text="This will highlight the move that has the lowest number of turns for a kill that has at least a chance above the consistency threshold.\nThis can be configured to suit your preferences")
        self.guaranteed_kill_explanation.grid(row=6, column=0, padx=self.padx, pady=self.pady - 4)

        self.ties_explanation = tk.Label(self.explanation_frame, text="Regardless of the strategy, ties between moves with the same # of turns will be broken with successive checks for the following stats: Highest Accuracy, Punish 2 turn moves (dig/fly), Highest damage")
        self.ties_explanation.grid(row=7, column=0, padx=self.padx, pady=(4 * self.pady, self.pady - 4))

        self.hyper_beam_explanation = tk.Label(self.explanation_frame, text="Hyper Beam is also special cased to not be highlighted if it cannot kill with a single non-crit hit, due to the need to recharge")
        self.hyper_beam_explanation.grid(row=8, column=0, padx=self.padx, pady=(6 * self.pady, self.pady - 4))

        self.close_button = custom_components.SimpleButton(self, text="Close", command=self._final_cleanup)
        self.close_button.pack(padx=self.padx, pady=self.pady)

        self.bind('<Return>', self._final_cleanup)
        self.bind('<Escape>', self._final_cleanup)
    
    def _final_cleanup(self, *args, **kwargs):
        if self._battle_controller is not None:
            self._battle_controller._full_refresh()
        self.close()
    
    def _toggle_accuracy(self, *args, **kwargs):
        config.set_ignore_accuracy(self.accuracy_label.is_checked())
    
    def _update_player_strat(self, *args, **kwargs):
        config.set_player_highlight_strategy(self.player_strat_val.get())
    
    def _update_enemy_strat(self, *args, **kwargs):
        config.set_enemy_highlight_strategy(self.enemy_strat_val.get())
    
    def _update_consistent_threshold(self, *args, **kwargs):
        result = config.DEFAULT_CONSISTENT_THRESHOLD
        try:
            result = int(self.consistent_threshold_val.get())
        except Exception:
            pass

        config.set_consistent_threshold(result)

    def _update_damage_search_depth(self, *args, **kwargs):
        result = config.DEFAULT_DAMAGE_SEARCH_DEPTH
        try:
            result = int(self.search_depth_val.get())
        except Exception:
            pass

        config.set_damage_search_depth(result)
