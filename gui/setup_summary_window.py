import tkinter as tk
from tkinter import ttk
import logging

from controllers.main_controller import MainController
from pkmn.gen_factory import current_gen_info
from utils import tk_utils

logger = logging.getLogger(__name__)


class SetupSummaryWindow(tk.Toplevel):
    def __init__(self, main_window, controller:MainController, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)

        self._controller = controller
        self._cur_data = []
    
        self._main_frame = ttk.Frame(self)
        self._main_frame.pack(padx=15, pady=15)

        self._text = ttk.Label(self._main_frame)
        self._text.pack(padx=2, pady=2)

        self._row_idx_header = 0
        self._row_idx_held_item = 1
        self._row_idx_moves_init = 2

        self.bind(self._controller.register_route_change(self), self._refresh)
        self._refresh()
    
    def _export_screen_shot(self, *args, **kwargs):
        self._controller.take_screenshot("setup_summary", tk_utils.get_bounding_box(self))
    
    def _refresh(self, *args, **kwargs):
        moves_used = []

        cur_event = self._controller.get_next_event()
        while cur_event is not None:
            if (
                cur_event.event_definition.trainer_def is not None and
                cur_event.event_definition.enabled and 
                (
                    cur_event.event_definition.is_highlighted() or
                    current_gen_info().is_major_fight(cur_event.event_definition.trainer_def.trainer_name)
                ) and
                cur_event.event_definition.trainer_def.setup_moves
            ):
                cur_setup_moves = {}
                for sm in cur_event.event_definition.trainer_def.setup_moves:
                    cur_setup_moves[sm] = cur_setup_moves.get(sm, 0) + 1
                setup_moves_text = [f"x{count} {sm}" for sm, count in cur_setup_moves.items()]

                moves_used.append(
                    f"{cur_event.event_definition.get_label()}: {','.join(setup_moves_text)}"
                )

            cur_event = self._controller.get_next_event(cur_event.group_id)

        if moves_used:
            final_text = "\n".join(["Setup Moves:"] + moves_used)
        else:
            final_text = "No setup moves used"
        self._text.configure(text=final_text)

