from tkinter import ttk
import logging
from typing import List

from gui import custom_components
from gui.pkmn_components.pkmn_viewer import PkmnViewer
from pkmn.gen_factory import current_gen_info
from pkmn import universal_data_objects
from routing import full_route_state

logger = logging.getLogger(__name__)



class BadgeBoostViewer(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._info_frame = ttk.Frame(self)
        self._info_frame.grid(row=0, column=0)

        self._move_selector_label = ttk.Label(self._info_frame, text="Setup Move: ")
        self._move_selector = custom_components.SimpleOptionMenu(self._info_frame, ["N/A"], callback=self._move_selected_callback)
        self._move_selector_label.pack()
        self._move_selector.pack()

        self._badge_summary = ttk.Label(self._info_frame)
        self._badge_summary.pack(pady=10)

        self._state:full_route_state.RouteState = None

        # 6 possible badge boosts from a single setup move, plus unmodified summary
        NUM_SUMMARIES = 7
        NUM_COLS = 4
        self._frames:List[ttk.Frame] = []
        self._labels:List[ttk.Label] = []
        self._viewers:List[PkmnViewer] = []

        for idx in range(NUM_SUMMARIES):
            cur_frame = ttk.Frame(self)
            # add 1 because the 0th frame is the info frame
            cur_frame.grid(row=((idx + 1) // NUM_COLS), column=((idx + 1) % NUM_COLS), padx=3, pady=3)

            self._frames.append(cur_frame)
            self._labels.append(ttk.Label(cur_frame))
            self._viewers.append(PkmnViewer(cur_frame, stats_only=True))
    
    def _clear_all_summaries(self):
        # intentionally skip base stat frame
        for idx in range(1, len(self._frames)):
            self._labels[idx].pack_forget()
            self._viewers[idx].pack_forget()
    
    def _update_base_summary(self):
        if self._state is None:
            self._labels[0].pack_forget()
            self._viewers[0].pack_forget()
            return

        self._labels[0].configure(text=f"Base: {self._state.solo_pkmn.name}")
        self._labels[0].pack()

        self._viewers[0].set_pkmn(self._state.solo_pkmn.get_pkmn_obj(self._state.badges), badges=self._state.badges)
        self._viewers[0].pack(padx=3, pady=3)
    
    def _move_selected_callback(self, *args, **kwargs):
        self._update_base_summary()

        move = self._move_selector.get()
        if not move:
            self._clear_all_summaries()
            return
        
        prev_mod = universal_data_objects.StageModifiers()
        stage_mod = None
        for idx in range(1, len(self._frames)):
            stage_mod = prev_mod.apply_stat_mod(current_gen_info().move_db().get_stat_mod(move))
            if stage_mod == prev_mod:
                self._labels[idx].pack_forget()
                self._viewers[idx].pack_forget()
                continue

            prev_mod = stage_mod

            self._labels[idx].configure(text=f"{idx}x {move}")
            self._labels[idx].pack()

            self._viewers[idx].set_pkmn(self._state.solo_pkmn.get_pkmn_obj(self._state.badges, stage_mod), badges=self._state.badges)
            self._viewers[idx].pack()

    
    def set_state(self, state:full_route_state.RouteState):
        self._state = state
        self._move_selector.new_values(current_gen_info().get_stat_modifer_moves())

        # when state changes, update the badge list label
        raw_badge_text = self._state.badges.to_string(verbose=False)
        final_badge_text = raw_badge_text.split(":")[0]
        badges = raw_badge_text.split(":")[1]

        if not badges.strip():
            final_badge_text += "\nNone"
        else:
            earned_badges = badges.split(',')
            badges = ""
            while len(earned_badges) > 0:
                if len(earned_badges) == 1:
                    badges += f"{earned_badges[0]}\n"
                    del earned_badges[0]
                else:
                    badges += f"{earned_badges[0]}, {earned_badges[1]}\n"
                    del earned_badges[0]
                    del earned_badges[0]

            final_badge_text += '\n' + badges.strip()

        self._badge_summary.config(text=final_badge_text)
        self._move_selected_callback()