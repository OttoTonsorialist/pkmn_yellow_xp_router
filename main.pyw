import argparse
import os
import time
import subprocess
import sys
import threading
import logging
import json

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, font, messagebox

from gui import custom_tkinter, route_event_components, pkmn_components, quick_add_components
from gui.event_details import EventDetails
from pkmn.universal_data_objects import StatBlock
from utils.constants import const
from utils.config_manager import config
from utils import route_one_utils, io_utils, auto_update, custom_logging
import pkmn
from routing.route_events import EventDefinition, EventFolder, EventGroup, EventItem, InventoryEventDefinition, TrainerEventDefinition, WildPkmnEventDefinition
import routing.router as router


if not os.path.exists(const.GLOBAL_CONFIG_FILE) or not os.path.exists(const.GLOBAL_CONFIG_DIR):
    # First time setup. Just need to create a few folders
    # TODO: proper error handling...? Idk man
    os.makedirs(const.GLOBAL_CONFIG_DIR)
    if not os.path.exists(config.get_user_data_dir()):
        os.makedirs(config.get_user_data_dir())


custom_logging.config_logging(const.GLOBAL_CONFIG_DIR)
logger = logging.getLogger(__name__)
flag_to_auto_update = False


class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self._data = router.Router()

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
            self.top_left_controls,
            trainer_add_callback=self.quick_add_event,
            trainer_select_callback=self.trainer_add_preview,
            area_add_callback=self.add_area,
            router=self._data,
        )
        self.trainer_add.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        self.item_add = quick_add_components.QuickItemAdd(
            self.top_left_controls,
            event_creation_callback=self.quick_add_event
        )
        self.item_add.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        self.wild_pkmn_add = quick_add_components.QuickWildPkmn(
            self.top_left_controls,
            event_creation_callback=self.quick_add_event
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

        self.event_list = pkmn_components.RouteList(self._data, self.left_info_panel)
        self.scroll_bar = tk.Scrollbar(self.left_info_panel, orient="vertical", command=self.event_list.yview, width=30)

        # intentionally pack event list after scrollbar, so they're ordered correctly
        self.scroll_bar.pack(side="right", fill=tk.BOTH)
        self.event_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True, side="right")
        self.event_list.configure(yscrollcommand=self.scroll_bar.set)

        # right panel for event details
        self.event_details = EventDetails(self.info_panel, event_update_callback=self.update_existing_event)
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
        self.bind("<<TreeviewSelect>>", self._handle_new_selection)
        self.bind(const.ROUTE_LIST_REFRESH_EVENT, self.update_run_status)
        self.bind(const.FORCE_QUIT_EVENT, self.cancel_and_quit)

        self.event_list.refresh()
        self.new_event_window = None

    def run(self):
        self.mainloop()
    
    def _on_close(self, *args, **kwargs):
        # just need to save window geometry before closing
        config.set_window_geometry(self.geometry())
        self.destroy()

    def save_route(self, *args, **kwargs):
        route_name = self.route_name.get()
        self._data.save(route_name)
        self.message_label.set_message(f"Successfully saved route: {route_name}")
    
    def export_notes(self, *args, **kwargs):
        self.message_label.set_message(f"Exported notes to: {self._data.export_notes(self.route_name.get())}")

    def load_custom_font(self):
        if config.get_custom_font_name() in font.families():
            defaultFont = font.nametofont("TkDefaultFont")
            defaultFont.configure(family=config.get_custom_font_name())
        else:
            defaultFont = font.nametofont("TkDefaultFont")
            defaultFont.configure(family=config.DEFAULT_FONT_NAME)

    def update_run_status(self, *args, **kwargs):
        if self._data.root_folder.has_errors():
            self.run_status_label.config(text="Run Status: Invalid", bg=const.ERROR_COLOR)
        else:
            self.run_status_label.config(text="Run Status: Valid", bg=const.VALID_COLOR)
    
    def update_run_version(self, *args, **kwargs):
        bg_color =const.VERSION_COLORS.get(self._data.pkmn_version, "white")

        self.route_version.config(text=f"{self._data.pkmn_version} Version", background=bg_color)
        self.trainer_add.update_pkmn_version()
        self.wild_pkmn_add.update_pkmn_version()
        self.item_add.update_pkmn_version()

    def update_quick_add_buttons(self, allow_enable):
        self.trainer_add.update_button_status(allow_enable=allow_enable)
        self.wild_pkmn_add.update_button_status(allow_enable=allow_enable)
        self.item_add.update_button_status(allow_enable=allow_enable)
    
    def trainer_add_preview(self, trainer_name):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) > 1:
            return

        if len(all_event_ids) == 0:
            init_state = self._data.init_route_state
        else:
            event_obj = self._data.get_event_obj(all_event_ids[0])
            if event_obj is None:
                init_state = self._data.init_route_state
            else:
                init_state = event_obj.init_state

        # create a fake event_def just so we can show the trainer that the user is looking at
        # TODO: just using the init_state as the post_event state as well. Ideally would like to use None for an empty state, but that's not currently supported
        self.event_details.show_event_details(
            EventDefinition(trainer_def=TrainerEventDefinition(trainer_name)),
            init_state,
            init_state,
            allow_updates=False
        )
    
    def _handle_new_selection(self, *args, **kwargs):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        # slightly weird behavior, but intentional. If only one element is selected,
        # we want to allow that element to be an EventItem, so that we can display the details.
        # But if multiple elements are selected, we want to ignore EventItems since they can't be bulk-edited
        if len(all_event_ids) > 1:
            all_event_ids = self.event_list.get_all_selected_event_ids(allow_event_items=False)

        if len(all_event_ids) > 1 or len(all_event_ids) == 0:
            event_group = None
            # allow adding if entire route is empty
            self.update_quick_add_buttons(len(self._data.root_folder.children) == 0)
        else:
            event_group = self._data.get_event_obj(all_event_ids[0])
            self.update_quick_add_buttons((event_group is not None) and (not isinstance(event_group, EventItem)))

        if event_group is None:
            self.event_details.show_event_details(None, self._data.init_route_state, self._data.get_final_state(), allow_updates=False)
            self.rename_folder_button.disable()
            self.item_add.cur_state = None
            if len(self._data.root_folder.children) == 0:
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
            self.item_add.cur_state = event_group.init_state
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
            self.item_add.cur_state = event_group.init_state

    def update_existing_event(self, new_event):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) > 1 or len(all_event_ids) == 0:
            return

        self._data.replace_event_group(all_event_ids[0], new_event)
        self.event_list.refresh()
        self._handle_new_selection()
    
    def add_area(self, area_name, include_rematches):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) > 1 or len(all_event_ids) == 0:
            return

        self._data.add_area(
            area_name=area_name,
            insert_after=all_event_ids[0],
            include_rematches=include_rematches
        )
        self.trainer_add.trainer_filter_callback()
        self.event_list.refresh()
    
    def quick_add_event(self, new_event):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) > 1 or len(all_event_ids) == 0:
            self._data.add_event_object(
                event_def=new_event
            )
        else:
            self._data.add_event_object(
                event_def=new_event,
                insert_after=all_event_ids[0]
            )

        self.trainer_add.trainer_filter_callback()
        self.event_list.refresh()

    def open_app_config_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = DataDirConfigWindow(self)
    
    def open_config_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = ConfigWindow(self)
    
    def open_new_route_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = NewRouteWindow(self)
    
    def create_new_route(self, solo_mon, base_route_path, pkmn_version, custom_dvs=None):
        if base_route_path == const.EMPTY_ROUTE_NAME:
            base_route_path = None
        
        self.new_event_window.close()
        self.new_event_window = None
        self.route_name.delete(0, tk.END)

        try:
            self._data.new_route(solo_mon, base_route_path, pkmn_version=pkmn_version, custom_dvs=custom_dvs)
        except Exception as e:
            logger.error(f"Exception ocurred trying to copy route: {base_route_path}")
            logger.exception(e)
            messagebox.showerror("Error!", "Failed to copy route.\nThis can happen if the route being copied is corrupted, or from a much older version")
            # load an empty route, just in case
            self._data.new_route(solo_mon)

        self.update_run_version()
        self.event_list.refresh()
        self._handle_new_selection()
    
    def open_load_route_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = LoadRouteWindow(self)

    def load_route(self, full_path_to_route):
        self.new_event_window.close()
        self.new_event_window = None
        self.route_name.delete(0, tk.END)

        try:
            _, route_name = os.path.split(full_path_to_route)
            route_name = os.path.splitext(route_name)[0]

            self._data.load(full_path_to_route)
            self.route_name.insert(0, route_name)
        except Exception as e:
            logger.error(f"Exception ocurred trying to load route: {full_path_to_route}")
            logger.exception(e)
            messagebox.showerror("Error!", "Failed to load route.\nThis can happen if the file is corrupted, or from a much older version")
            # load an empty route, just in case
            self._data.new_route("Abra")

        self.update_run_version()
        self.event_list.refresh()
        self._handle_new_selection()

    def open_customize_dvs_window(self, *args, **kwargs):
        if self._is_active_window() and self._data.init_route_state is not None:
            self.new_event_window = CustomDvsWindow(self, self._data.init_route_state.solo_pkmn.dvs)
    
    def customize_dvs(self, new_dvs):
        self.new_event_window.close()
        self.new_event_window = None
        self._data.change_current_dvs(new_dvs)
        self.event_list.refresh()
        self._handle_new_selection()

    def move_group_up(self, event=None):
        for cur_event in self.event_list.get_all_selected_event_ids(allow_event_items=False):
            self._data.move_event_object(cur_event, True)

        self.event_list.refresh()

    def move_group_down(self, event=None):
        # NOTE: have to reverse the list since we move items one at a time
        for cur_event in reversed(self.event_list.get_all_selected_event_ids(allow_event_items=False)):
            self._data.move_event_object(cur_event, False)

        self.event_list.refresh()

    def toggle_event_highlight(self, event=None):
        for cur_event in self.event_list.get_all_selected_event_ids(allow_event_items=False):
            self._data.toggle_event_highlight(cur_event)

        self.event_list.refresh()

    def delete_group(self, event=None):
        all_event_ids = self.event_list.get_all_selected_event_ids(allow_event_items=False)
        if len(all_event_ids) == 0:
            return
        
        do_prompt = False
        if len(all_event_ids) == 1:
            cur_event_id = all_event_ids[0]
            event_obj = self._data.get_event_obj(cur_event_id)
            if isinstance(event_obj, EventFolder) and len(event_obj.children) > 0:
                do_prompt = True
        else:
            do_prompt = True
        
        if do_prompt:
            if self._is_active_window():
                self.new_event_window = DeleteConfirmation(self, len(all_event_ids) == 1)
        else:
            # only don't prompt when deleting a single event (or empty folder)
            self._data.remove_event_object(all_event_ids[0])
            self.event_list.refresh()
            self.trainer_add.trainer_filter_callback()
    
    def confirmed_delete(self):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) == 0:
            return

        self._data.batch_remove_events(all_event_ids)
        self.new_event_window.close()
        self.new_event_window = None
        self.event_list.refresh()
        self.trainer_add.trainer_filter_callback()

    def finalize_new_folder(self, new_folder_name, prev_folder_name=None):
        all_event_ids = self.event_list.get_all_selected_event_ids(allow_event_items=False)
        if len(all_event_ids) > 1:
            return

        if prev_folder_name is None:
            if len(all_event_ids) == 0:
                self._data.add_event_object(new_folder_name=new_folder_name)
            else:
                self._data.add_event_object(new_folder_name=new_folder_name, insert_after=all_event_ids[0])
        else:
            self._data.rename_event_folder(prev_folder_name, new_folder_name)

        self.new_event_window.close()
        self.new_event_window = None
        self.event_list.refresh()

    def open_transfer_event_window(self, event=None):
        if self._is_active_window():
            all_event_ids = self.event_list.get_all_selected_event_ids(allow_event_items=False)
            if len(all_event_ids) == 0:
                return

            invalid_folders = set()
            for cur_event_id in all_event_ids:
                for cur_invalid in self._data.get_invalid_folder_transfers(cur_event_id):
                    invalid_folders.add(cur_invalid)
            
            self.new_event_window = TransferEventWindow(
                self,
                list(self._data.folder_lookup.keys()),
                [x for x in self._data.folder_lookup.keys() if x not in invalid_folders]
            )
    
    def transfer_to_folder(self, new_folder_name):
        all_event_ids = self.event_list.get_all_selected_event_ids(allow_event_items=False)
        if len(all_event_ids) == 0:
            return

        self._data.transfer_events(all_event_ids, new_folder_name)
        self.new_event_window.close()
        self.new_event_window = None
        self.event_list.refresh()

    def rename_folder(self, *args, **kwargs):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) > 1 or len(all_event_ids) == 0:
            return

        self.open_new_folder_window(**{const.EVENT_FOLDER_NAME: self._data.get_event_obj(all_event_ids[0]).name})

    def open_new_event_window(self, *args, **kwargs):
        if self._is_active_window():
            all_event_ids = self.event_list.get_all_selected_event_ids()
            if len(all_event_ids) > 1 or len(all_event_ids) == 0:
                return

            event_id = all_event_ids[0]
            event_obj = self._data.get_event_obj(event_id)
            if event_obj is None:
                return

            state = event_obj.init_state
            self.new_event_window = NewEventWindow(self, self._data.defeated_trainers, state)

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
                list(self._data.folder_lookup.keys()),
                existing_folder_name,
            )

    def combined_open_new_event_window(self, *args, **kwargs):
        if self._is_active_window():
            all_event_ids = self.event_list.get_all_selected_event_ids()
            if len(all_event_ids) > 1 or len(all_event_ids) == 0:
                return

            event_id = all_event_ids[0]
            event_obj = self._data.get_event_obj(event_id)

            if isinstance(event_obj, EventFolder):
                if const.EVENT_FOLDER_NAME in kwargs:
                    existing_folder_name = kwargs.get(const.EVENT_FOLDER_NAME)
                else:
                    existing_folder_name = None
                self.new_event_window = NewFolderWindow(
                    self,
                    list(self._data.folder_lookup.keys()),
                    existing_folder_name,
                )
            else:
                if event_obj is None:
                    state = self._data.get_final_state()
                else:
                    state = event_obj.init_state

                self.new_event_window = NewEventWindow(self, self._data.defeated_trainers, state)
    
    def just_export_and_run(self, *args, **kwargs):
        try:
            if self._data.init_route_state is None:
                self.message_label.set_message(f"Cannot export when no route is loaded")

            jar_path = config.get_route_one_path()
            if not jar_path:
                config_path, _, _ = route_one_utils.export_to_route_one(self._data, self.route_name.get())
                self.message_label.set_message(f"Could not run RouteOne, jar path not set. Exported RouteOne files: {config_path}")
            else:
                config_path, _, out_path = route_one_utils.export_to_route_one(self._data, self.route_name.get())
                result = route_one_utils.run_route_one(jar_path, config_path)
                if not result:
                    self.message_label.set_message(f"Ran RouteOne successfully. Result file: {out_path}")
        except Exception as e:
            self.message_label.set_message(f"Exception attempting to export and run: {type(e)}: {e}")

    def open_export_window(self, event=None):
        if self._is_active_window():
            self.new_event_window = RouteOneWindow(self, self.route_name.get())

    def cancel_new_event(self, event=None):
        if self.new_event_window is not None:
            self.new_event_window.close()
            self.new_event_window = None

    def cancel_and_quit(self, *args, **kwargs):
        if self.new_event_window is not None:
            self.new_event_window.close()
            self.new_event_window = None
        self.destroy()
    
    def new_event(self, event_def):
        all_event_ids = self.event_list.get_all_selected_event_ids()
        if len(all_event_ids) > 1 or len(all_event_ids) == 0:
            return

        self._data.add_event_object(event_def=event_def, insert_after=all_event_ids[0])
        self.new_event_window.close()
        self.new_event_window = None
        self.event_list.refresh()
    
    def _is_active_window(self):
        # returns true if the current window is active (i.e. no sub-windows exist)
        if self.new_event_window is not None and tk.Toplevel.winfo_exists(self.new_event_window):
            return False
        return True


class DataDirConfigWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, *args, first_time_setup=False, **kwargs):
        super().__init__(main_window, *args, **kwargs)

        self.first_time_setup = first_time_setup
        self._data_dir_changed = False
        self._thread = None
        self._new_app_version = None
        self._new_asset_url = None

        self.padx = 5
        self.pady = 5
        self.app_info_frame = tk.Frame(self)
        self.app_info_frame.pack(padx=self.padx, pady=(2 * self.pady))
        self.data_location_frame = tk.Frame(self)
        self.data_location_frame.pack(padx=self.padx, pady=(4 * self.pady, 2 * self.pady))

        self.app_version_label = tk.Label(self.app_info_frame, text="App Version:")
        self.app_version_label.grid(row=0, column=0)
        self.app_version_value = tk.Label(self.app_info_frame, text=const.APP_VERSION)
        self.app_version_value.grid(row=0, column=1)

        self.app_release_date_label = tk.Label(self.app_info_frame, text="Release Date:")
        self.app_release_date_label.grid(row=1, column=0)
        self.app_release_date_value = tk.Label(self.app_info_frame, text=const.APP_RELEASE_DATE)
        self.app_release_date_value.grid(row=1, column=1)

        self._windows_label = tk.Label(self.app_info_frame, text="Automatic updates only supported on windows machines")
        self._windows_label.grid(row=5, column=0, columnspan=2, padx=self.padx, pady=(2 * self.pady, self.pady))
        self._latest_version_label = tk.Label(self.app_info_frame, text="Fetching newest version...")
        self._latest_version_label.grid(row=6, column=0, columnspan=2)
        self._check_for_updates_button = custom_tkinter.SimpleButton(self.app_info_frame, text="No Upgrade Needed", command=self._kick_off_auto_update)
        self._check_for_updates_button.grid(row=7, column=0, columnspan=2)
        self._check_for_updates_button.disable()

        self.data_location_value = tk.Label(self.data_location_frame, text=f"Data Location: {config.get_user_data_dir()}")
        self.data_location_value.grid(row=15, column=0, columnspan=2)
        self.data_location_label = custom_tkinter.SimpleButton(self.data_location_frame, text="Open Data Folder", command=self.open_data_location)
        self.data_location_label.grid(row=16, column=0)
        self.data_location_change_button = custom_tkinter.SimpleButton(self.data_location_frame, text="Move Data Location", command=self.change_data_location)
        self.data_location_change_button.grid(row=16, column=1)

        self.app_location_button = custom_tkinter.SimpleButton(self.data_location_frame, text="Open Config/Logs Folder", command=self.open_global_config_location)
        self.app_location_button.grid(row=17, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.close_button = custom_tkinter.SimpleButton(self, text="Close", command=self._final_cleanup)
        self.close_button.pack(padx=self.padx, pady=self.pady)

        self.bind('<Return>', self._final_cleanup)
        self.bind('<Escape>', self._final_cleanup)
        self._thread = threading.Thread(target=self._get_new_updates_info)
        self._thread.start()
    
    def _final_cleanup(self, *args, **kwargs):
        if self.first_time_setup and not self._data_dir_changed:
            io_utils.change_user_data_location(None, config.get_user_data_dir())
        self._thread.join()
        self._main_window.cancel_new_event()
    
    def _get_new_updates_info(self, *args, **kwargs):
        self._new_app_version, self._new_asset_url = auto_update.get_new_version_info()
        self._latest_version_label.configure(text=f"Newest Version: {self._new_app_version}")
        if auto_update.is_upgrade_needed(self._new_app_version):
            self._check_for_updates_button.configure(text="Upgrade")
            self._check_for_updates_button.enable()
    
    def _kick_off_auto_update(self, *args, **kwargs):
        global flag_to_auto_update
        flag_to_auto_update = True
        self._thread.join()
        self._main_window.cancel_and_quit()

    def open_global_config_location(self, *args, **kwargs):
        io_utils.open_explorer(const.GLOBAL_CONFIG_DIR)

    def open_data_location(self, *args, **kwargs):
        io_utils.open_explorer(config.get_user_data_dir())

    def change_data_location(self, *args, **kwargs):
        valid_path_found = False
        while not valid_path_found:
            file_result = filedialog.askdirectory(initialdir=config.get_user_data_dir(), mustexist=False)
            if not file_result:
                self.lift()
                return

            new_path = os.path.realpath(file_result)
            if os.path.realpath(const.SOURCE_ROOT_PATH) in new_path:
                messagebox.showerror("Error", "Cannot place the data dir inside the app, as it will be removed during automatic updates")
            else:
                valid_path_found = True

        if io_utils.change_user_data_location(config.get_user_data_dir(), new_path):
            config.set_user_data_dir(new_path)
            self.data_location_value.config(text=new_path)
        else:
            messagebox.showerror("Error", "Failed to change user data location...")

        self.lift()


class CustomDvsWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, init_dvs:StatBlock, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs, width=400)

        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        self.custom_dvs_hp_label = tk.Label(self.controls_frame, text="HP DV:")
        self.custom_dvs_hp_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hp = custom_tkinter.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.hp, callback=self._recalc_hidden_power)
        self.custom_dvs_hp.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_atk_label = tk.Label(self.controls_frame, text="Attack DV:")
        self.custom_dvs_atk_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_atk = custom_tkinter.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.attack, callback=self._recalc_hidden_power)
        self.custom_dvs_atk.grid(row=1, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_def_label = tk.Label(self.controls_frame, text="Defense DV:")
        self.custom_dvs_def_label.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_def = custom_tkinter.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.defense, callback=self._recalc_hidden_power)
        self.custom_dvs_def.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spd_label = tk.Label(self.controls_frame, text="Speed DV:")
        self.custom_dvs_spd_label.grid(row=3, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spd = custom_tkinter.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.speed, callback=self._recalc_hidden_power)
        self.custom_dvs_spd.grid(row=3, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spc_label = tk.Label(self.controls_frame, text="Special DV:")
        self.custom_dvs_spc_label.grid(row=4, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spc = custom_tkinter.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.special_attack, callback=self._recalc_hidden_power)
        self.custom_dvs_spc.grid(row=4, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_hidden_power_label = tk.Label(self.controls_frame, text="Hidden Power:")
        self.custom_dvs_hidden_power_label.grid(row=5, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hidden_power = tk.Label(self.controls_frame)
        self.custom_dvs_hidden_power.grid(row=5, column=1, padx=self.padx, pady=self.pady)


        self.create_button = custom_tkinter.SimpleButton(self.controls_frame, text="Set New DVs", command=self.set_dvs)
        self.create_button.grid(row=30, column=0, padx=self.padx, pady=self.pady)
        self.cancel_button = custom_tkinter.SimpleButton(self.controls_frame, text="Cancel", command=self._main_window.cancel_new_event)
        self.cancel_button.grid(row=30, column=1, padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.set_dvs)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self._recalc_hidden_power()
    
    def _recalc_hidden_power(self, *args, **kwargs):
        try:
            hp_type, hp_power = pkmn.current_gen_info().get_hidden_power(
                StatBlock(
                    int(self.custom_dvs_hp.get()),
                    int(self.custom_dvs_atk.get()),
                    int(self.custom_dvs_def.get()),
                    int(self.custom_dvs_spc.get()),
                    int(self.custom_dvs_spc.get()),
                    int(self.custom_dvs_spd.get())
                )
            )

            if not hp_type:
                self.custom_dvs_hidden_power.configure(text=f"Not supported in gen 1")
            else:
                self.custom_dvs_hidden_power.configure(text=f"{hp_type}: {hp_power}")
        except Exception as e:
            self.custom_dvs_hidden_power.configure(text=f"Failed to calculate, invalid DVs")

    def _get_custom_dvs(self, *args, **kwargs):
        return StatBlock(
            int(self.custom_dvs_hp.get()),
            int(self.custom_dvs_atk.get()),
            int(self.custom_dvs_def.get()),
            int(self.custom_dvs_spc.get()),
            int(self.custom_dvs_spc.get()),
            int(self.custom_dvs_spd.get())
        )
    
    def set_dvs(self, *args, **kwargs):
        self._main_window.customize_dvs(
            StatBlock(
                int(self.custom_dvs_hp.get()),
                int(self.custom_dvs_atk.get()),
                int(self.custom_dvs_def.get()),
                int(self.custom_dvs_spc.get()),
                int(self.custom_dvs_spc.get()),
                int(self.custom_dvs_spd.get())
            )
        )


class NewRouteWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs, width=400)

        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        self.pkmn_version_label = tk.Label(self.controls_frame, text="Pokemon Version:")
        self.pkmn_version_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.pkmn_version = custom_tkinter.SimpleOptionMenu(self.controls_frame, const.VERSION_LIST, callback=self._pkmn_version_callback)
        self.pkmn_version.config(width=20)
        self.pkmn_version.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.solo_selector_label = tk.Label(self.controls_frame, text="Solo Pokemon:")
        self.solo_selector_label.grid(row=1, column=0, padx=self.padx, pady=(4 * self.pady, self.pady))
        self.solo_selector = custom_tkinter.SimpleOptionMenu(self.controls_frame, [const.NO_POKEMON])
        self.solo_selector.config(width=20)
        self.solo_selector.grid(row=1, column=1, padx=self.padx, pady=(4 * self.pady, self.pady))

        self.pkmn_filter_label = tk.Label(self.controls_frame, text="Solo Pokemon Filter:")
        self.pkmn_filter_label.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.pkmn_filter = custom_tkinter.SimpleEntry(self.controls_frame, callback=self._pkmn_filter_callback)
        self.pkmn_filter.config(width=30)
        self.pkmn_filter.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        # need to create a local cache of all min battles due to all the version switching we're going to do
        self._min_battles_cache = [const.EMPTY_ROUTE_NAME]
        self.min_battles_selector_label = tk.Label(self.controls_frame, text="Base Route:")
        self.min_battles_selector_label.grid(row=3, column=0, padx=self.padx, pady=(4 * self.pady, self.pady))
        self.min_battles_selector = custom_tkinter.SimpleOptionMenu(self.controls_frame, self._min_battles_cache)
        self.min_battles_selector.grid(row=3, column=1, padx=self.padx, pady=(4 * self.pady, self.pady))

        self.min_battles_filter_label = tk.Label(self.controls_frame, text="Base Route Filter:")
        self.min_battles_filter_label.grid(row=4, column=0, padx=self.padx, pady=self.pady)
        self.min_battles_filter = custom_tkinter.SimpleEntry(self.controls_frame, callback=self._base_route_filter_callback)
        self.min_battles_filter.config(width=30)
        self.min_battles_filter.grid(row=4, column=1, padx=self.padx, pady=self.pady)

        self.max_dvs_flag = tk.BooleanVar()
        self.max_dvs_flag.set(True)
        self.max_dvs_flag.trace("w", self._custom_dvs_callback)
        self.custom_dvs_label = tk.Label(self.controls_frame, text="Max DVs?")
        self.custom_dvs_checkbox = tk.Checkbutton(self.controls_frame, variable=self.max_dvs_flag, onvalue=True, offvalue=False)
        self.custom_dvs_label.grid(row=5, column=0, padx=self.padx, pady=(4 * self.pady, self.pady))
        self.custom_dvs_checkbox.grid(row=5, column=1, padx=self.padx, pady=(4 * self.pady, self.pady))

        self.custom_dvs_frame = tk.Frame(self.controls_frame)

        self.custom_dvs_hp_label = tk.Label(self.custom_dvs_frame, text="HP DV:")
        self.custom_dvs_hp_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hp = custom_tkinter.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_hp.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_atk_label = tk.Label(self.custom_dvs_frame, text="Attack DV:")
        self.custom_dvs_atk_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_atk = custom_tkinter.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_atk.grid(row=1, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_def_label = tk.Label(self.custom_dvs_frame, text="Defense DV:")
        self.custom_dvs_def_label.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_def = custom_tkinter.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_def.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spd_label = tk.Label(self.custom_dvs_frame, text="Speed DV:")
        self.custom_dvs_spd_label.grid(row=3, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spd = custom_tkinter.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_spd.grid(row=3, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spc_label = tk.Label(self.custom_dvs_frame, text="Special DV:")
        self.custom_dvs_spc_label.grid(row=4, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spc = custom_tkinter.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_spc.grid(row=4, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_hidden_power_label = tk.Label(self.custom_dvs_frame, text="Hidden Power:")
        self.custom_dvs_hidden_power_label.grid(row=5, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hidden_power = tk.Label(self.custom_dvs_frame)
        self.custom_dvs_hidden_power.grid(row=5, column=1, padx=self.padx, pady=self.pady)


        self.warning_label = tk.Label(self.controls_frame, text="WARNING: Any unsaved changes in your current route\nwill be lost when creating a new route!", justify=tk.CENTER, anchor=tk.CENTER)
        self.warning_label.grid(row=29, column=0, columnspan=2, sticky=tk.EW, padx=self.padx, pady=self.pady)

        self.create_button = custom_tkinter.SimpleButton(self.controls_frame, text="Create Route", command=self.create)
        self.create_button.grid(row=30, column=0, padx=self.padx, pady=self.pady)
        self.cancel_button = custom_tkinter.SimpleButton(self.controls_frame, text="Cancel", command=self._main_window.cancel_new_event)
        self.cancel_button.grid(row=30, column=1, padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.create)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self._pkmn_version_callback()
        self.pkmn_filter.focus()
    
    def _recalc_hidden_power(self, *args, **kwargs):
        try:
            hp_type, hp_power = pkmn.specific_gen_info(self.pkmn_version.get()).get_hidden_power(
                StatBlock(
                    int(self.custom_dvs_hp.get()),
                    int(self.custom_dvs_atk.get()),
                    int(self.custom_dvs_def.get()),
                    int(self.custom_dvs_spc.get()),
                    int(self.custom_dvs_spc.get()),
                    int(self.custom_dvs_spd.get())
                )
            )

            if not hp_type:
                self.custom_dvs_hidden_power.configure(text=f"Not supported in gen 1")
            else:
                self.custom_dvs_hidden_power.configure(text=f"{hp_type}: {hp_power}")
        except Exception as e:
            self.custom_dvs_hidden_power.configure(text=f"Failed to calculate, invalid DVs")

    def _pkmn_version_callback(self, *args, **kwargs):
        # now that we've loaded the right version, repopulate the pkmn selector just in case
        temp_gen = pkmn.specific_gen_info(self.pkmn_version.get())
        self.solo_selector.new_values(temp_gen.pkmn_db().get_filtered_names(filter_val=self.pkmn_filter.get().strip()))

        all_routes = [const.EMPTY_ROUTE_NAME]
        for preset_route_name in temp_gen.min_battles_db().data:
            all_routes.append(const.PRESET_ROUTE_PREFIX + preset_route_name)

        for test_route in io_utils.get_existing_route_names():
            try:
                with open(io_utils.get_existing_route_path(test_route), 'r') as f:
                    raw = json.load(f)
                    if raw[const.PKMN_VERSION_KEY] == self.pkmn_version.get():
                        all_routes.append(test_route)
            except Exception as e:
                pass

        self._min_battles_cache = all_routes
        self._base_route_filter_callback()

    def _pkmn_filter_callback(self, *args, **kwargs):
        self.solo_selector.new_values(pkmn.specific_gen_info(self.pkmn_version.get()).pkmn_db().get_filtered_names(filter_val=self.pkmn_filter.get().strip()))

    def _base_route_filter_callback(self, *args, **kwargs):
        # NOTE: assume the _min_battles_cache is always accurate, and just filter it down as needed
        filter_val = self.min_battles_filter.get().strip().lower()
        new_vals = [x for x in self._min_battles_cache if filter_val in x.lower()]

        if not new_vals:
            new_vals = [const.EMPTY_ROUTE_NAME]

        self.min_battles_selector.new_values(new_vals)
    
    def _custom_dvs_callback(self, *args, **kwargs):
        if not self.max_dvs_flag.get():
            self.custom_dvs_frame.grid(row=5, column=0, columnspan=2)
            self._recalc_hidden_power()
        else:
            self.custom_dvs_frame.grid_forget()
    
    def _get_custom_dvs(self, *args, **kwargs):
        if self.max_dvs_flag.get():
            return None
        
        return {
            const.HP: int(self.custom_dvs_hp.get()),
            const.ATK: int(self.custom_dvs_atk.get()),
            const.DEF: int(self.custom_dvs_def.get()),
            const.SPD: int(self.custom_dvs_spd.get()),
            const.SPC: int(self.custom_dvs_spc.get()),
        }
    
    def create(self, *args, **kwargs):
        selected_base_route = self.min_battles_selector.get()
        if selected_base_route == const.EMPTY_ROUTE_NAME:
            selected_base_route = None
        elif selected_base_route.startswith(const.PRESET_ROUTE_PREFIX):
            temp_gen = pkmn.specific_gen_info(self.pkmn_version.get())
            selected_base_route = os.path.join(temp_gen.min_battles_db().get_dir(), selected_base_route[len(const.PRESET_ROUTE_PREFIX):] + ".json")
        else:
            selected_base_route = io_utils.get_existing_route_path(selected_base_route)
            
        self._main_window.create_new_route(
            self.solo_selector.get(),
            selected_base_route,
            self.pkmn_version.get(),
            self._get_custom_dvs()
        )


class LoadRouteWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)

        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        self.previous_route_label = tk.Label(self.controls_frame, text="Existing Routes:")
        self.previous_route_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.previous_route_names = custom_tkinter.SimpleOptionMenu(self.controls_frame, [const.NO_SAVED_ROUTES], callback=self._select_callback)
        self.previous_route_names.grid(row=0, column=1, padx=self.padx, pady=self.pady)
        self.previous_route_names.config(width=25)

        self.filter_label = tk.Label(self.controls_frame, text="Filter:")
        self.filter = custom_tkinter.SimpleEntry(self.controls_frame, callback=self._filter_callback)
        self.filter_label.grid(row=1, column=0)
        self.filter.grid(row=1, column=1)

        self.allow_oudated = tk.BooleanVar()
        self.allow_oudated.trace("w", self._filter_callback)
        self.outdated_label = tk.Label(self.controls_frame, text="Show Backup Routes?")
        self.outdated_checkbox = tk.Checkbutton(self.controls_frame, variable=self.allow_oudated, onvalue=True, offvalue=False)
        self.outdated_label.grid(row=2, column=0)
        self.outdated_checkbox.grid(row=2, column=1)

        self.outdated_info_label = tk.Label(self.controls_frame, text="Backup Routes are older versions of your route.\nEvery save makes a backup that is persisted, and can be reloaded if needed.\nThese are hidden by default because they can quickly pile up")
        self.outdated_info_label.grid(row=3, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.warning_label = tk.Label(self.controls_frame, text="WARNING: Any unsaved changes in your current route\nwill be lost when loading an existing route!")
        self.warning_label.grid(row=4, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.create_button = custom_tkinter.SimpleButton(self.controls_frame, text="Load Route", command=self.load)
        self.create_button.grid(row=10, column=0, padx=self.padx, pady=self.pady)
        self.cancel_button = custom_tkinter.SimpleButton(self.controls_frame, text="Cancel", command=self._main_window.cancel_new_event)
        self.cancel_button.grid(row=10, column=1, padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.load)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self.filter.focus()
        self._filter_callback()
        self._select_callback()

    def _filter_callback(self, *args, **kwargs):
        all_routes = io_utils.get_existing_route_names(
            filter_text=self.filter.get(),
            load_backups=self.allow_oudated.get()
        )

        if not all_routes:
            all_routes = [const.NO_SAVED_ROUTES]

        self.previous_route_names.new_values(all_routes)

    def _select_callback(self, *args, **kwargs):
        selected_route = self.previous_route_names.get()
        if selected_route == const.NO_SAVED_ROUTES:
            self.create_button.disable()
        else:
            self.create_button.enable()
    
    def load(self, *args, **kwargs):
        selected_route = self.previous_route_names.get()
        if selected_route == const.NO_SAVED_ROUTES:
            return
        self._main_window.load_route(io_utils.get_existing_route_path(self.previous_route_names.get()))


class NewFolderWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, cur_folder_names, prev_folder_name, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        if main_window is None:
            raise ValueError('Must set main_window when creating NewFolderWindow')
        
        self._cur_folder_names = cur_folder_names
        self._prev_folder_name = prev_folder_name

        self._label = tk.Label(self)
        self._folder_name = custom_tkinter.SimpleEntry(self, callback=self.folder_name_update)
        self._label.grid(row=0, column=0, padx=10, pady=10)
        self._folder_name.grid(row=0, column=1, padx=10, pady=10)
        self._add_button = custom_tkinter.SimpleButton(self, command=self.create)
        self._cancel_button = custom_tkinter.SimpleButton(self, text="Cancel", command=self._main_window.cancel_new_event)
        self._add_button.grid(row=1, column=0, padx=10, pady=10)
        self._cancel_button.grid(row=1, column=1, padx=10, pady=10)

        self.bind('<Return>', self.create)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self._folder_name.focus()

        if prev_folder_name is None:
            self.title("Create New Folder")
            self._label.configure(text="New Folder Name")
            self._add_button.configure(text="New Folder")
        else:
            self.title("Update Folder Name")
            self._label.configure(text="Update Folder Name")
            self._folder_name.set(prev_folder_name)
            self._add_button.configure(text="Update Folder")

    def folder_name_update(self, *args, **kwargs):
        cur_name = self._folder_name.get()
        if cur_name in self._cur_folder_names:
            self._add_button.disable()
        else:
            self._add_button.enable()
    
    def create(self, *args, **kwargs):
        cur_name = self._folder_name.get()
        if not cur_name:
            return
        elif cur_name in self._cur_folder_names:
            return

        self._main_window.finalize_new_folder(cur_name, prev_folder_name=self._prev_folder_name)


class DeleteConfirmation(custom_tkinter.Popup):
    def __init__(self, main_window: Main, is_nonempty_folder, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        if main_window is None:
            raise ValueError('Must set main_window when creating DeleteConfirmation')
        
        if is_nonempty_folder:
            text = "You are trying to delete a non-empty folder.\nAre you sure you want to delete the folder and all child events?"
        else:
            text = "You are trying to delete multiple items at once.\nAre you sure you want to delete all selected items?"
        
        self._label = tk.Label(self, text=text)
        self._label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self._confirm_button = custom_tkinter.SimpleButton(self, text="Delete", command=self.delete)
        self._cancel_button = custom_tkinter.SimpleButton(self, text="Cancel", command=self._main_window.cancel_new_event)
        self._confirm_button.grid(row=1, column=0, padx=10, pady=10)
        self._cancel_button.grid(row=1, column=1, padx=10, pady=10)

        self.bind('<Return>', self.delete)
        self.bind('<Escape>', self._main_window.cancel_new_event)

    def delete(self, *args, **kwargs):
        self._main_window.confirmed_delete()


class TransferEventWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, all_existing_folders, valid_dest_folders, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        if main_window is None:
            raise ValueError('Must set main_window when creating TransferEventWindow')
        
        self._all_existing_folders = all_existing_folders
        self._valid_dest_folders = valid_dest_folders

        self._transfer_type_label = tk.Label(self, text=f"Transfer to:")
        self._transfer_type = custom_tkinter.SimpleOptionMenu(self, option_list=[const.TRANSFER_EXISTING_FOLDER, const.TRANSFER_NEW_FOLDER], callback=self._transfer_type_callback)
        self._transfer_type_label.grid(row=0, column=0, padx=10, pady=10)
        self._transfer_type.grid(row=0, column=1, padx=10, pady=10)

        self._new_folder_label = tk.Label(self, text=f"New folder:")
        self._new_folder_name = custom_tkinter.SimpleEntry(self, callback=self._new_folder_callback)

        self._dest_folder_label = tk.Label(self, text=f"New folder:")
        self._dest_folder_name = custom_tkinter.SimpleOptionMenu(self, option_list=self.get_possible_folders())

        self.filter_label = tk.Label(self, text="Filter:")
        self.filter = custom_tkinter.SimpleEntry(self, callback=self._filter_callback)

        self._add_button = custom_tkinter.SimpleButton(self, command=self.transfer, text="Transfer to Folder")
        self._cancel_button = custom_tkinter.SimpleButton(self, text="Cancel", command=self._main_window.cancel_new_event)
        self._add_button.grid(row=3, column=0, padx=10, pady=10)
        self._cancel_button.grid(row=3, column=1, padx=10, pady=10)

        self.bind('<Return>', self.transfer)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self._transfer_type_callback()
        self.filter.focus()
    
    def get_possible_folders(self, filter_text=""):
        filter_text = filter_text.lower()
        result = [x for x in self._valid_dest_folders if filter_text in x.lower()]

        if not result:
            result = [const.NO_FOLDERS]

        return result
    
    def _transfer_type_callback(self, *args, **kwargs):
        if self._transfer_type.get() == const.TRANSFER_EXISTING_FOLDER:
            self._dest_folder_label.grid(row=1, column=0, padx=10, pady=10)
            self._dest_folder_name.grid(row=1, column=1, padx=10, pady=10)
            self.filter_label.grid(row=2, column=0, padx=10, pady=10)
            self.filter.grid(row=2, column=1, padx=10, pady=10)
            self._new_folder_label.grid_forget()
            self._new_folder_name.grid_forget()
            self._filter_callback()
        else:
            self._dest_folder_label.grid_forget()
            self._dest_folder_name.grid_forget()
            self.filter_label.grid_forget()
            self.filter.grid_forget()
            self._new_folder_label.grid(row=1, column=0, padx=10, pady=10)
            self._new_folder_name.grid(row=1, column=1, padx=10, pady=10)
            self._new_folder_callback()

    def _filter_callback(self, *args, **kwargs):
        dest_folder_vals = self.get_possible_folders(filter_text=self.filter.get())
        if const.NO_FOLDERS in dest_folder_vals:
            self._add_button.disable()
        else:
            self._add_button.enable()

        self._dest_folder_name.new_values(dest_folder_vals)

    def _new_folder_callback(self, *args, **kwargs):
        if self._new_folder_name.get() in self._all_existing_folders:
            self._add_button.disable()
        else:
            self._add_button.enable()
    
    def transfer(self, *args, **kwargs):
        if self._transfer_type.get() == const.TRANSFER_EXISTING_FOLDER:
            if self._dest_folder_name.get() != const.NO_FOLDERS:
                self._main_window.transfer_to_folder(self._dest_folder_name.get())
        else:
            if self._new_folder_name.get() not in self._all_existing_folders:
                self._main_window.transfer_to_folder(self._new_folder_name.get().strip())


class NewEventWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, cur_defeated_trainers, cur_state, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs, width=700, height=600)

        self.title("Create New Event")
        self._cur_defeated_trainers = cur_defeated_trainers
        self._cur_state = cur_state

        self._top_pane = tk.Frame(self)
        self._top_pane.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

        self._state_viewer = pkmn_components.StateViewer(self._top_pane)
        self._state_viewer.grid(row=0, column=0)
        self._state_viewer.set_state(cur_state)

        self._input_frame = tk.Frame(self._top_pane, width=700, height=600)
        self._input_frame.grid(row=1, column=0)
        self._input_frame.grid_propagate(False)

        # elements going inside the frame
        self._event_type_label = tk.Label(self._input_frame, text="Event:")
        self._event_type_label.grid(row=0, column=0)
        self._event_type = custom_tkinter.SimpleOptionMenu(self._input_frame, const.ROUTE_EVENT_TYPES, callback=self._event_type_callback)
        self._event_type.grid(row=0, column=1)

        self._create_new_event_button = custom_tkinter.SimpleButton(self, text="Add Event", command=self._new_event)
        self._create_new_event_button.grid(row=1, column=0)
        self._create_new_event_button.disable()

        self._cancel_button = custom_tkinter.SimpleButton(self, text="Cancel", command=self._main_window.cancel_new_event)
        self._cancel_button.grid(row=1, column=1)
        self._cancel_button.enable()

        self._event_editor_lookup = route_event_components.EventEditorFactory(self._input_frame, self._create_new_event_button)
        self._cur_editor = None

        self.bind('<Return>', self._new_event)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self._event_type.focus_set()
        self._event_type_callback()

    def _event_type_callback(self, *args, **kwargs):
        new_event_type = self._event_type.get()

        # otherwise, hide our current editor, and get the new one
        if self._cur_editor is not None:
            self._cur_editor.grid_remove()
        
        self._cur_editor = self._event_editor_lookup.get_editor(
            route_event_components.EditorParams(
                new_event_type,
                self._cur_defeated_trainers,
                self._cur_state,
            )
        )
        self._cur_editor.grid(row=1, column=0, columnspan=2)

    def _new_event(self, *args, **kwargs):
        self._main_window.new_event(self._cur_editor.get_event())


class RouteOneWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, cur_route_name, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        
        self._cur_route_name = cur_route_name

        if self._main_window._data.init_route_state is None:
            self._final_config_path = self._final_route_path = self._final_output_path = "Not Generated"
            route_one_results_init = "Cannot export when no route is loaded"
        else:
            self._final_config_path, self._final_route_path, self._final_output_path = \
                route_one_utils.export_to_route_one(self._main_window._data, self._cur_route_name)
            route_one_results_init = ""

        self._config_file_label = tk.Label(self, text=f"Config path: {self._final_config_path}")
        self._config_file_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self._route_file_label = tk.Label(self, text=f"Route path: {self._final_route_path}")
        self._route_file_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self._route_jar_label = tk.Label(self, text=f"RouteOne jar Path: {config.get_route_one_path()}")
        self._route_jar_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self._set_jar_button = custom_tkinter.SimpleButton(self, text=f"Set R1 jar path", command=self.set_jar_path)
        self._set_jar_button.grid(row=3, column=0, padx=10, pady=10)
        self._run_route_one_button = custom_tkinter.SimpleButton(self, text=f"Run RouteOne", command=self.run_route_one)
        self._run_route_one_button.grid(row=3, column=1, padx=10, pady=10)

        # TODO: gross, ugly, wtv
        if self._main_window._data.init_route_state is None:
            self._run_route_one_button.disable()

        self._route_one_results_label = tk.Label(self, text=route_one_results_init, justify=tk.CENTER)
        self._route_one_results_label.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

        self._close_button = custom_tkinter.SimpleButton(self, text="Close", command=self._main_window.cancel_new_event)
        self._close_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.bind('<Escape>', self._main_window.cancel_new_event)

    def set_jar_path(self, *args, **kwargs):
        file_result = filedialog.askopenfile()
        if file_result is None:
            self.lift()
            return
        jar_path = file_result.name
        self._route_jar_label.config(text=f"RouteOne jar Path: {jar_path}")
        config.set_route_one_path(jar_path)
        self.lift()

    def run_route_one(self, *args, **kwargs):
        if not config.get_route_one_path():
            self._route_one_results_label.config(text="No RouteOne jar path set, cannot run...")
            return
        
        result = route_one_utils.run_route_one(config.get_route_one_path(), self._final_config_path)
        if not result:
            self._route_one_results_label.config(text=f"RouteOne finished: {self._final_output_path}\nDouble check top of output file for errors")
        else:
            self._route_one_results_label.config(text=f"Error encountered running RouteOne: {result}")

        self.lift()


class ConfigWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        
        self._font_frame = tk.Frame(self)
        self._font_frame.grid(row=0, column=0)
        self._font_frame.columnconfigure(1, weight=1)

        self._font_name_label = tk.Label(self._font_frame, text="Font Name:")
        self._font_name_label.grid(row=3, column=0, padx=3, pady=3, sticky=tk.EW)

        self._font_name = custom_tkinter.SimpleOptionMenu(self._font_frame, sorted(font.families()))
        self._font_name.grid(row=3, column=1, padx=5, pady=3, sticky=tk.EW)
        custom_font_name = config.get_custom_font_name()
        if custom_font_name not in font.families():
            custom_font_name = config.DEFAULT_FONT_NAME
        self._font_name.set(custom_font_name)

        self._font_name_button = tk.Button(self._font_frame, text="Set Font Name", command=self.set_font_name)
        self._font_name_button.grid(row=4, column=0, columnspan=2, padx=3, pady=3)

        self._font_warning = tk.Label(self._font_frame, text=f"If your custom font is not present in the list\nMake sure that it is installed on your system\nAnd then restart the program")
        self._font_warning.grid(row=5, column=0, columnspan=2, padx=5, pady=3, sticky=tk.EW)

        self._color_frame = tk.Frame(self)
        self._color_frame.grid(row=2, column=0, pady=20)

        self._color_header = tk.Label(self._color_frame, text="Color Config:")
        self._color_header.grid(row=0, column=0, padx=5, pady=3, sticky=tk.EW)

        self._reset_colors_button = tk.Button(self._color_frame, text="Reset all colors", command=self._reset_all_colors)
        self._reset_colors_button.grid(row=1, column=0, padx=5, pady=3, sticky=tk.EW)

        self._success_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Success Color:", setter=config.set_success_color, getter=config.get_success_color, callback=self.lift)
        self._success_color.grid(row=2, column=0, sticky=tk.EW)

        self._warning_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Warning Color:", setter=config.set_warning_color, getter=config.get_warning_color, callback=self.lift)
        self._warning_color.grid(row=3, column=0, sticky=tk.EW)

        self._failure_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Failure Color:", setter=config.set_failure_color, getter=config.get_failure_color, callback=self.lift)
        self._failure_color.grid(row=4, column=0, sticky=tk.EW)

        self._divider_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Divider Color:", setter=config.set_divider_color, getter=config.get_divider_color, callback=self.lift)
        self._divider_color.grid(row=5, column=0, sticky=tk.EW)
        
        self._header_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Header Color:", setter=config.set_header_color, getter=config.get_header_color, callback=self.lift)
        self._header_color.grid(row=6, column=0, sticky=tk.EW)
        
        self._primary_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Primary Color:", setter=config.set_primary_color, getter=config.get_primary_color, callback=self.lift)
        self._primary_color.grid(row=7, column=0, sticky=tk.EW)
        
        self._secondary_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Secondary Color:", setter=config.set_secondary_color, getter=config.get_secondary_color, callback=self.lift)
        self._secondary_color.grid(row=8, column=0, sticky=tk.EW)
        
        self._contrast_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Contrast Color:", setter=config.set_contrast_color, getter=config.get_contrast_color, callback=self.lift)
        self._contrast_color.grid(row=9, column=0, sticky=tk.EW)
        
        self._background_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Background Color:", setter=config.set_background_color, getter=config.get_background_color, callback=self.lift)
        self._background_color.grid(row=10, column=0, sticky=tk.EW)
        
        self._text_color = custom_tkinter.ConfigColorUpdater(self._color_frame, label_text="Text Color:", setter=config.set_text_color, getter=config.get_text_color, callback=self.lift)
        self._text_color.grid(row=11, column=0, sticky=tk.EW)

        self._restart_label = tk.Label(self._color_frame, text="After changing colors, you must restart the program\nbefore color changes will take effect")
        self._restart_label.grid(row=15, column=0, padx=5, pady=5, sticky=tk.EW)

        self._close_button = custom_tkinter.SimpleButton(self, text="Close", command=self._main_window.cancel_new_event)
        self._close_button.grid(row=15, column=0, padx=5, pady=2)

        self.bind('<Escape>', self._main_window.cancel_new_event)
    
    def _reset_all_colors(self, *args, **kwargs):
        config.reset_all_colors()
        self._success_color.refresh_color()
        self._warning_color.refresh_color()
        self._failure_color.refresh_color()
        self._divider_color.refresh_color()
        self._header_color.refresh_color()
        self._primary_color.refresh_color()
        self._secondary_color.refresh_color()
        self._contrast_color.refresh_color()
        self._background_color.refresh_color()
        self._text_color.refresh_color()

    def set_font_name(self, *args, **kwargs):
        config.set_custom_font_name(self._font_name.get())
        self._main_window.load_custom_font()


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


def startup_check_for_upgrade(main_app:Main):
    new_app_version, new_asset_url = auto_update.get_new_version_info()
    logger.info(f"Latest version determined to be: {new_app_version}")

    # kinda dumb, but this should have enough delay that when restarting
    # the parent process should have died already, so we can properly clean it up
    auto_update.auto_cleanup_old_version()

    if not auto_update.is_upgrade_needed(new_app_version):
        logger.info(f"No upgrade needed")
        return
    
    if not messagebox.askyesno("Update?", f"Found new version {new_app_version}\nDo you want to update?"):
        logger.info(f"User rejected auto-update")
        return
    
    logger.info(f"User requested auto-update")
    global flag_to_auto_update
    flag_to_auto_update = True
    main_app.event_generate(const.FORCE_QUIT_EVENT)


class AutoUpgradeGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._allow_close = False

        self.auto_update_frame = tk.Frame(self, width=250, height=150)
        self.auto_update_frame.pack()
        self.auto_update_frame.pack_propagate(False)

        self.processing_message = tk.Label(self.auto_update_frame)
        self.processing_message.pack(pady=10, padx=20)

        self.auto_update_message = tk.Label(self.auto_update_frame)
        self.auto_update_message.pack(pady=10, padx=10)

        self.button = custom_tkinter.SimpleButton(self.auto_update_frame, text="Restart App", command=self._prevent_abort)
        self.button.pack(pady=10, padx=10)
        self.button.disable()
        
        self._dum_thread = threading.Thread(target=self._update_processing_text)
        self._dum_thread.daemon = True
        self._dum_thread.start()
        
        self._thread = threading.Thread(target=self._auto_update_app)
        self._thread.daemon = True
        self._thread.start()

        self.bind(const.FORCE_QUIT_EVENT, self._prevent_abort)
        self.protocol("WM_DELETE_WINDOW", self._prevent_abort)
    
    def _prevent_abort(self, *args, **kwargs):
        if self._allow_close:
            self.destroy()
    
    def _update_processing_text(self, *args, **kwargs):
        messages = [
            "Updating .",
            "Updating ..",
            "Updating ...",
        ]
        cur_idx = 0
        while not self._allow_close:
            self.processing_message.configure(text=messages[cur_idx])
            cur_idx = (cur_idx + 1) % len(messages)
            time.sleep(0.1)
    
    def _display_update_message(self, new_text):
        self.auto_update_message.configure(text=new_text)

    def _auto_update_app(self, *args, **kwargs):
        try:
            success = auto_update.update(display_fn=self._display_update_message)
        except Exception as e:
            success = False

        self._allow_close = True
        time.sleep(0.15)
        if not success:
            self.processing_message.configure(text="Error")
            self.auto_update_message.configure(text="Failed automatic update\nTry manually installing the new version")
        else:
            self.processing_message.configure(text="Success!")
            self.auto_update_message.configure(text="Automatic update successful!\nClick OK to restart app")
        
        self.button.enable()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        const.DEBUG_MODE = True
    
    app = Main()
    background_thread = threading.Thread(target=startup_check_for_upgrade, args=(app,))

    background_thread.start()
    app.run()

    background_thread.join()

    if flag_to_auto_update:
        auto_update.auto_cleanup_old_version()
        app_upgrade = AutoUpgradeGUI()
        app_upgrade.mainloop()

        logger.info(f"About to restart: {sys.argv}")
        if os.path.splitext(sys.argv[0])[1] == ".pyw":
            subprocess.Popen([sys.executable] + sys.argv, start_new_session=True)
        else:
            subprocess.Popen(sys.argv, start_new_session=True)

    
