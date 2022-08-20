import argparse
import os

import tkinter as tk
from tkinter import filedialog
from tkinter import ANCHOR, ttk

from gui import custom_tkinter, route_event_components, pkmn_components, quick_add_components
from gui.event_details import EventDetails
from pkmn.route_events import EventDefinition, EventFolder, EventGroup, EventItem, InventoryEventDefinition, WildPkmnEventDefinition
from utils.constants import const
from utils.config_manager import config
import pkmn.pkmn_db as pkmn_db
import pkmn.router as router
from utils import route_one_utils


class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self._data = router.Router()

        self.geometry(f"2000x1200")
        self.title("Pokemon RBY XP Router")

        # fix tkinter bug
        style = ttk.Style()
        style.map("Treeview", foreground=fixed_map("foreground", style), background=fixed_map("background", style))

        # menu bar
        self.top_menu_bar = tk.Menu(self)
        self.config(menu=self.top_menu_bar)

        self.file_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.file_menu.add_command(label="New Route       (Ctrl+N)", command=self.open_new_route_window)
        self.file_menu.add_command(label="Load Route      (Ctrl+L)", command=self.open_load_route_window)
        self.file_menu.add_command(label="Save Route       (Ctrl+S)", command=self.save_route)
        self.file_menu.add_command(label="Export Notes       (Ctrl+Shift+W)", command=self.save_route)

        self.event_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.event_menu.add_command(label="New Event                   (Ctrl+F)", command=self.open_new_event_window)
        self.event_menu.add_command(label="Move Event Up           (Ctrl+E)", command=self.move_group_up)
        self.event_menu.add_command(label="Move Event Down      (Ctrl+D)", command=self.move_group_down)
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

        self.padding_left = tk.Frame(self.group_controls)
        self.padding_left.grid(row=0, column=0)
        
        self.move_group_up_button = custom_tkinter.SimpleButton(self.group_controls, text='Move Event Up', command=self.move_group_up, width=15)
        self.move_group_up_button.grid(row=0, column=1, padx=5, pady=1)
        self.move_group_down_button = custom_tkinter.SimpleButton(self.group_controls, text='Move Event Down', command=self.move_group_down, width=15)
        self.move_group_down_button.grid(row=0, column=2, padx=5, pady=1)
        self.transfer_event_button = custom_tkinter.SimpleButton(self.group_controls, text='Transfer Event', command=self.open_transfer_event_window, width=15)
        self.transfer_event_button.grid(row=0, column=3, padx=5, pady=1)

        self.delete_event_button = custom_tkinter.SimpleButton(self.group_controls, text='Delete Event', command=self.delete_group, width=15)
        self.delete_event_button.grid(row=0, column=5, padx=5, pady=1)

        self.new_folder_button = custom_tkinter.SimpleButton(self.group_controls, text='New Folder', command=self.open_new_folder_window, width=15)
        self.new_folder_button.grid(row=0, column=7, padx=5, pady=1)
        self.rename_folder_button = custom_tkinter.SimpleButton(self.group_controls, text='Rename Folder', command=self.rename_folder, width=15)
        self.rename_folder_button.grid(row=0, column=8, padx=5, pady=1)

        self.padding_right = tk.Frame(self.group_controls)
        self.padding_right.grid(row=0, column=10)

        self.group_controls.columnconfigure(0, weight=1)
        self.group_controls.columnconfigure(4, weight=1)
        self.group_controls.columnconfigure(6, weight=1)
        self.group_controls.columnconfigure(10, weight=1)

        self.event_list = pkmn_components.RouteList(self._data, self.left_info_panel)
        self.event_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True, side="left")
        self.scroll_bar = tk.Scrollbar(self.left_info_panel, orient="vertical", command=self.event_list.yview)
        self.scroll_bar.pack(side="right", fill=tk.BOTH)
        self.event_list.configure(yscrollcommand=self.scroll_bar.set)

        # right panel for event details
        self.event_details = EventDetails(self.info_panel, event_update_callback=self.update_existing_event)
        self.event_details.grid(row=0, column=1, sticky=tk.NSEW)
        self.event_details.pack_propagate(0)

        self.info_panel.grid_rowconfigure(0, weight=1)
        # these uniform values don't have to be a specific value, they just have to match
        self.info_panel.grid_columnconfigure(0, weight=1, uniform="test")
        #self.info_panel.grid_columnconfigure(1, weight=1, uniform="test")

        # main route actions
        self.bind('<Control-n>', self.open_new_route_window)
        self.bind('<Control-l>', self.open_load_route_window)
        self.bind('<Control-s>', self.save_route)
        self.bind('<Control-W>', self.export_notes)
        # event actions
        self.bind('<Control-f>', self.open_new_event_window)
        self.bind('<Control-d>', self.move_group_down)
        self.bind('<Control-e>', self.move_group_up)
        self.bind('<Control-r>', self.open_transfer_event_window)
        self.bind('<Control-b>', self.delete_group)
        self.bind('<Delete>', self.delete_group)
        # folder actions
        self.bind('<Control-q>', self.open_new_folder_window)
        self.bind('<Control-w>', self.rename_folder)
        # route One integrations
        self.bind('<Control-E>', self.open_export_window)
        self.bind('<Control-R>', self.just_export_and_run)
        # detail update function
        self.bind("<<TreeviewSelect>>", self.show_event_details)
        self.bind(const.ROUTE_LIST_REFRESH_EVENT, self.update_run_status)

        self.event_list.refresh()
        self.new_event_window = None

    def run(self):
        self.mainloop()

    def save_route(self, *args, **kwargs):
        route_name = self.route_name.get()
        self._data.save(route_name)
        self.message_label.set_message(f"Successfully saved route: {route_name}")
    
    def export_notes(self, *args, **kwargs):
        self.message_label.set_message(f"Exported notes to: {self._data.export_notes(self.route_name.get())}")

    def update_run_status(self, *args, **kwargs):
        if self._data.root_folder.has_errors():
            self.run_status_label.config(text="Run Status: Invalid", bg=const.ERROR_COLOR)
        else:
            self.run_status_label.config(text="Run Status: Valid", bg=const.VALID_COLOR)
    
    def update_run_version(self, *args, **kwargs):
        if self._data.pkmn_version == const.YELLOW_VERSION:
            bg_color = const.YELLOW_COLOR
        elif self._data.pkmn_version == const.RED_VERSION:
            bg_color = const.RED_COLOR
        elif self._data.pkmn_version == const.BLUE_VERSION:
            bg_color = const.BLUE_COLOR
        else:
            bg_color = "white"

        self.route_version.config(text=f"{self._data.pkmn_version} Version", background=bg_color)
        self.trainer_add.update_pkmn_version()
        self.wild_pkmn_add.update_pkmn_version()
        self.item_add.update_pkmn_version()

    def update_quick_add_buttons(self, allow_enable):
        self.trainer_add.update_button_status(allow_enable=allow_enable)
        self.wild_pkmn_add.update_button_status(allow_enable=allow_enable)
        self.item_add.update_button_status(allow_enable=allow_enable)
    
    def trainer_add_preview(self, trainer_name):
        event_group = self._data.get_event_obj(self.event_list.get_selected_event_id())
        if event_group is None:
            init_state = self._data.init_route_state
        else:
            init_state = event_group.init_state

        # create a fake event_def just so we can show the trainer that the user is looking at
        # TODO: just using the init_state as the post_event state as well. Ideally would like to use None for an empty state, but that's not currently supported
        self.event_details.show_event_details(
            EventDefinition(trainer_name=trainer_name),
            init_state,
            init_state,
            allow_updates=False
        )
    
    def show_event_details(self, *args, **kwargs):
        event_group = self._data.get_event_obj(self.event_list.get_selected_event_id())
        self.update_quick_add_buttons((event_group is not None) and (not isinstance(event_group, EventItem)))
        
        if event_group is None:
            self.event_details.show_event_details(None, self._data.init_route_state, self._data.get_final_state(), allow_updates=False)
            self.rename_folder_button.disable()
            self.delete_event_button.disable()
            self.transfer_event_button.disable()
            self.new_folder_button.disable()
            self.move_group_down_button.disable()
            self.move_group_up_button.disable()
            self.item_add.cur_state = None
        elif isinstance(event_group, EventFolder):
            self.event_details.show_event_details(None, event_group.init_state, event_group.final_state, allow_updates=False)
            self.rename_folder_button.enable()
            self.transfer_event_button.enable()
            self.new_folder_button.enable()
            self.move_group_down_button.enable()
            self.move_group_up_button.enable()
            if len(event_group.children) == 0:
                self.delete_event_button.enable()
            else:
                self.delete_event_button.disable()
            self.item_add.cur_state = event_group.init_state
        else:
            do_allow_updates = (
                 isinstance(event_group, EventGroup) or 
                 event_group.event_definition.get_event_type() == const.TASK_LEARN_MOVE_LEVELUP
            )
            self.event_details.show_event_details(event_group.event_definition, event_group.init_state, event_group.final_state, do_allow_updates)
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
        self._data.replace_event_group(self.event_list.get_selected_event_id(), new_event)
        self.event_list.refresh()
        self.show_event_details()
    
    def add_area(self, area_name):
        self._data.add_area(
            area_name=area_name,
            insert_before=self.event_list.get_selected_event_id()
        )
        self.trainer_add.trainer_filter_callback()
        self.event_list.refresh()
    
    def quick_add_event(self, new_event):
        self._data.add_event_object(
            event_def=new_event,
            insert_before=self.event_list.get_selected_event_id()
        )
        self.trainer_add.trainer_filter_callback()
        self.event_list.refresh()
    
    def open_new_route_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = NewRouteWindow(self)
    
    def create_new_route(self, solo_mon, min_battles_name, pkmn_version):
        if min_battles_name == const.EMPTY_ROUTE_NAME:
            min_battles_name = None
        
        self.new_event_window.close()
        self.new_event_window = None
        self._data.new_route(solo_mon, min_battles_name, pkmn_version=pkmn_version)
        self.update_run_version()
        self.event_list.refresh()
        self.show_event_details()
    
    def open_load_route_window(self, *args, **kwargs):
        if self._is_active_window():
            self.new_event_window = LoadRouteWindow(self)

    def load_route(self, route_to_load):
        self.new_event_window.close()
        self.new_event_window = None
        self._data.load(route_to_load)
        self.route_name.delete(0, tk.END)
        self.route_name.insert(0, route_to_load)
        self.update_run_version()
        self.event_list.refresh()
        self.show_event_details()

    def move_group_up(self, event=None):
        cur_event_id = self.event_list.get_selected_event_id()
        if cur_event_id == -1:
            return
        self._data.move_event_object(self.event_list.get_selected_event_id(), True)
        self.event_list.refresh()

    def move_group_down(self, event=None):
        cur_event_id = self.event_list.get_selected_event_id()
        if cur_event_id == -1:
            return
        self._data.move_event_object(self.event_list.get_selected_event_id(), False)
        self.event_list.refresh()

    def delete_group(self, event=None):
        cur_event_id = self.event_list.get_selected_event_id()
        if cur_event_id == -1:
            return
        self._data.remove_event_object(self.event_list.get_selected_event_id())
        self.event_list.refresh()

    def finalize_new_folder(self, new_folder_name, prev_folder_name=None):
        if prev_folder_name is None:
            self._data.add_event_object(new_folder_name=new_folder_name, insert_before=self.event_list.get_selected_event_id())
        else:
            self._data.rename_event_folder(prev_folder_name, new_folder_name)

        self.new_event_window.close()
        self.new_event_window = None
        self.event_list.refresh()

    def open_transfer_event_window(self, event=None):
        if self._is_active_window():
            event_group_id = self.event_list.get_selected_event_id()
            if event_group_id == -1:
                return

            dest_folder_list = list(self._data.folder_lookup.keys())
            cur_event_folder = self._data.get_event_obj(event_group_id).parent.name
            dest_folder_list.remove(cur_event_folder)

            event_obj = self._data.get_event_obj(event_group_id)
            if isinstance(event_obj, EventFolder):
                dest_folder_list.remove(event_obj.name)

            self.new_event_window = TransferEventWindow(
                self,
                event_group_id,
                dest_folder_list,
                cur_event_folder
            )
    
    def transfer_event(self, event_group_id, new_folder_name):
        self._data.transfer_event_object(event_group_id, new_folder_name)
        self.new_event_window.close()
        self.new_event_window = None
        self.event_list.refresh()

    def rename_folder(self, *args, **kwargs):
        self.open_new_folder_window(**{const.EVENT_FOLDER_NAME: self._data.get_event_obj(self.event_list.get_selected_event_id()).name})

    def open_new_event_window(self, *args, **kwargs):
        if self._is_active_window():
            event_id = self.event_list.get_selected_event_id()
            event_obj = self._data.get_event_obj(event_id)

            if event_obj is None:
                return

            state = event_obj.init_state
            self.new_event_window = NewEventWindow(self, self._data.defeated_trainers, state)

    def open_new_folder_window(self, *args, **kwargs):
        if self._is_active_window():
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
            event_id = self.event_list.get_selected_event_id()
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
    
    def new_event(self, event_def):
        self._data.add_event_object(event_def=event_def, insert_before=self.event_list.get_selected_event_id())
        self.new_event_window.close()
        self.new_event_window = None
        self.event_list.refresh()
    
    def _is_active_window(self):
        # returns true if the current window is active (i.e. no sub-windows exist)
        if self.new_event_window is not None and tk.Toplevel.winfo_exists(self.new_event_window):
            return False
        return True


class NewRouteWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs, width=400)

        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        self.pkmn_version_label = tk.Label(self.controls_frame, text="Pokemon Version:")
        self.pkmn_version_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.pkmn_version = custom_tkinter.SimpleOptionMenu(self.controls_frame, const.VERSION_LIST, command=self._pkmn_version_callback)
        self.pkmn_version.config(width=20)
        self.pkmn_version.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.solo_selector_label = tk.Label(self.controls_frame, text="Solo Pokemon:")
        self.solo_selector_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.solo_selector = custom_tkinter.SimpleOptionMenu(self.controls_frame, [const.NO_POKEMON])
        self.solo_selector.config(width=20)
        self.solo_selector.grid(row=1, column=1, padx=self.padx, pady=self.pady)

        self.pkmn_filter_label = tk.Label(self.controls_frame, text="Solo Pokemon Filter:")
        self.pkmn_filter_label.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.pkmn_filter = custom_tkinter.SimpleEntry(self.controls_frame, callback=self._pkmn_filter_callback)
        self.pkmn_filter.config(width=30)
        self.pkmn_filter.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        self.min_battles_selector_label = tk.Label(self.controls_frame, text="Base Min-Battles Route:")
        self.min_battles_selector_label.grid(row=3, column=0, padx=self.padx, pady=self.pady)
        self.min_battles_selector = custom_tkinter.SimpleOptionMenu(self.controls_frame, [const.EMPTY_ROUTE_NAME])
        self.min_battles_selector.grid(row=3, column=1, padx=self.padx, pady=self.pady)

        self.warning_label = tk.Label(self.controls_frame, text="WARNING: Any unsaved changes in your current route\nwill be lost when creating a new route!", justify=tk.CENTER, anchor=tk.CENTER)
        self.warning_label.grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=self.padx, pady=self.pady)

        self.create_button = custom_tkinter.SimpleButton(self.controls_frame, text="Create Route", command=self.create)
        self.create_button.grid(row=10, column=0, padx=self.padx, pady=self.pady)
        self.cancel_button = custom_tkinter.SimpleButton(self.controls_frame, text="Cancel", command=self._main_window.cancel_new_event)
        self.cancel_button.grid(row=10, column=1, padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.create)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self._pkmn_version_callback()
        self.pkmn_filter.focus()

    def _pkmn_version_callback(self, *args, **kwargs):
        # TODO: gross! ugly! slow! fix later! reloading entire db from disk every time we change this dropdown value :/
        pkmn_db.change_version(self.pkmn_version.get())
        # now that we've loaded the right version, repopulate the pkmn selector just in case
        self.solo_selector.new_values(pkmn_db.pkmn_db.get_filtered_names(filter_val=self.pkmn_filter.get().strip()))
        self.min_battles_selector.new_values([const.EMPTY_ROUTE_NAME] + pkmn_db.min_battles_db.data)

    def _pkmn_filter_callback(self, *args, **kwargs):
        self.solo_selector.new_values(pkmn_db.pkmn_db.get_filtered_names(filter_val=self.pkmn_filter.get().strip()))
    
    def create(self, *args, **kwargs):
        self._main_window.create_new_route(self.solo_selector.get(), self.min_battles_selector.get(), self.pkmn_version.get())


class LoadRouteWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)

        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        self.previous_route_label = tk.Label(self.controls_frame, text="Existing Routes:")
        self.previous_route_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.previous_route_names = custom_tkinter.SimpleOptionMenu(self.controls_frame, self.get_existing_routes())
        self.previous_route_names.grid(row=0, column=1, padx=self.padx, pady=self.pady)
        self.previous_route_names.config(width=25)

        self.filter_label = tk.Label(self.controls_frame, text="Filter:")
        self.filter = custom_tkinter.SimpleEntry(self.controls_frame, callback=self._filter_callback)
        self.filter_label.grid(row=1, column=0)
        self.filter.grid(row=1, column=1)

        self.warning_label = tk.Label(self.controls_frame, text="WARNING: Any unsaved changes in your current route\nwill be lost when loading an existing route!")
        self.warning_label.grid(row=2, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.create_button = custom_tkinter.SimpleButton(self.controls_frame, text="Load Route", command=self.load)
        self.create_button.grid(row=3, column=0, padx=self.padx, pady=self.pady)
        self.cancel_button = custom_tkinter.SimpleButton(self.controls_frame, text="Cancel", command=self._main_window.cancel_new_event)
        self.cancel_button.grid(row=3, column=1, padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.load)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self.filter.focus()

    def get_existing_routes(self, filter_text=""):
        loaded_routes = []
        filter_text = filter_text.lower()
        if os.path.exists(const.SAVED_ROUTES_DIR):
            for fragment in os.listdir(const.SAVED_ROUTES_DIR):
                name, ext = os.path.splitext(fragment)
                if filter_text not in name.lower():
                    continue
                if ext != ".json":
                    continue
                loaded_routes.append(name)

        return loaded_routes

    def _filter_callback(self, *args, **kwargs):
        self.previous_route_names.new_values(self.get_existing_routes(filter_text=self.filter.get()))
    
    def load(self, *args, **kwargs):
        self._main_window.load_route(self.previous_route_names.get())


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


class TransferEventWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, cur_event_id, cur_folder_names, prev_folder_name, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        if main_window is None:
            raise ValueError('Must set main_window when creating TransferEventWindow')
        
        self._cur_event_id = cur_event_id
        self._cur_folder_names = cur_folder_names
        self._prev_folder_name = prev_folder_name

        self._prev_folder_label = tk.Label(self, text=f"Current folder: {self._prev_folder_name}")
        self._prev_folder_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self._new_folder_label = tk.Label(self, text=f"New folder:")
        self._folder_name = custom_tkinter.SimpleOptionMenu(self, option_list=self.get_possible_folders())
        self._new_folder_label.grid(row=1, column=0, padx=10, pady=10)
        self._folder_name.grid(row=1, column=1, padx=10, pady=10)

        self.filter_label = tk.Label(self, text="Filter:")
        self.filter = custom_tkinter.SimpleEntry(self, callback=self._filter_callback)
        self.filter_label.grid(row=2, column=0, padx=10, pady=10)
        self.filter.grid(row=2, column=1, padx=10, pady=10)

        self._add_button = custom_tkinter.SimpleButton(self, command=self.transfer, text="Update Folder")
        self._cancel_button = custom_tkinter.SimpleButton(self, text="Cancel", command=self._main_window.cancel_new_event)
        self._add_button.grid(row=3, column=0, padx=10, pady=10)
        self._cancel_button.grid(row=3, column=1, padx=10, pady=10)

        self.bind('<Return>', self.transfer)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self.filter.focus()
    
    def get_possible_folders(self, filter_text=""):
        filter_text = filter_text.lower()
        result = [x for x in self._cur_folder_names if filter_text in x.lower()]
        return result

    def _filter_callback(self, *args, **kwargs):
        self._folder_name.new_values(self.get_possible_folders(filter_text=self.filter.get()))
    
    def transfer(self, *args, **kwargs):
        self._main_window.transfer_event(self._cur_event_id, self._folder_name.get())


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
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if args.debug:
        const.DEBUG_MODE = True

    Main().run()
