import os
import logging

import tkinter as tk
from tkinter import ttk, font, messagebox

from controllers.main_controller import MainController
from gui import custom_tkinter, pkmn_components, quick_add_components
from gui.event_details import EventDetails
from gui.popups.color_config import ConfigWindow
from gui.popups.custom_dvs_popup import CustomDvsWindow
from gui.popups.data_dir_config_popup import DataDirConfigWindow
from gui.popups.delete_confirmation_popup import DeleteConfirmation
from gui.popups.load_route_popup import LoadRouteWindow
from gui.popups.new_event_popup import NewEventWindow
from gui.popups.new_folder_popup import NewFolderWindow
from gui.popups.new_route_popup import NewRouteWindow
from gui.popups.route_one_popup import RouteOneWindow
from gui.popups.transfer_event_popup import TransferEventWindow
from utils.constants import const
from utils.config_manager import config
from utils import route_one_utils
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem, TrainerEventDefinition
import routing.router as router

logger = logging.getLogger(__name__)
flag_to_auto_update = False


class MainWindow(tk.Tk):
    def __init__(self, controller:MainController):
        super().__init__()
        self._controller = controller

        geometry = config.get_window_geometry()
        if not geometry:
            geometry = "2000x1200"
        self.geometry(geometry)
        self.title("Pokemon RBY XP Router")

        # fix tkinter bug
        style = ttk.Style()
        style.map("Treeview", foreground=fixed_map("foreground", style), background=fixed_map("background", style))

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

        style.configure("TNotebook", background=config.get_background_color())
        style.configure("TNotebook.Tab", background=config.get_secondary_color(), borderwidth=1, bordercolor="black")
        style.map("TNotebook.Tab", background=[("selected", config.get_primary_color())])

        self.load_custom_font()

        # menu bar
        self.top_menu_bar = tk.Menu(self)
        self.config(menu=self.top_menu_bar)

        self.file_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.file_menu.add_command(label="Customize DVs     (Ctrl+X)", command=self.open_customize_dvs_window)
        self.file_menu.add_command(label="New Route       (Ctrl+N)", command=self.open_new_route_window)
        self.file_menu.add_command(label="Load Route      (Ctrl+L)", command=self.open_load_route_window)
        self.file_menu.add_command(label="Save Route       (Ctrl+S)", command=self.save_route)
        self.file_menu.add_command(label="Export Notes       (Ctrl+Shift+W)", command=self.export_notes)
        self.file_menu.add_command(label="Config Colors       (Ctrl+Shift+D)", command=self.open_config_window)
        self.file_menu.add_command(label="App Config       (Ctrl+Shift+Z)", command=self.open_app_config_window)

        self.event_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.event_menu.add_command(label="New Event                   (Ctrl+F)", command=self.open_new_event_window)
        self.event_menu.add_command(label="Move Event Up           (Ctrl+E)", command=self.move_group_up)
        self.event_menu.add_command(label="Move Event Down      (Ctrl+D)", command=self.move_group_down)
        self.event_menu.add_command(label="Toggle Highlight       (Ctrl+V)", command=self.toggle_event_highlight)
        self.event_menu.add_command(label="Transfer Event             (Ctrl+R)", command=self.open_transfer_event_window)
        self.event_menu.add_command(label="Delete Event             (Ctrl+B)", command=self.delete_group)

        self.folder_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.folder_menu.add_command(label="New Folder                   (Ctrl+Q)", command=self.open_new_folder_window)
        self.folder_menu.add_command(label="Rename Cur Folder       (Ctrl+W)", command=self.rename_folder)

        self.export_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.export_menu.add_command(label="Export           (Ctrl+Shift+E)", command=self.open_export_window)
        self.export_menu.add_command(label="Quick Run    (Ctrl+Shift+R)", command=self.just_export_and_run)

        self.top_menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.top_menu_bar.add_cascade(label="Events", menu=self.event_menu)
        self.top_menu_bar.add_cascade(label="Folders", menu=self.folder_menu)
        self.top_menu_bar.add_cascade(label="RouteOne", menu=self.export_menu)

        # main container for everything to sit in... might be unnecessary?
        self.primary_window = tk.Frame(self)
        self.primary_window.pack(fill=tk.BOTH, expand=True)

        # create top row, which goes across the whole screen
        self.top_row = tk.Frame(self.primary_window)
        self.top_row.pack(fill=tk.X)
        self.top_row.pack_propagate(False)

        self.run_status_label = tk.Label(self.top_row, text="Run Status: Valid", background=const.VALID_COLOR, anchor=tk.W, padx=10, pady=10)
        self.run_status_label.grid(row=0, column=0, sticky=tk.W)

        self.route_version = tk.Label(self.top_row, text="RBY Version", anchor=tk.W, padx=10, pady=10)
        self.route_version.grid(row=0, column=1)

        self.route_name_label = tk.Label(self.top_row, text="Route Name: ")
        self.route_name_label.grid(row=0, column=2)

        self.route_name = tk.Entry(self.top_row)
        self.route_name.grid(row=0, column=3)
        self.route_name.config(width=30)

        self.message_label = custom_tkinter.AutoClearingLabel(self.top_row, width=100, justify=tk.LEFT, anchor=tk.W)
        self.message_label.grid(row=0, column=4, sticky=tk.E)

        # create container for split columns
        self.info_panel = tk.Frame(self.primary_window)
        self.info_panel.pack(expand=True, fill=tk.BOTH)

        # left panel for controls and event list
        self.left_info_panel = tk.Frame(self.info_panel)
        self.left_info_panel.grid(row=0, column=0, sticky="nsew")

        self.top_left_controls = tk.Frame(self.left_info_panel)
        self.top_left_controls.pack(fill=tk.X, anchor=tk.CENTER)

        self.trainer_add = quick_add_components.QuickTrainerAdd(
            self._controller,
            self.top_left_controls,
            trainer_select_callback=self.trainer_add_preview,
        )
        self.trainer_add.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        self.item_add = quick_add_components.QuickItemAdd(
            self._controller,
            self.top_left_controls,
        )
        self.item_add.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        self.wild_pkmn_add = quick_add_components.QuickWildPkmn(
            self._controller,
            self.top_left_controls,
        )
        self.wild_pkmn_add.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)

        self.group_controls = tk.Frame(self.left_info_panel)
        self.group_controls.pack(fill=tk.X, anchor=tk.CENTER)
        
        self.move_group_up_button = custom_tkinter.SimpleButton(self.group_controls, text='Move Event Up', command=self.move_group_up, width=15)
        self.move_group_up_button.grid(row=0, column=1, padx=5, pady=1)
        self.move_group_down_button = custom_tkinter.SimpleButton(self.group_controls, text='Move Event Down', command=self.move_group_down, width=15)
        self.move_group_down_button.grid(row=0, column=2, padx=5, pady=1)
        self.move_group_down_button = custom_tkinter.SimpleButton(self.group_controls, text='Toggle Highlight', command=self.toggle_event_highlight, width=15)
        self.move_group_down_button.grid(row=0, column=3, padx=5, pady=1)
        self.transfer_event_button = custom_tkinter.SimpleButton(self.group_controls, text='Transfer Event', command=self.open_transfer_event_window, width=15)
        self.transfer_event_button.grid(row=0, column=4, padx=5, pady=1)

        self.delete_event_button = custom_tkinter.SimpleButton(self.group_controls, text='Delete Event', command=self.delete_group, width=15)
        self.delete_event_button.grid(row=0, column=6, padx=5, pady=1)

        self.new_folder_button = custom_tkinter.SimpleButton(self.group_controls, text='New Folder', command=self.open_new_folder_window, width=15)
        self.new_folder_button.grid(row=0, column=8, padx=5, pady=1)
        self.rename_folder_button = custom_tkinter.SimpleButton(self.group_controls, text='Rename Folder', command=self.rename_folder, width=15)
        self.rename_folder_button.grid(row=0, column=9, padx=5, pady=1)

        self.group_controls.columnconfigure(0, weight=1)
        self.group_controls.columnconfigure(5, weight=1)
        self.group_controls.columnconfigure(7, weight=1)
        self.group_controls.columnconfigure(11, weight=1)

        self.event_list = pkmn_components.RouteList(self._controller, self.left_info_panel)
        self.scroll_bar = tk.Scrollbar(self.left_info_panel, orient="vertical", command=self.event_list.yview, width=30)

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
        self.bind('<Control-f>', self.open_new_event_window)
        self.bind('<Control-d>', self.move_group_down)
        self.bind('<Control-e>', self.move_group_up)
        self.bind('<Control-v>', self.toggle_event_highlight)
        self.bind('<Control-r>', self.open_transfer_event_window)
        self.bind('<Control-b>', self.delete_group)
        self.bind('<Delete>', self.delete_group)
        # folder actions
        self.bind('<Control-q>', self.open_new_folder_window)
        self.bind('<Control-w>', self.rename_folder)
        # route One integrations
        self.bind('<Control-E>', self.open_export_window)
        self.bind('<Control-R>', self.just_export_and_run)
        # config integrations
        self.bind('<Control-D>', self.open_config_window)
        self.bind('<Control-Z>', self.open_app_config_window)
        # detail update function
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<<TreeviewSelect>>", self._report_new_selection)
        self.bind(const.ROUTE_LIST_REFRESH_EVENT, self.update_run_status)
        self.bind(const.FORCE_QUIT_EVENT, self.cancel_and_quit)

        self._controller.register_event_selection(self._handle_new_selection)
        self._controller.register_version_change(self.update_run_version)
        self._controller.register_exception_callback(self._on_exception)
        self._controller.register_name_change(self._on_name_change)
        # TODO: should this be moved directly to the event list class?
        self._controller.register_route_change(self.event_list.refresh)

        self.event_list.refresh()
        self.new_event_window = None

    def run(self):
        self.mainloop()
    
    def _on_close(self, *args, **kwargs):
        # just need to save window geometry before closing
        config.set_window_geometry(self.geometry())
        self.destroy()
    
    def _on_exception(self, exception):
        #messagebox.showerror("Error!", "Failed to load route.\nThis can happen if the file is corrupted, or from a much older version")
        messagebox.showerror("Error!", f"Exception encountered ({type(exception)}): {exception}")
    
    def _on_name_change(self):
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
            self.run_status_label.config(text="Run Status: Invalid", bg=const.ERROR_COLOR)
        else:
            self.run_status_label.config(text="Run Status: Valid", bg=const.VALID_COLOR)
    
    def update_run_version(self, *args, **kwargs):
        self.route_version.config(
            text=f"{self._controller.get_version()} Version",
            background=const.VERSION_COLORS.get(self._controller.get_version(), "white")
        )
    
    def trainer_add_preview(self, trainer_name):
        # TODO: should migrate this to use the controller...
        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) > 1:
            return

        init_state = self._controller.get_state_after(
            previous_event_id=None if len(all_event_ids) == 0 else all_event_ids[0]
        )

        # create a fake event_def just so we can show the trainer that the user is looking at
        # TODO: just using the init_state as the post_event state as well. Ideally would like to use None for an empty state, but that's not currently supported
        self.event_details.show_event_details(
            EventDefinition(trainer_def=TrainerEventDefinition(trainer_name)),
            init_state,
            init_state,
            allow_updates=False
        )
    
    def _report_new_selection(self, *args, **kwargs):
        # this is different from _handle_new_selection as we are reporting the new selection
        # from the users action (via a tk event) to the controller
        # _handle_new_selection will respond to the controller's event about the selection changing
        self._controller.select_new_events(self.event_list.get_all_selected_event_ids())
    
    def _handle_new_selection(self, *args, **kwargs):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        # slightly weird behavior, but intentional. If only one element is selected,
        # we want to allow that element to be an EventItem, so that we can display the details.
        # But if multiple elements are selected, we want to ignore EventItems since they can't be bulk-edited
        if len(all_event_ids) > 1:
            all_event_ids = self.event_list.get_all_selected_event_ids(allow_event_items=False)

        if len(all_event_ids) > 1 or len(all_event_ids) == 0:
            event_group = None
        else:
            event_group = self._controller.get_event_by_id(all_event_ids[0])

        if event_group is None:
            self.event_details.show_event_details(None, self._controller.get_init_state(), self._controller.get_final_state(), allow_updates=False)
            self.rename_folder_button.disable()
            if self._controller.is_empty():
                self.new_folder_button.enable()
                self.delete_event_button.disable()
                self.transfer_event_button.disable()
            else:
                self.new_folder_button.disable()
                if len(all_event_ids) == 0:
                    self.delete_event_button.disable()
                    self.transfer_event_button.disable()
                    self.move_group_down_button.disable()
                    self.move_group_up_button.disable()
                else:
                    self.delete_event_button.enable()
                    self.transfer_event_button.enable()
                    self.move_group_down_button.enable()
                    self.move_group_up_button.enable()
        elif isinstance(event_group, EventFolder):
            self.event_details.show_event_details(event_group.event_definition, event_group.init_state, event_group.final_state)
            self.rename_folder_button.enable()
            self.transfer_event_button.enable()
            self.new_folder_button.enable()
            self.move_group_down_button.enable()
            self.move_group_up_button.enable()
            self.delete_event_button.enable()
        else:
            do_allow_updates = (
                 isinstance(event_group, EventGroup) or 
                 event_group.event_definition.get_event_type() == const.TASK_LEARN_MOVE_LEVELUP
            )
            trainer_event_group = event_group
            if isinstance(trainer_event_group, EventItem):
                trainer_event_group = trainer_event_group.parent
            self.event_details.show_event_details(event_group.event_definition, event_group.init_state, event_group.final_state, do_allow_updates, event_group=trainer_event_group)
            self.rename_folder_button.disable()
            if isinstance(event_group, EventItem):
                self.delete_event_button.disable()
                self.transfer_event_button.disable()
                self.new_folder_button.disable()
                self.move_group_down_button.disable()
                self.move_group_up_button.disable()
            else:
                self.delete_event_button.enable()
                self.transfer_event_button.enable()
                self.new_folder_button.enable()
                self.move_group_down_button.enable()
                self.move_group_up_button.enable()
    
    def open_app_config_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = DataDirConfigWindow(self, self.cancel_and_quit)
    
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

    def open_new_event_window(self, *args, **kwargs):
        if self._is_active_window():
            all_event_ids = self.event_list.get_all_selected_event_ids()
            if len(all_event_ids) > 1 or len(all_event_ids) == 0:
                return

            event_id = all_event_ids[0]
            event_obj = self._controller.get_event_by_id(event_id)
            if event_obj is None:
                return

            state = event_obj.init_state
            self.new_event_window = NewEventWindow(
                self,
                self._controller,
                self._controller.get_defeated_trainers(),
                state,
                insert_after=event_id
            )

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

    def combined_open_new_event_window(self, *args, **kwargs):
        if self._is_active_window():
            all_event_ids = self.event_list.get_all_selected_event_ids()
            if len(all_event_ids) > 1 or len(all_event_ids) == 0:
                return

            event_id = all_event_ids[0]
            event_obj = self._controller.get_event_by_id(event_id)

            if isinstance(event_obj, EventFolder):
                if const.EVENT_FOLDER_NAME in kwargs:
                    existing_folder_name = kwargs.get(const.EVENT_FOLDER_NAME)
                else:
                    existing_folder_name = None
                self.new_event_window = NewFolderWindow(
                    self,
                    self._controller,
                    self._controller.get_all_folder_names(),
                    existing_folder_name,
                    insert_after=event_id
                )
            else:
                if event_obj is None:
                    state = self._controller.get_final_state()
                else:
                    state = event_obj.init_state

                self.new_event_window = NewEventWindow(
                    self,
                    self._controller,
                    self._controller.get_defeated_trainers(),
                    state,
                    insert_after=event_id
                )
    
    def just_export_and_run(self, *args, **kwargs):
        try:
            if self._controller.get_init_state() is None:
                self.message_label.set_message(f"Cannot export when no route is loaded")

            jar_path = config.get_route_one_path()
            if not jar_path:
                config_path, _, _ = route_one_utils.export_to_route_one(self._controller.get_raw_route(), self.route_name.get())
                self.message_label.set_message(f"Could not run RouteOne, jar path not set. Exported RouteOne files: {config_path}")
            else:
                config_path, _, out_path = route_one_utils.export_to_route_one(self._controller.get_raw_route(), self.route_name.get())
                result = route_one_utils.run_route_one(jar_path, config_path)
                if not result:
                    self.message_label.set_message(f"Ran RouteOne successfully. Result file: {out_path}")
        except Exception as e:
            self.message_label.set_message(f"Exception attempting to export and run: {type(e)}: {e}")

    def open_export_window(self, event=None):
        if self._is_active_window():
            self.new_event_window = RouteOneWindow(self, self.route_name.get())

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
