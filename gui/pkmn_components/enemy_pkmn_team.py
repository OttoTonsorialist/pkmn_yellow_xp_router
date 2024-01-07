from tkinter import ttk
from typing import List
import logging
from gui.pkmn_components.pkmn_viewer import PkmnViewer

from pkmn import universal_data_objects
from routing import full_route_state

logger = logging.getLogger(__name__)



class EnemyPkmnTeam(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._all_pkmn:List[PkmnViewer] = []

        self._all_pkmn.append(PkmnViewer(self, font_size=10))
        self._all_pkmn.append(PkmnViewer(self, font_size=10))
        self._all_pkmn.append(PkmnViewer(self, font_size=10))
        self._all_pkmn.append(PkmnViewer(self, font_size=10))
        self._all_pkmn.append(PkmnViewer(self, font_size=10))
        self._all_pkmn.append(PkmnViewer(self, font_size=10))

    def set_team(self, enemy_pkmn:List[universal_data_objects.EnemyPkmn], cur_state:full_route_state.RouteState=None):
        if enemy_pkmn is None:
            enemy_pkmn = []

        idx = -1
        for idx, cur_pkmn in enumerate(enemy_pkmn):
            if cur_state is not None:
                if cur_state.solo_pkmn.cur_stats.speed > cur_pkmn.cur_stats.speed:
                    speed_style = "Success"
                elif cur_state.solo_pkmn.cur_stats.speed == cur_pkmn.cur_stats.speed:
                    speed_style = "Warning"
                else:
                    speed_style = "Failure"
                cur_state = cur_state.defeat_pkmn(cur_pkmn)[0]
            else:
                speed_style = "Contrast"

            self._all_pkmn[idx].set_pkmn(cur_pkmn, speed_style=speed_style)
            self._all_pkmn[idx].grid(row=idx//3,column=idx%3, padx=5, pady=(5, 10))
        
        for missing_idx in range(idx+1, 6):
            self._all_pkmn[missing_idx].grid_forget()