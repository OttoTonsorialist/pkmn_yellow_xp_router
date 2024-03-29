import tkinter as tk
from tkinter import ttk
import logging
from controllers.battle_summary_controller import BattleSummaryController
import time

from controllers.main_controller import MainController
from gui import custom_components, route_event_components, battle_summary
from gui.pkmn_components.state_viewer import StateViewer
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem
from utils.constants import const
from utils.config_manager import config
from utils import tk_utils
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


class EventDetails(ttk.Frame):
    def __init__(self, controller:MainController, *args, **kwargs):
        self.state_summary_width = 900
        self.battle_summary_width = 1400
        self.save_delay = 2
        super().__init__(*args, **kwargs, width=self.state_summary_width)
        self.grid_propagate(False)

        self._controller = controller
        self._battle_summary_controller = BattleSummaryController(self._controller)
        self._ignore_tab_switching = False
        self._cur_delayed_event_id = None
        self._cur_delayed_event_start = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook_holder = ttk.Frame(self)
        self.notebook_holder.grid(row=0, column=0, padx=2, pady=2, sticky=tk.NSEW)
        self.notebook_holder.columnconfigure(0, weight=1)
        self.notebook_holder.rowconfigure(0, weight=1)
        self.tabbed_states = ttk.Notebook(self.notebook_holder)
        self.tabbed_states.enable_traversal()

        self.pre_state_frame = ttk.Frame(self.tabbed_states)
        self.pre_state_frame.grid(row=0, column=0, padx=2, pady=2, sticky=tk.NSEW)
        self.auto_change_tab_checkbox = custom_components.CheckboxLabel(self.pre_state_frame, text="Switch tabs automatically", flip=True, toggle_command=self._handle_auto_switch_toggle)
        self.auto_change_tab_checkbox.grid(column=1, row=0, padx=10, pady=5, columnspan=2)
        self.auto_change_tab_checkbox.set_checked(config.do_auto_switch())
        self.state_pre_viewer = StateViewer(self.pre_state_frame)
        self.state_pre_viewer.grid(column=1, row=2, padx=10, pady=10, columnspan=2)

        self.pre_state_frame.columnconfigure(0, weight=1)
        self.pre_state_frame.columnconfigure(3, weight=1)
        self.pre_state_frame.rowconfigure(5, weight=1)

        self.battle_summary_frame = battle_summary.BattleSummary(self._battle_summary_controller, self.tabbed_states, width=self.battle_summary_width)
        self.battle_summary_frame.grid(row=1, column=0, padx=2, pady=2)
        self.battle_summary_frame.show_contents()

        self.tabbed_states.add(self.pre_state_frame, text="Pre-event State")
        self.pre_state_tab_index = 0
        self.tabbed_states.add(self.battle_summary_frame, text="Battle Summary")
        self.battle_summary_tab_index = 1
        self.tabbed_states.grid(row=0, column=0, sticky=tk.NSEW)
        self.tabbed_states.columnconfigure(0, weight=1)
        self.tabbed_states.rowconfigure(0, weight=1)

        self.event_details_frame = ttk.Frame(self.pre_state_frame)
        self.event_details_frame.grid(row=5, column=0, columnspan=4, sticky=tk.NSEW)
        self.event_details_frame.rowconfigure(0, weight=1, uniform="group")
        self.event_details_frame.rowconfigure(2, weight=1, uniform="group")
        self.event_details_frame.columnconfigure(0, weight=1, uniform="group")
        self.event_details_frame.columnconfigure(2, weight=1, uniform="group")

        self.footer_frame = ttk.Frame(self)
        self.footer_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)

        # create this slightly out of order because we need the reference
        self.event_editor_lookup = route_event_components.EventEditorFactory(self.event_details_frame)
        self.current_event_editor = None

        self.trainer_notes = route_event_components.EventEditorFactory(self.footer_frame).get_editor(
            route_event_components.EditorParams(const.TASK_NOTES_ONLY, None, None),
            save_callback=self.update_existing_event,
            delayed_save_callback=self.update_existing_event_after_delay,
            notes_visibility_callback=self._tab_changed_callback,
        )
        self.trainer_notes.grid(row=0, column=0, sticky=tk.EW)

        self.footer_frame.columnconfigure(0, weight=1)

        self.tabbed_states.bind('<<NotebookTabChanged>>', self._tab_changed_callback)
        self.bind(self._controller.register_event_selection(self), self._handle_selection)
        self.bind(self._controller.register_record_mode_change(self), self._handle_selection)
        self.bind(self._controller.register_route_change(self), self._handle_route_change)
        self.bind(self._controller.register_version_change(self), self._handle_version_change)
        self.bind(self._battle_summary_controller.register_nonload_change(self), self.update_existing_event)
        self._controller.register_pre_save_hook(self.force_and_clear_event_update)

        self._tab_changed_callback()
    
    def _tab_changed_callback(self, *args, **kwargs):
        if not self.tabbed_states.select():
            # This doesn't occur during normal processing, but can occur when closing down the app
            # Just prevent an extra error from occuring
            # this value should be a string containing an identifier (or empty, if no tabs exist)
            return

        selected_tab_index = self.tabbed_states.index(self.tabbed_states.select())
        if selected_tab_index == self.battle_summary_tab_index:
            self.configure(width=self.battle_summary_width)
            self.battle_summary_frame.after(300, self.battle_summary_frame.show_contents)
            if not config.are_notes_visible_in_battle_summary():
                self.footer_frame.grid_forget()
        else:
            self.battle_summary_frame.hide_contents()
            self.configure(width=self.state_summary_width)
            self.footer_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)
    
    def change_tabs(self, *args, **kwargs):
        if not self.tabbed_states.select():
            return

        selected_tab_index = self.tabbed_states.index(self.tabbed_states.select())
        if selected_tab_index == self.battle_summary_tab_index:
            self.tabbed_states.select(self.pre_state_tab_index)
        else:
            self.tabbed_states.select(self.battle_summary_tab_index)
    
    def _handle_version_change(self, *args, **kwargs):
        self._battle_summary_controller.load_empty()
        self.battle_summary_frame.configure_weather(current_gen_info().get_valid_weather())
        self.battle_summary_frame.configure_setup_moves(current_gen_info().get_stat_modifer_moves())
    
    def _handle_auto_switch_toggle(self, *args, **kwargs):
        config.set_auto_switch(self.auto_change_tab_checkbox.is_checked())
    
    def _handle_route_change(self, *args, **kwargs):
        event_group = self._controller.get_single_selected_event_obj()
        if event_group is None:
            self.state_pre_viewer.set_state(self._controller.get_init_state())
            self.battle_summary_frame.set_team(None)
        else:
            self.state_pre_viewer.set_state(event_group.init_state)
            if event_group.event_definition.trainer_def is not None:
                self.battle_summary_frame.set_team(
                    event_group.event_definition.get_pokemon_list(),
                    cur_state=event_group.init_state,
                    event_group=event_group
                )
            else:
                self.battle_summary_frame.set_team(None)
    
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
            if isinstance(trainer_event_group, EventItem) and event_group.event_definition.learn_move is None:
                trainer_event_group = trainer_event_group.parent
            
            if self._ignore_tab_switching or self.auto_change_tab_checkbox.is_checked():
                if trainer_event_group.event_definition.trainer_def is not None:
                    self.tabbed_states.select(self.battle_summary_tab_index)
                else:
                    self.tabbed_states.select(self.pre_state_tab_index)
            self.show_event_details(event_group.event_definition, event_group.init_state, event_group.final_state, do_allow_updates, event_group=trainer_event_group)
    
    def show_event_details(self, event_def:EventDefinition, init_state, final_state, allow_updates=True, event_group:EventGroup=None):
        self.force_and_clear_event_update()
        if self._controller.is_record_mode_active():
            allow_updates = False

        self.state_pre_viewer.set_state(init_state)
        if self.current_event_editor is not None:
            self.current_event_editor.grid_forget()
            self.current_event_editor = None

        if event_def is None:
            self.trainer_notes.load_event(None)
            self.battle_summary_frame.set_team(None)
        else:
            self.trainer_notes.load_event(event_def)
            if event_def.trainer_def is not None:
                self.battle_summary_frame.set_team(event_def.get_pokemon_list(), cur_state=init_state, event_group=event_group)
            else:
                self.battle_summary_frame.set_team(None)

            if event_def.get_event_type() != const.TASK_NOTES_ONLY:
                # TODO: fix this gross ugly hack
                self.current_event_editor = self.event_editor_lookup.get_editor(
                    route_event_components.EditorParams(event_def.get_event_type(), None, init_state),
                    save_callback=self.update_existing_event,
                    delayed_save_callback=self.update_existing_event_after_delay,
                    is_enabled=allow_updates
                )
                self.current_event_editor.load_event(event_def)
                self.current_event_editor.grid(row=1, column=1)

    def update_existing_event(self, *args, **kwargs):
        self._event_update_helper(self._controller.get_single_selected_event_id())

    def update_existing_event_after_delay(self, *args, **kwargs):
        to_save = self._controller.get_single_selected_event_id()
        if self._cur_delayed_event_id is not None and self._cur_delayed_event_id != to_save:
            logger.error(f"Unexpected switch of event id from {self._cur_delayed_event_id} to {to_save}, something has gone wrong")

        self._cur_delayed_event_id = to_save
        self._cur_delayed_event_start = time.time() + self.save_delay
        self.after(int(self.save_delay * 1000), self._delayed_event_update)
    
    def force_and_clear_event_update(self, *args, **kwargs):
        if self._cur_delayed_event_id is None:
            return
        
        self._event_update_helper(self._cur_delayed_event_id)

    def _delayed_event_update(self, *args, **kwargs):
        if self._cur_delayed_event_id is None or self._cur_delayed_event_start is None:
            # if the save has already occurred, silently exit
            return
        
        if self._cur_delayed_event_start - time.time() > 0:
            return

        self._event_update_helper(self._cur_delayed_event_id)

    def _event_update_helper(self, event_to_update):
        if event_to_update is None:
            return

        if self._cur_delayed_event_id is not None and self._cur_delayed_event_id != event_to_update:
            logger.error(f"Found delayed update for: {self._cur_delayed_event_id} which is different from the current update occuring for {event_to_update}")
        
        self._cur_delayed_event_id = None
        self._cur_delayed_event_start = None
        try:
            if self.current_event_editor is None:
                new_event = EventDefinition()
            else:
                new_event = self.current_event_editor.get_event()
            
            if new_event.get_event_type() == const.TASK_TRAINER_BATTLE:
                new_trainer_def = self._battle_summary_controller.get_partial_trainer_definition()
                if new_trainer_def is None:
                    logger.error(f"Expected to get updated trainer def from battle summary controller, but got None instead")
                else:
                    new_trainer_def.exp_split = new_event.trainer_def.exp_split
                    new_trainer_def.pay_day_amount = new_event.trainer_def.pay_day_amount
                    new_trainer_def.mon_order = new_event.trainer_def.mon_order
                    new_event.trainer_def = new_trainer_def
            
            new_event.notes = self.trainer_notes.get_event().notes
        except Exception as e:
            logger.error("Exception occurred trying to update current event")
            logger.exception(e)
            self._controller.trigger_exception("Exception occurred trying to update current event")
            return
        
        self._controller.update_existing_event(event_to_update, new_event)
    
    def take_battle_summary_screenshot(self, *args, **kwargs):
        if self.tabbed_states.index(self.tabbed_states.select()) == self.battle_summary_tab_index:
            self._battle_summary_controller.take_screenshot(
                tk_utils.get_bounding_box(self.battle_summary_frame)
            )
            
    