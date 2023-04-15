import tkinter as tk
from tkinter import ttk
import logging

from controllers.main_controller import MainController
from gui import custom_components, route_event_components, pkmn_components, quick_add_components, battle_summary
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, TrainerEventDefinition, VitaminEventDefinition
from utils.constants import const
from utils.config_manager import config

logger = logging.getLogger(__name__)


class EventDetails(ttk.Frame):
    def __init__(self, controller:MainController, *args, **kwargs):
        self.state_summary_width = 900
        self.battle_summary_width = 1400
        super().__init__(*args, **kwargs, width=self.state_summary_width)

        self._controller = controller
        self._prev_selected_tab = None

        self.notebook_holder = ttk.Frame(self)
        self.tabbed_states = ttk.Notebook(self.notebook_holder)

        self.pre_state_frame = ttk.Frame(self.tabbed_states)
        self.pre_state_frame.pack(fill=tk.X)
        self.auto_change_tab_checkbox = custom_components.CheckboxLabel(self.pre_state_frame, text="Switch tabs automatically", flip=True)
        self.auto_change_tab_checkbox.grid(column=1, row=0, padx=10, pady=5, columnspan=2)
        self.auto_change_tab_checkbox.set_checked(True)
        self.state_pre_label = tk.Label(self.pre_state_frame, text="Pre-event State Display Mode:")
        self.state_pre_label.grid(column=1, row=1, padx=10, pady=5)
        self.pre_state_selector = custom_components.SimpleOptionMenu(self.pre_state_frame, [const.STATE_SUMMARY_LABEL, const.BADGE_BOOST_LABEL], callback=self._pre_state_display_mode_callback, width=25)
        self.pre_state_selector.grid(column=2, row=1, padx=10, pady=5)
        self.state_pre_viewer = pkmn_components.StateViewer(self.pre_state_frame)
        self.state_pre_viewer.grid(column=1, row=2, padx=10, pady=10, columnspan=2)
        self.badge_boost_viewer = pkmn_components.BadgeBoostViewer(self.pre_state_frame)

        self.pre_state_frame.columnconfigure(0, weight=1)
        self.pre_state_frame.columnconfigure(3, weight=1)

        self.post_state_frame = ttk.Frame(self.tabbed_states)
        self.post_state_frame.pack()
        self.state_post_label = tk.Label(self.post_state_frame, text="Post-event State:")
        self.state_post_label.grid(column=1, row=0, padx=10, pady=10)
        self.state_post_viewer = pkmn_components.StateViewer(self.post_state_frame)
        self.state_post_viewer.grid(column=1, row=1, padx=10, pady=10)

        self.battle_summary_frame = battle_summary.BattleSummary(self.tabbed_states, save_callback=self.update_existing_event)
        self.battle_summary_frame.pack(padx=2, pady=2)

        self.simple_battle_summary_frame = battle_summary.BattleSummary(self.tabbed_states, simple_mode=True)
        self.simple_battle_summary_frame.pack(padx=2, pady=2, expand=True, fill=tk.Y)

        self.tabbed_states.add(self.pre_state_frame, text="Pre-event State")
        self.pre_state_tab_index = 0
        self.tabbed_states.add(self.post_state_frame, text="Post-event State")
        self.post_state_tab_index = 1
        self.tabbed_states.add(self.battle_summary_frame, text="Battle Summary")
        self.battle_summary_tab_index = 2
        self.tabbed_states.add(self.simple_battle_summary_frame, text="Simple Battle Summary")
        self.simple_battle_summary_tab_index = 3
        self.tabbed_states.pack(expand=True, fill=tk.BOTH)

        self.event_viewer_frame = ttk.Frame(self)
        self.event_viewer_frame.pack(anchor=tk.N, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.event_details_frame = ttk.Frame(self.event_viewer_frame)
        self.event_details_frame.grid(row=0, column=0)

        self.event_viewer_frame.rowconfigure(0, weight=1)
        self.event_viewer_frame.columnconfigure(0, weight=1)

        self.footer_frame = ttk.Frame(self.event_viewer_frame)
        self.footer_frame.grid(row=1, column=0, sticky=tk.EW)

        self.footer_button_frame = ttk.Frame(self.footer_frame)

        # create this slightly out of order because we need the reference
        self.event_editor_lookup = route_event_components.EventEditorFactory(self.event_details_frame)
        self.current_event_editor = None

        self.trainer_notes = route_event_components.EventEditorFactory(self.footer_frame).get_editor(
            route_event_components.EditorParams(const.TASK_NOTES_ONLY, None, None),
            save_callback=self.update_existing_event
        )
        self.trainer_notes.grid(row=0, column=0, sticky=tk.EW)

        self.footer_button_frame.grid(row=1, column=0, sticky=tk.EW)

        self.footer_frame.columnconfigure(0, weight=1)

        self.tabbed_states.bind('<<NotebookTabChanged>>', self._tab_changed_callback)
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
                self.simple_battle_summary_frame.pause_calculations()
            else:
                self.configure(width=self.state_summary_width)
                self.battle_summary_frame.pause_calculations()
                self.simple_battle_summary_frame.allow_calculations()
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
            self.simple_battle_summary_frame.pause_calculations()

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
            
            if self.auto_change_tab_checkbox.is_checked():
                if trainer_event_group.event_definition.trainer_def is not None:
                    self.tabbed_states.select(self.battle_summary_tab_index)
                else:
                    self.tabbed_states.select(self.pre_state_tab_index)
            self.show_event_details(event_group.event_definition, event_group.init_state, event_group.final_state, do_allow_updates, event_group=trainer_event_group)
    
    def show_event_details(self, event_def:EventDefinition, init_state, final_state, allow_updates=True, event_group:EventGroup=None):
        if self._controller.is_record_mode_active():
            allow_updates = False

        self.state_pre_viewer.set_state(init_state)
        self.badge_boost_viewer.set_state(init_state)

        self.state_post_viewer.set_state(final_state)

        if self.current_event_editor is not None:
            self.current_event_editor.pack_forget()
            self.current_event_editor = None

        if event_def is None:
            self.trainer_notes.load_event(None)
            self.battle_summary_frame.set_team(None)
            self.simple_battle_summary_frame.set_team(None)
        else:
            self.trainer_notes.load_event(event_def)
            if event_def.trainer_def is not None:
                self.battle_summary_frame.set_team(event_def.get_trainer_obj().pkmn, cur_state=init_state, event_group=event_group)
                self.simple_battle_summary_frame.set_team(event_def.get_trainer_obj().pkmn, cur_state=init_state, event_group=event_group)
            else:
                self.battle_summary_frame.set_team(None)
                self.simple_battle_summary_frame.set_team(None)

            if event_def.get_event_type() != const.TASK_NOTES_ONLY:
                # TODO: fix this gross ugly hack
                self.current_event_editor = self.event_editor_lookup.get_editor(
                    route_event_components.EditorParams(event_def.get_event_type(), None, init_state),
                    save_callback=self.update_existing_event,
                    is_enabled=allow_updates
                )
                self.current_event_editor.load_event(event_def)
                self.current_event_editor.pack()

    def update_existing_event(self, *args, **kwargs):
        event_to_update = self._controller.get_single_selected_event_id()
        if event_to_update is None:
            return

        try:
            if self.current_event_editor is None:
                new_event = EventDefinition()
            else:
                new_event = self.current_event_editor.get_event()
            
            if new_event.get_event_type() == const.TASK_TRAINER_BATTLE:
                new_event.trainer_def.setup_moves = self.battle_summary_frame.get_setup_moves()
                new_event.trainer_def.enemy_setup_moves = self.battle_summary_frame.get_enemy_setup_moves()
                new_event.trainer_def.mimic_selection = self.battle_summary_frame.get_mimic_selection()
                new_event.trainer_def.custom_move_data = self.battle_summary_frame.get_custom_move_data()
            
            new_event.notes = self.trainer_notes.get_event().notes
        except Exception as e:
            logger.error("Exception occurred trying to update current event")
            logger.exception(e)
            self._controller.trigger_exception("Exception occurred trying to update current event")
            return
        
        self._controller.update_existing_event(event_to_update, new_event)
    