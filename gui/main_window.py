import os
import threading
import logging

import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, font, messagebox

from controllers.main_controller import MainController
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
from route_recording.recorder import RecorderController
from utils.constants import const
from utils.config_manager import config
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem, TrainerEventDefinition
import routing.router as router

logger = logging.getLogger(__name__)
flag_to_auto_update = False


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._controller = MainController()
        self._recorder_controller = RecorderController(self._controller)

        geometry = config.get_window_geometry()
        if not geometry:
            geometry = "2000x1200"
        self.geometry(geometry)
        self.title("Pokemon RBY XP Router")

        # fix tkinter bug
        style = ttk.Style()
        style.map("Treeview", foreground=fixed_map("foreground", style), bg_color=fixed_map("bg_color", style))

        style.layout("TNotebook", [])
        # magic, found here: https://stackoverflow.com/a/29572789
        style.element_create('Plain.Notebook.tab', "from", 'default')
        style.layout("TNotebook.Tab",
            [('Plain.Notebook.tab', {'children':
                [('Notebook.padding', {'side': 'top', 'children':
                    [('Notebook.focus', {'side': 'top', 'children':
                        [('Notebook.label', {'side': 'top', 'sticky': ''})],
                    'sticky': 'nswe'})],
                'sticky': 'nswe'})],
            'sticky': 'nswe'})])

        style.configure("TNotebook", bg_color=config.get_background_color())
        style.configure("TNotebook.Tab", bg_color=config.get_secondary_color(), borderwidth=1, bordercolor="black")
        style.map("TNotebook.Tab", bg_color=[("selected", config.get_primary_color())])

        self.load_custom_font()
        ctk.set_appearance_mode("dark")

        # menu bar
        self.top_menu_bar = tk.Menu(self)
        self.configure(menu=self.top_menu_bar)

        self.file_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.file_menu.add_command(label="Customize DVs     (Ctrl+X)", command=self.open_customize_dvs_window)
        self.file_menu.add_command(label="New Route       (Ctrl+N)", command=self.open_new_route_window)
        self.file_menu.add_command(label="Load Route      (Ctrl+L)", command=self.open_load_route_window)
        self.file_menu.add_command(label="Save Route       (Ctrl+S)", command=self.save_route)
        self.file_menu.add_command(label="Export Notes       (Ctrl+Shift+W)", command=self.export_notes)
        self.file_menu.add_command(label="Config Colors       (Ctrl+Shift+D)", command=self.open_config_window)
        self.file_menu.add_command(label="Custom Gens       (Ctrl+Shift+E)", command=self.open_custom_gens_window)
        self.file_menu.add_command(label="App Config       (Ctrl+Shift+Z)", command=self.open_app_config_window)

        self.event_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.event_menu.add_command(label="Move Event Up           (Ctrl+E)", command=self.move_group_up)
        self.event_menu.add_command(label="Move Event Down      (Ctrl+D)", command=self.move_group_down)
        self.event_menu.add_command(label="Toggle Highlight       (Ctrl+V)", command=self.toggle_event_highlight)
        self.event_menu.add_command(label="Transfer Event             (Ctrl+R)", command=self.open_transfer_event_window)
        self.event_menu.add_command(label="Delete Event             (Ctrl+B)", command=self.delete_group)

        self.folder_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.folder_menu.add_command(label="New Folder                   (Ctrl+Q)", command=self.open_new_folder_window)
        self.folder_menu.add_command(label="Rename Cur Folder       (Ctrl+W)", command=self.rename_folder)

        self.top_menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.top_menu_bar.add_cascade(label="Events", menu=self.event_menu)
        self.top_menu_bar.add_cascade(label="Folders", menu=self.folder_menu)

        # main container for everything to sit in... might be unnecessary?
        self.primary_window = ctk.CTkFrame(self)
        self.primary_window.pack(fill=tk.BOTH, expand=True)

        # create top row, which goes across the whole screen
        self.top_row = ctk.CTkFrame(self.primary_window)
        self.top_row.pack(fill=tk.X)
        self.top_row.pack_propagate(False)

        self.record_button = custom_components.SimpleButton(self.top_row, text="Enable\nRecording", command=self.record_button_clicked)
        self.record_button.grid(row=0, column=0, sticky=tk.W, padx=3, pady=3)
        self.record_button.disable()

        self.run_status_label = ctk.CTkLabel(self.top_row, text="Run Status: Valid", bg_color=const.VALID_COLOR, anchor=tk.W, padx=10, pady=10)
        self.run_status_label.grid(row=0, column=1, sticky=tk.W)

        self.route_version = ctk.CTkLabel(self.top_row, text="RBY Version", anchor=tk.W, padx=10, pady=10, text_color="black")
        self.route_version.grid(row=0, column=2)

        self.route_name_label = ctk.CTkLabel(self.top_row, text="Route Name: ")
        self.route_name_label.grid(row=0, column=3)

        self.route_name = ctk.CTkEntry(self.top_row)
        self.route_name.grid(row=0, column=4)
        self.route_name.configure(width=150)

        self.message_label = custom_components.AutoClearingLabel(self.top_row, width=100, justify=tk.LEFT, anchor=tk.W)
        self.message_label.grid(row=0, column=5, sticky=tk.E)

        # create container for split columns
        self.info_panel = ctk.CTkFrame(self.primary_window)
        self.info_panel.pack(expand=True, fill=tk.BOTH)

        # left panel for controls and event list
        self.left_info_panel = ctk.CTkFrame(self.info_panel)
        self.left_info_panel.grid(row=0, column=0, sticky="nsew")

        self.top_left_controls = ctk.CTkFrame(self.left_info_panel)
        self.top_left_controls.pack(fill=tk.X, anchor=tk.CENTER)

        self.recorder_status = RecorderStatus(self._controller, self._recorder_controller, self.top_left_controls)

        self.trainer_add = quick_add_components.QuickTrainerAdd(
            self._controller,
            self.top_left_controls
        )

        self.item_add = quick_add_components.QuickItemAdd(
            self._controller,
            self.top_left_controls,
        )

        self.wild_pkmn_add = quick_add_components.QuickWildPkmn(
            self._controller,
            self.top_left_controls,
        )

        self.misc_add = quick_add_components.QuickMiscEvents(
            self._controller,
            self.top_left_controls,
        )

        self.recorder_status.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5, columnspan=4)
        self.trainer_add.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        self.item_add.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)
        self.wild_pkmn_add.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)
        self.misc_add.grid(row=0, column=3, sticky=tk.NSEW, padx=5, pady=5)

        self.group_controls = ctk.CTkFrame(self.left_info_panel)
        self.group_controls.pack(fill=tk.X, anchor=tk.CENTER)
        
        self.move_group_up_button = custom_components.SimpleButton(self.group_controls, text='Move Event Up', command=self.move_group_up, width=15)
        self.move_group_up_button.grid(row=0, column=1, padx=5, pady=1)
        self.move_group_down_button = custom_components.SimpleButton(self.group_controls, text='Move Event Down', command=self.move_group_down, width=15)
        self.move_group_down_button.grid(row=0, column=2, padx=5, pady=1)
        self.highlight_toggle_button = custom_components.SimpleButton(self.group_controls, text='Toggle Highlight', command=self.toggle_event_highlight, width=15)
        self.highlight_toggle_button.grid(row=0, column=3, padx=5, pady=1)
        self.transfer_event_button = custom_components.SimpleButton(self.group_controls, text='Transfer Event', command=self.open_transfer_event_window, width=15)
        self.transfer_event_button.grid(row=0, column=4, padx=5, pady=1)

        self.delete_event_button = custom_components.SimpleButton(self.group_controls, text='Delete Event', command=self.delete_group, width=15)
        self.delete_event_button.grid(row=0, column=6, padx=5, pady=1)

        self.new_folder_button = custom_components.SimpleButton(self.group_controls, text='New Folder', command=self.open_new_folder_window, width=15)
        self.new_folder_button.grid(row=0, column=8, padx=5, pady=1)
        self.rename_folder_button = custom_components.SimpleButton(self.group_controls, text='Rename Folder', command=self.rename_folder, width=15)
        self.rename_folder_button.grid(row=0, column=9, padx=5, pady=1)

        self.group_controls.columnconfigure(0, weight=1)
        self.group_controls.columnconfigure(5, weight=1)
        self.group_controls.columnconfigure(7, weight=1)
        self.group_controls.columnconfigure(11, weight=1)

        self.route_search = RouteSearch(self._controller, self.left_info_panel)
        self.route_search.pack(fill=tk.X, anchor=tk.CENTER)

        self.frame_for_event_list = ctk.CTkFrame(self.left_info_panel)
        self.frame_for_event_list.pack(fill=tk.BOTH, anchor=tk.CENTER, expand=True)

        self.event_list = pkmn_components.RouteList(self._controller, self.frame_for_event_list)
        self.scroll_bar = ctk.CTkScrollbar(self.frame_for_event_list, orientation="vertical", command=self.event_list.yview, width=30)

        # intentionally pack event list after scrollbar, so they're ordered correctly
        self.scroll_bar.pack(side="right", fill=tk.BOTH)
        self.event_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True, side="right")
        self.event_list.configure(yscrollcommand=self.scroll_bar.set)

        # right panel for event details
        self.event_details = EventDetails(self._controller, self.info_panel)
        self.event_details.grid(row=0, column=1, sticky=tk.NSEW)
        self.event_details.pack_propagate(0)

        self.info_panel.grid_rowconfigure(0, weight=1)
        # these uniform values don't have to be a specific value, they just have to match
        self.info_panel.grid_columnconfigure(0, weight=1, uniform="test")

        # main route actions
        self.bind('<Control-x>', self.open_customize_dvs_window)
        self.bind('<Control-n>', self.open_new_route_window)
        self.bind('<Control-l>', self.open_load_route_window)
        self.bind('<Control-s>', self.save_route)
        self.bind('<Control-W>', self.export_notes)
        # event actions
        self.bind('<Control-d>', self.move_group_down)
        self.bind('<Control-e>', self.move_group_up)
        self.bind('<Control-v>', self.toggle_event_highlight)
        self.bind('<Control-r>', self.open_transfer_event_window)
        self.bind('<Control-b>', self.delete_group)
        self.bind('<Delete>', self.delete_group)
        # folder actions
        self.bind('<Control-q>', self.open_new_folder_window)
        self.bind('<Control-w>', self.rename_folder)
        # config integrations
        self.bind('<Control-E>', self.open_custom_gens_window)
        self.bind('<Control-D>', self.open_config_window)
        self.bind('<Control-Z>', self.open_app_config_window)
        # detail update function
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<<TreeviewSelect>>", self._report_new_selection)
        self.bind(const.ROUTE_LIST_REFRESH_EVENT, self.update_run_status)
        self.bind(const.FORCE_QUIT_EVENT, self.cancel_and_quit)

        self.bind(self._controller.register_event_selection(self), self._handle_new_selection)
        self.bind(self._controller.register_version_change(self), self.update_run_version)
        self.bind(self._controller.register_exception_callback(self), self._on_exception)
        self.bind(self._controller.register_name_change(self), self._on_name_change)
        self.bind(self._controller.register_record_mode_change(self), self._on_record_mode_changed)
        # TODO: should this be moved directly to the event list class?
        self.bind(self._controller.register_route_change(self), self.event_list.refresh)

        self.event_list.refresh()
        self.new_event_window = None

    def run(self):
        # TODO: is this the right place for it?
        self._controller.load_all_custom_versions()
        self.mainloop()
    
    def _on_close(self, *args, **kwargs):
        # just need to save window geometry before closing
        config.set_window_geometry(self.geometry())
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
            self.run_status_label.configure(text="Run Status: Invalid", bg_color=const.ERROR_COLOR)
        else:
            self.run_status_label.configure(text="Run Status: Valid", bg_color=const.VALID_COLOR)
    
    def update_run_version(self, *args, **kwargs):
        self.route_version.configure(
            text=f"{self._controller.get_version()} Version",
            bg_color=const.VERSION_COLORS.get(self._controller.get_version(), "white")
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

    def trainer_preview(self):
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
    
    def open_custom_gens_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = CustomGenWindow(self, self._controller)
    
    def open_config_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = ConfigWindow(self)
    
    def open_new_route_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = NewRouteWindow(self, self._controller)
    
    def open_load_route_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = LoadRouteWindow(self, self._controller)

    def open_customize_dvs_window(self, *args, **kwargs):
        if self._is_active_window() and self._controller.get_init_state() is not None:
            self.new_event_window = CustomDvsWindow(self, self._controller, self._controller.get_dvs())

    def move_group_up(self, event=None):
        self._controller.move_groups_up(self.event_list.get_all_selected_event_ids(allow_event_items=False))

    def move_group_down(self, event=None):
        # NOTE: have to reverse the list since we move items one at a time
        self._controller.move_groups_down(reversed(self.event_list.get_all_selected_event_ids(allow_event_items=False)))

    def toggle_event_highlight(self, event=None):
        self._controller.toggle_event_highlight(self.event_list.get_all_selected_event_ids(allow_event_items=False))

    def delete_group(self, event=None):
        all_event_ids = self.event_list.get_all_selected_event_ids(allow_event_items=False)
        if len(all_event_ids) == 0:
            return
        
        do_prompt = False
        if len(all_event_ids) == 1:
            cur_event_id = all_event_ids[0]
            event_obj = self._controller.get_event_by_id(cur_event_id)
            if isinstance(event_obj, EventFolder) and len(event_obj.children) > 0:
                do_prompt = True
        else:
            do_prompt = True
        
        if do_prompt:
            if self._is_active_window():
                self.new_event_window = DeleteConfirmation(self, self._controller, all_event_ids)
        else:
            # only don't prompt when deleting a single event (or empty folder)
            self._controller.delete_events([all_event_ids[0]])
            self.event_list.refresh()
            self.trainer_add.trainer_filter_callback()

    def open_transfer_event_window(self, event=None):
        if self._is_active_window():
            all_event_ids = self.event_list.get_all_selected_event_ids(allow_event_items=False)
            if len(all_event_ids) == 0:
                return

            invalid_folders = set()
            for cur_event_id in all_event_ids:
                for cur_invalid in self._controller.get_invalid_folders(cur_event_id):
                    invalid_folders.add(cur_invalid)
            
            self.new_event_window = TransferEventWindow(
                self,
                self._controller,
                self._controller.get_all_folder_names(),
                [x for x in self._controller.get_all_folder_names() if x not in invalid_folders],
                all_event_ids
            )

    def rename_folder(self, *args, **kwargs):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) > 1 or len(all_event_ids) == 0:
            return

        self.open_new_folder_window(**{const.EVENT_FOLDER_NAME: self._controller.get_event_by_id(all_event_ids[0]).name})

    def open_new_folder_window(self, *args, **kwargs):
        if self._is_active_window():
            all_event_ids = self.event_list.get_all_selected_event_ids()
            if len(all_event_ids) > 1:
                return

            if const.EVENT_FOLDER_NAME in kwargs:
                existing_folder_name = kwargs.get(const.EVENT_FOLDER_NAME)
            else:
                existing_folder_name = None
            self.new_event_window = NewFolderWindow(
                self,
                self._controller,
                self._controller.get_all_folder_names(),
                existing_folder_name,
                insert_after=all_event_ids[0] if len(all_event_ids) == 1 else None
            )

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


def fixed_map(option, style):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
    return [elm for elm in style.map('Treeview', query_opt=option) if
      elm[:2] != ('!disabled', '!selected')]
