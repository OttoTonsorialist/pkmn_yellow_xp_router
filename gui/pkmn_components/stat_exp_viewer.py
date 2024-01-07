from tkinter import ttk
from typing import List, Tuple
import logging
from gui.pkmn_components.stat_column import StatColumn

from pkmn.gen_factory import current_gen_info
from pkmn import universal_data_objects
from routing import full_route_state

logger = logging.getLogger(__name__)

class StatExpViewer(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(height=150, width=250)
        self._net_gain_column:StatColumn = None
        self._realized_stat_xp_column:StatColumn = None
        self._total_stat_xp_column:StatColumn = None
        self._state = None
        self._stat_labels: List[str] = [] 
        self._cached_gen = None
        self._config_for_gen()

    def _config_for_gen(self) -> Tuple[List[str]]:
        cur_gen = current_gen_info().get_generation()
        if cur_gen == self._cached_gen:
            return

        self._cached_gen = cur_gen
        if cur_gen >= 2:
            new_labels = ["HP:", "Attack:", "Defense:", "Spc Atk:", "Spc Def:", "Speed:"]
        else:
            new_labels =["HP:", "Attack:", "Defense:", "Special:", "Speed:"]

        if cur_gen >= 3:
            gain_header = "Net Stats\nFrom EVs"
            realized_header = "Realized\nEVs"
            total_header = "Total\nEVs"
        else:
            gain_header = "Net Stats\nFrom StatExp"
            realized_header = "Realized\nStatExp"
            total_header = "Total\nStatExp"
        
        self._stat_labels = new_labels
        
        if self._net_gain_column is not None:
            self._net_gain_column.grid_forget()
        self._net_gain_column = StatColumn(self, num_rows=len(self._stat_labels), val_width=3, style_prefix="Header")
        self._net_gain_column.set_labels(self._stat_labels)
        self._net_gain_column.set_header(gain_header)
        self._net_gain_column.grid(row=0, column=0)

        if self._realized_stat_xp_column is not None:
            self._realized_stat_xp_column.grid_forget()
        self._realized_stat_xp_column = StatColumn(self, num_rows=len(self._stat_labels), val_width=5, style_prefix="Secondary")
        self._realized_stat_xp_column.set_labels(self._stat_labels)
        self._realized_stat_xp_column.set_header(realized_header)
        self._realized_stat_xp_column.grid(row=0, column=1)

        if self._total_stat_xp_column is not None:
            self._total_stat_xp_column.grid_forget()
        self._total_stat_xp_column = StatColumn(self, num_rows=len(self._stat_labels), val_width=5)
        self._total_stat_xp_column.set_labels(self._stat_labels)
        self._total_stat_xp_column.set_header(total_header)
        self._total_stat_xp_column.grid(row=0, column=2)

    def _vals_from_stat_block(self, stat_block:universal_data_objects.StatBlock):
        if current_gen_info().get_generation() >= 2:
            return [stat_block.hp, stat_block.attack, stat_block.defense, stat_block.special_attack, stat_block.special_defense, stat_block.speed]
        else:
            return [stat_block.hp, stat_block.attack, stat_block.defense, stat_block.special_attack, stat_block.speed]

    def set_state(self, state:full_route_state.RouteState):
        self._config_for_gen()
        self._state = state

        self._net_gain_column.set_values(
            self._vals_from_stat_block(
                self._state.solo_pkmn.get_net_gain_from_stat_xp(self._state.badges)
            )
        )
        self._realized_stat_xp_column.set_values(
            self._vals_from_stat_block(
                self._state.solo_pkmn.realized_stat_xp
            )
        )
        self._total_stat_xp_column.set_values(
            self._vals_from_stat_block(
                self._state.solo_pkmn.unrealized_stat_xp
            )
        )