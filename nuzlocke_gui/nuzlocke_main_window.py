import os
import threading
import logging

import tkinter as tk
from tkinter import ttk, font, messagebox

from gui import custom_components, pkmn_components, quick_add_components
from gui.event_details import EventDetails
from gui.popups.color_config import ConfigWindow
from gui.popups.custom_dvs_popup import CustomDvsWindow
from gui.popups.data_dir_config_popup import DataDirConfigWindow
from gui.popups.delete_confirmation_popup import DeleteConfirmation
from gui.popups.load_route_popup import LoadRouteWindow
from gui.popups.new_folder_popup import NewFolderWindow
from gui.popups.new_route_popup import NewRouteWindow
from gui.popups.transfer_event_popup import TransferEventWindow
from gui.popups.custom_gen_popup import CustomGenWindow
from gui.recorder_status import RecorderStatus
from gui.route_search_component import RouteSearch
from nuzlocke_gui.nuzlocke_controller import NuzlockeController
from route_recording.recorder import RecorderController
from utils.constants import const
from utils.config_manager import config
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem, TrainerEventDefinition
import routing.router as router

logger = logging.getLogger(__name__)
flag_to_auto_update = False


class NuzlockeWindow(tk.Tk):
    def __init__(self, controller:NuzlockeController):
        super().__init__()
        self._controller = controller
        self._recorder_controller = RecorderController(self._controller)

        geometry = None
        #geometry = config.get_window_geometry()
        if not geometry:
            geometry = "2000x1200"
        self.geometry(geometry)
        self.title("Pokemon RBY XP Router")

        self.call("source", os.path.join(const.ASSETS_PATH, "azure.tcl"))
        self.call("set_theme", "dark")

        self.load_custom_font()

        # main container for everything to sit in... might be unnecessary?
        self.primary_window = ttk.Frame(self)
        self.primary_window.pack(fill=tk.BOTH, expand=True)

        # create container for split columns
        self.info_panel = ttk.Frame(self.primary_window)
        self.info_panel.pack(expand=True, fill=tk.BOTH)

        # left panel for controls
        self.left_info_panel = ttk.Frame(self.info_panel)
        self.left_info_panel.grid(row=0, column=0, sticky="nsew")

        self.top_left_controls = ttk.Frame(self.left_info_panel)
        self.top_left_controls.pack(fill=tk.X, anchor=tk.CENTER)

        # right panel for event details
        self.event_details = EventDetails(self._controller, self.info_panel)
        self.event_details.grid(row=0, column=1, sticky=tk.NSEW)
        self.event_details.pack_propagate(0)

        self.info_panel.grid_rowconfigure(0, weight=1)
        self.info_panel.grid_columnconfigure(0, weight=1, uniform="test")

        # TODO: reload from gamehook
        #self.bind('<Control-r>', self.open_transfer_event_window)

        # detail update function
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind(const.FORCE_QUIT_EVENT, self.cancel_and_quit)

        self.bind(self._controller.register_exception_callback(self), self._on_exception)
        self.new_event_window = None

    def run(self):
        # TODO: is this the right place for it?
        self._controller.load_all_custom_versions()
        self.mainloop()
    
    def _on_close(self, *args, **kwargs):
        # TODO: do we care about this for the dumb nuzlocke app?
        #config.set_window_geometry(self.geometry())
        self.destroy()
    
    def _on_exception(self, *args, **kwargs):
        exception_message = self._controller.get_next_exception_info()
        while exception_message is not None:
            threading.Thread(
                target=messagebox.showerror,
                args=("Error!", exception_message),
                daemon=True
            ).start()
            exception_message = self._controller.get_next_exception_info()
    
    def _on_name_change(self, *args, **kwargs):
        self.route_name.delete(0, tk.END)
        self.route_name.insert(0, self._controller.get_current_route_name())

    def save_route(self, *args, **kwargs):
        route_name = self.route_name.get()
        self._controller.save_route(route_name)
        self.message_label.set_message(f"Successfully saved route: {route_name}")
    
    def export_notes(self, *args, **kwargs):
        self.message_label.set_message(f"Exported notes to: {self._controller.export_notes(self.route_name.get())}")

    def load_custom_font(self):
        if config.get_custom_font_name() in font.families():
            defaultFont = font.nametofont("TkDefaultFont")
            defaultFont.configure(family=config.get_custom_font_name())
        else:
            defaultFont = font.nametofont("TkDefaultFont")
            defaultFont.configure(family=config.DEFAULT_FONT_NAME)

    def update_run_status(self, *args, **kwargs):
        if self._controller.has_errors():
            self.run_status_frame.config(style="Warning.TFrame")
            self.run_status_label.config(text="Run Status: Invalid", style="Warning.TLabel")
        else:
            self.run_status_frame.config(style="Success.TFrame")
            self.run_status_label.config(text="Run Status: Valid", style="Success.TLabel")
    
    def update_run_version(self, *args, **kwargs):
        self.route_version.config(
            text=f"{self._controller.get_version()} Version",
            background=const.VERSION_COLORS.get(self._controller.get_version(), "white")
        )
        self.record_button.enable()
    
    def record_button_clicked(self, *args, **kwargs):
        self._controller.set_record_mode(not self._controller.is_record_mode_active())
    
    def _on_record_mode_changed(self, *args, **kwargs):
        if self._controller.is_record_mode_active():
            self.record_button.configure(text="Cancel\nRecording")
            self.recorder_status.lift()
        else:
            self.record_button.configure(text="Enable\nRecording")
            self.recorder_status.lower()
        self._handle_new_selection()

    def trainer_preview(self, *args, **kwargs):
        if self._controller.get_preview_event() is None:
            return

        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) > 1:
            return

        init_state = self._controller.get_state_after(
            previous_event_id=None if len(all_event_ids) == 0 else all_event_ids[0]
        )

        # create a fake event_def just so we can show the trainer that the user is looking at
        # TODO: just using the init_state as the post_event state as well. Ideally would like to use None for an empty state, but that's not currently supported
        self.event_details.show_event_details(
            self._controller.get_preview_event(),
            init_state,
            init_state,
            allow_updates=False
        )
    
    def _report_new_selection(self, *args, **kwargs):
        # this is different from _handle_new_selection as we are reporting the new selection
        # from the users action (via a tk event) to the controller
        # _handle_new_selection will respond to the controller's event about the selection changing

        # guard against unnecessary updates so that the treeview can be updated without creating an infinite loop
        cur_treeview_selected = self.event_list.get_all_selected_event_ids()
        if self._controller.get_all_selected_ids() != cur_treeview_selected:
            self._controller.select_new_events(cur_treeview_selected)
    
    def _handle_new_selection(self, *args, **kwargs):
        # just re-use the variable temporarily
        all_event_ids = self._controller.get_all_selected_ids()
        if all_event_ids != self.event_list.get_all_selected_event_ids():
            self.event_list.set_all_selected_event_ids(all_event_ids)

        self.event_list.scroll_to_selected_events()

        # now assign it the value it will have for the rest of the function
        all_event_ids = self.event_list.get_all_selected_event_ids(allow_event_items=False)
        if len(all_event_ids) > 1 or len(all_event_ids) == 0:
            event_group = None
        else:
            event_group = self._controller.get_event_by_id(all_event_ids[0])
        
        disable_all = False
        if self._controller.is_record_mode_active() or self._controller.get_raw_route().init_route_state is None:
            disable_all = True
        
        if not disable_all and isinstance(event_group, EventFolder):
            self.rename_folder_button.enable()
        else:
            self.rename_folder_button.disable()
        
        if not disable_all and (event_group is not None or len(all_event_ids) > 0):
            # As long as we have any editable events selected, toggle the buttons to allow editing those events
            self.delete_event_button.enable()
            self.transfer_event_button.enable()
            self.move_group_down_button.enable()
            self.move_group_up_button.enable()
            self.highlight_toggle_button.enable()
        else:
            self.delete_event_button.disable()
            self.transfer_event_button.disable()
            self.move_group_down_button.disable()
            self.move_group_up_button.disable()
            self.highlight_toggle_button.disable()
        
        if not disable_all and (event_group is not None or len(self.event_list.get_all_selected_event_ids()) == 0):
            # as long as we have a finite place to create a new folder, enable the option
            # either only a single event is selected, or no events are selected
            # Need to check all events, not just editable ones
            self.new_folder_button.enable()
        else:
            self.new_folder_button.disable()
    
    def open_app_config_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = DataDirConfigWindow(self, self.cancel_and_quit)

    def clear_popup(self, *args, **kwargs):
        # hook for when a pop-up cleans up after itself
        # assumes the pop-up is getting destroyed, and we just want to drop the reference to a (now unused) object
        # TODO: with new pop-up paradigm, can we drop reference tracking in the main window entirely?
        if self.new_event_window is not None:
            self.new_event_window = None

    def cancel_and_quit(self, *args, **kwargs):
        if self.new_event_window is not None:
            self.new_event_window.close()
            self.new_event_window = None
        self.destroy()
    
    def _is_active_window(self):
        # returns true if the current window is active (i.e. no sub-windows exist)
        if self.new_event_window is not None and tk.Toplevel.winfo_exists(self.new_event_window):
            return False
        return True
