import tkinter as tk
from tkinter import ttk
import logging

from gui import custom_components, route_event_components, battle_summary
from nuzlocke_gui.nuzlocke_controller import NuzlockeController
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem
from utils.constants import const
from utils.config_manager import config

logger = logging.getLogger(__name__)


class EventDetails(ttk.Frame):
    def __init__(self, controller:NuzlockeController, *args, **kwargs):
        self.state_summary_width = 900
        self.battle_summary_width = 1400
        super().__init__(*args, **kwargs, width=self.state_summary_width)

        self._controller = controller
        self._prev_selected_tab = None

        self.battle_summary_frame = battle_summary.BattleSummary(self)
        self.battle_summary_frame.pack(padx=2, pady=2)

        self.bind(self._controller.register_event_selection(self), self._handle_selection)
        self.bind(self._controller.register_record_mode_change(self), self._handle_selection)
        self.bind(self._controller.register_route_change(self), self._handle_route_change)

        self._tab_changed_callback()
    
    def _tab_changed_callback(self, *args, **kwargs):
        if not self.tabbed_states.select():
            # This doesn't occur during normal processing, but can occur when closing down the app
            # Just prevent an extra error from occuring
            # this value should be a string containing an identifier (or empty, if no tabs exist)
            return

        selected_tab_index = self.tabbed_states.index(self.tabbed_states.select())
        prev_tab = self._prev_selected_tab
        self._prev_selected_tab = selected_tab_index

        if selected_tab_index == self.battle_summary_tab_index or selected_tab_index == self.simple_battle_summary_tab_index:
            if prev_tab == selected_tab_index:
                return

            if selected_tab_index ==  self.battle_summary_tab_index:
                self.configure(width=self.battle_summary_width)
                self.battle_summary_frame.allow_calculations()
            else:
                self.configure(width=self.state_summary_width)
                self.battle_summary_frame.pause_calculations()
            self.event_details_frame.grid_forget()
            self.event_viewer_frame.pack_forget()
            self.notebook_holder.pack_forget()
            self.notebook_holder.pack(anchor=tk.N, fill=tk.BOTH, expand=True, padx=2, pady=2)
            self.event_viewer_frame.pack(anchor=tk.N, fill=tk.BOTH, expand=False, padx=2, pady=2)

        else:
            if prev_tab == self.pre_state_tab_index or prev_tab == self.post_state_tab_index:
                return
            self.configure(width=self.state_summary_width)
            self.notebook_holder.pack_forget()
            self.notebook_holder.pack(anchor=tk.N, fill=tk.X, padx=2, pady=2)
            self.event_viewer_frame.pack_forget()
            self.event_viewer_frame.pack(anchor=tk.N, fill=tk.BOTH, expand=True, padx=2, pady=2)
            self.event_details_frame.grid(row=0, column=0)
            self.battle_summary_frame.pause_calculations()

    def _pre_state_display_mode_callback(self, *args, **kwargs):
        if self.pre_state_selector.get() == const.BADGE_BOOST_LABEL:
            self.state_pre_viewer.grid_forget()
            self.badge_boost_viewer.grid(column=1, row=1, padx=10, pady=10, columnspan=2)
        else:
            self.badge_boost_viewer.grid_forget()
            self.state_pre_viewer.grid(column=1, row=1, padx=10, pady=10, columnspan=2)
    
    def _handle_route_change(self, *args, **kwargs):
        event_group = self._controller.get_single_selected_event_obj()
        if event_group is None:
            self.state_pre_viewer.set_state(self._controller.get_init_state())
            self.badge_boost_viewer.set_state(self._controller.get_init_state())
            self.state_post_viewer.set_state(self._controller.get_final_state())
        else:
            self.state_pre_viewer.set_state(event_group.init_state)
            self.badge_boost_viewer.set_state(event_group.init_state)
            self.state_post_viewer.set_state(event_group.final_state)
    
    def _handle_selection(self, *args, **kwargs):
        event_group = self._controller.get_single_selected_event_obj()

        if event_group is None:
            self.show_event_details(None, self._controller.get_init_state(), self._controller.get_final_state(), allow_updates=False)
        elif isinstance(event_group, EventFolder):
            self.show_event_details(event_group.event_definition, event_group.init_state, event_group.final_state)
        else:
            do_allow_updates = (
                 isinstance(event_group, EventGroup) or 
                 event_group.event_definition.get_event_type() == const.TASK_LEARN_MOVE_LEVELUP
            )
            trainer_event_group = event_group
            if isinstance(trainer_event_group, EventItem):
                trainer_event_group = trainer_event_group.parent
            self.show_event_details(event_group.event_definition, event_group.init_state, event_group.final_state, do_allow_updates, event_group=trainer_event_group)
    
    def show_event_details(self, event_def:EventDefinition, init_state, final_state, allow_updates=True, event_group:EventGroup=None):
        if self._controller.is_record_mode_active():
            allow_updates = False

        if self.current_event_editor is not None:
            self.current_event_editor.pack_forget()
            self.current_event_editor = None

        if event_def is None:
            self.trainer_notes.load_event(None)
            self.battle_summary_frame.set_team(None)
        else:
            self.trainer_notes.load_event(event_def)
            if event_def.trainer_def is not None:
                self.battle_summary_frame.set_team(event_def.get_trainer_obj().pkmn, cur_state=init_state, event_group=event_group)
            else:
                self.battle_summary_frame.set_team(None)

            if event_def.get_event_type() != const.TASK_NOTES_ONLY:
                # TODO: fix this gross ugly hack
                self.current_event_editor = self.event_editor_lookup.get_editor(
                    route_event_components.EditorParams(event_def.get_event_type(), None, init_state),
                    save_callback=self.update_existing_event,
                    is_enabled=allow_updates
                )
                self.current_event_editor.load_event(event_def)
                self.current_event_editor.pack()
