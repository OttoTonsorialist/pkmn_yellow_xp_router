import tkinter as tk
from tkinter import ttk
from typing import List
from dataclasses import dataclass
import logging

from controllers.main_controller import MainController
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


@dataclass
class SummaryInfo:
    trainer_name:str
    mon_level:int
    moves:List[str]

@dataclass
class RenderInfo:
    move_name:str
    move_type:str
    start_idx:int
    end_idx:int


class RouteSummaryWindow(tk.Toplevel):
    def __init__(self, main_window, controller:MainController, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._controller = controller
        self._cur_data = []
    
        self._main_frame = ttk.Frame(self)
        self._main_frame.pack(padx=2, pady=2)

        self._header_frames:List[ttk.Frame] = []
        self._move_frames:List[List[ttk.Frame]] = [[], [], [], []]
        self._labels:List[ttk.Label] = []

        self.bind(self._controller.register_route_change(self), self._refresh)
        self._refresh()
    
    def _refresh(self, *args, **kwargs):
        for to_remove in self._labels:
            to_remove.pack_forget()
        self._header_frames:List[ttk.Label] = []

        for to_remove in self._header_frames:
            to_remove.grid_forget()
        self._header_frames:List[ttk.Frame] = []

        for cur_move_slot in self._move_frames:
            for to_remove in cur_move_slot:
                to_remove.grid_forget()
        self._move_frames:List[List[ttk.Frame]] = [[], [], [], []]

        summary_list:List[SummaryInfo] = []
        cur_event = self._controller.get_next_event()
        while cur_event is not None:
            if cur_event.event_definition.trainer_def is not None and cur_event.event_definition.enabled:
                if (
                    cur_event.event_definition.is_highlighted() or
                    current_gen_info().is_major_fight(cur_event.event_definition.trainer_def.trainer_name)
                ):
                    summary_list.append(
                        SummaryInfo(
                            cur_event.event_definition.trainer_def.trainer_name,
                            cur_event.init_state.solo_pkmn.cur_level,
                            cur_event.init_state.solo_pkmn.move_list,
                        )
                    )
            
            cur_event = self._controller.get_next_event(cur_event.group_id)
        
        move_display_info:List[List[RenderInfo]] = [[], [], [], []]
        for cur_idx, cur_summary in enumerate(summary_list):
            header_frame = ttk.Frame(self._main_frame, width=130, height=60)
            header_frame.grid(row=0, column=cur_idx, padx=2, pady=2)
            header_frame.pack_propagate(0)

            trainer_label = ttk.Label(header_frame, text=cur_summary.trainer_name)
            trainer_label.pack(pady=2)
            self._labels.append(trainer_label)

            level_label = ttk.Label(header_frame, text=f"Lv: {cur_summary.mon_level}")
            level_label.pack(pady=2)
            self._labels.append(level_label)

            self._header_frames.append(header_frame)

            for move_idx in range(0, 4):
                next_move = ""
                if move_idx < len(cur_summary.moves):
                    next_move = cur_summary.moves[move_idx]
                    if next_move is None:
                        next_move = ""
                
                if (
                    len(move_display_info[move_idx]) == 0 or
                    move_display_info[move_idx][-1].move_name != next_move
                ):
                    if next_move == "":
                        move_type = ""
                    else:
                        move_type = current_gen_info().move_db().get_move(next_move).move_type

                    move_display_info[move_idx].append(RenderInfo(next_move, move_type, cur_idx, cur_idx))
                else:
                    move_display_info[move_idx][-1].end_idx = cur_idx
        
        for cur_move_idx, cur_slot_display in enumerate(move_display_info):
            for cur_move_info in cur_slot_display:
                cur_move_frame = ttk.Frame(self._main_frame)
                cur_move_frame.grid(
                    row=cur_move_idx + 1,
                    column=cur_move_info.start_idx,
                    columnspan=((cur_move_info.end_idx - cur_move_info.start_idx) + 1)
                )

                move_label = ttk.Label(cur_move_frame, text=cur_move_info.move_name)
                move_label.pack()
                self._labels.append(move_label)

