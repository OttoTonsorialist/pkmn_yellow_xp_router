import tkinter as tk
from tkinter import ttk
from typing import List
from dataclasses import dataclass
import logging

from controllers.main_controller import MainController
from pkmn.gen_factory import current_gen_info
from utils.constants import const
from utils import tk_utils

logger = logging.getLogger(__name__)


@dataclass
class SummaryInfo:
    trainer_name:str
    mon_level:int
    held_item:str
    moves:List[str]
    rare_candy_count:int

@dataclass
class RenderInfo:
    move_name:str
    move_type:str
    start_idx:int
    end_idx:int


class RouteSummaryWindow(tk.Toplevel):
    def __init__(self, main_window, controller:MainController, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)

        self._top_menu_bar = tk.Menu(self)
        self._top_menu_bar.add_command(label="Export Screenshot (Ctrl+P)", accelerator="Ctrl+P", command=self._export_screen_shot)
        self.config(menu=self._top_menu_bar)

        self._controller = controller
        self._cur_data = []
    
        self._main_frame = ttk.Frame(self)
        self._main_frame.pack(padx=2, pady=2)

        self._header_frames:List[ttk.Frame] = []
        self._held_item_frames:List[ttk.Frame] = []
        self._move_frames:List[List[ttk.Frame]] = [[], [], [], []]
        self._labels:List[ttk.Label] = []

        self._row_idx_header = 0
        self._row_idx_held_item = 1
        self._row_idx_moves_init = 2

        self.bind(self._controller.register_route_change(self), self._refresh)
        self.bind('<Control-p>', self._export_screen_shot)
        self._refresh()
    
    def _export_screen_shot(self, *args, **kwargs):
        self._controller.take_screenshot("run_summary", tk_utils.get_bounding_box(self))
    
    def _refresh(self, *args, **kwargs):
        for to_remove in self._labels:
            to_remove.pack_forget()
        self._labels:List[ttk.Label] = []

        for to_remove in self._header_frames:
            to_remove.grid_forget()
        self._header_frames:List[ttk.Frame] = []

        for to_remove in self._held_item_frames:
            to_remove.grid_forget()
        self._held_item_frames:List[ttk.Frame] = []

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
                            cur_event.init_state.solo_pkmn.held_item,
                            cur_event.init_state.solo_pkmn.move_list,
                            0,
                        )
                    )
            elif cur_event.event_definition.rare_candy is not None and cur_event.event_definition.enabled:
                summary_list.append(
                    SummaryInfo(
                        "",
                        cur_event.final_state.solo_pkmn.cur_level,
                        cur_event.final_state.solo_pkmn.held_item,
                        cur_event.final_state.solo_pkmn.move_list,
                        rare_candy_count=cur_event.event_definition.rare_candy.amount,
                    )
                )
            
            cur_event = self._controller.get_next_event(cur_event.group_id)
        
        if len(summary_list) == 0:
            header_frame = ttk.Frame(self._main_frame, style="SummaryHeader.TFrame")
            header_frame.grid(row=0, column=0, padx=2, pady=2, sticky=tk.NSEW)
            self._header_frames.append(header_frame)

            trainer_label = ttk.Label(header_frame, text="No major fights in route. Please add major fights or highlight other fights to see summary", style="SummaryHeader.TLabel", justify="center")
            trainer_label.pack(pady=15, padx=15)
            self._labels.append(trainer_label)
            return


        move_display_info:List[List[RenderInfo]] = [[], [], [], []]
        held_item_display_info:List[RenderInfo] = []
        for cur_idx, cur_summary in enumerate(summary_list):

            if cur_summary.rare_candy_count == 0:
                header_style = "SummaryHeader.TFrame"
                label_style = "SummaryHeader.TLabel"

                split_name = cur_summary.trainer_name.split(" ")
                if len(split_name) > 2:
                    first_line = " ".join(split_name[0:2])
                    second_line = " ".join(split_name[2:])
                    trainer_text = first_line + "\n" + second_line
                elif len(split_name) == 2 and len(split_name[1]) > 1:
                    trainer_text = split_name[0] + "\n" + split_name[1]
                else:
                    trainer_text = cur_summary.trainer_name

            else:
                header_style = "SummaryHeaderCandy.TFrame"
                label_style = "SummaryHeaderCandy.TLabel"
                trainer_text = f"Rare Candy x{cur_summary.rare_candy_count}"

            header_frame = ttk.Frame(self._main_frame, style=header_style)
            header_frame.grid(row=0, column=cur_idx, padx=2, pady=2, sticky=tk.NSEW)

            trainer_label = ttk.Label(header_frame, text=trainer_text, style=label_style, justify="center")
            trainer_label.pack(pady=(15, 2), padx=5)
            self._labels.append(trainer_label)

            level_label = ttk.Label(header_frame, text=f"Lv: {cur_summary.mon_level}", style=label_style)
            level_label.pack(pady=(2, 15), padx=5, side="bottom")

            self._labels.append(level_label)
            self._header_frames.append(header_frame)

            if len(held_item_display_info) == 0 or held_item_display_info[-1].move_name != cur_summary.held_item:
                held_item_display_info.append(RenderInfo(cur_summary.held_item, None, cur_idx, cur_idx))
            else:
                held_item_display_info[-1].end_idx = cur_idx

            for move_idx in range(0, 4):
                next_move = ""
                if move_idx < len(cur_summary.moves):
                    next_move = cur_summary.moves[move_idx]
                    if next_move is None:
                        next_move = ""

                if next_move == "":
                    move_type = ""
                elif next_move == const.HIDDEN_POWER_MOVE_NAME:
                    move_type = current_gen_info().get_hidden_power(self._controller.get_dvs())[0]
                    next_move = f"{next_move} ({move_type})"
                else:
                    move_type = current_gen_info().move_db().get_move(next_move).move_type
                
                if (
                    len(move_display_info[move_idx]) == 0 or
                    move_display_info[move_idx][-1].move_name != next_move
                ):
                    move_display_info[move_idx].append(RenderInfo(next_move, move_type, cur_idx, cur_idx))
                else:
                    move_display_info[move_idx][-1].end_idx = cur_idx
        
        if current_gen_info().get_generation() != 1:
            for cur_held_item_display in held_item_display_info:
                cur_held_item_frame = ttk.Frame(self._main_frame, style="SummaryHeader.TFrame")
                cur_held_item_frame.grid(
                    row=self._row_idx_held_item,
                    column=cur_held_item_display.start_idx,
                    columnspan=((cur_held_item_display.end_idx - cur_held_item_display.start_idx) + 1),
                    sticky=tk.NSEW,
                    padx=2, pady=2
                )
                self._held_item_frames.append(cur_held_item_frame)

                display_text = cur_held_item_display.move_name
                if not display_text:
                    display_text = "None"
                held_label = ttk.Label(cur_held_item_frame, text=display_text, style=f"SummaryHeader.TLabel")
                held_label.pack()
                self._labels.append(held_label)
        
        for cur_move_idx, cur_slot_display in enumerate(move_display_info):
            for cur_move_info in cur_slot_display:
                cur_move_frame = ttk.Frame(self._main_frame, style=f"{cur_move_info.move_type}Type.TFrame")
                cur_move_frame.grid(
                    row=self._row_idx_moves_init + cur_move_idx,
                    column=cur_move_info.start_idx,
                    columnspan=((cur_move_info.end_idx - cur_move_info.start_idx) + 1),
                    sticky=tk.NSEW,
                    padx=2, pady=2
                )
                self._move_frames[cur_move_idx].append(cur_move_frame)

                move_label = ttk.Label(cur_move_frame, text=cur_move_info.move_name, style=f"{cur_move_info.move_type}Type.TLabel")
                move_label.pack()
                self._labels.append(move_label)

