import argparse
import subprocess
import os

import tkinter as tk
from tkinter import filedialog
from tkinter import ANCHOR, ttk

from gui import custom_tkinter, route_event_components, pkmn_components
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

        self.minsize(2000, 1200)
        self.title("Pokemon Yellow XP Router")

        # fix tkinter bug
        style = ttk.Style()
        style.map("Treeview", foreground=fixed_map("foreground", style), background=fixed_map("background", style))

        # menu bar
        self.top_menu_bar = tk.Menu(self)
        self.config(menu=self.top_menu_bar)

        self.file_menu = tk.Menu(self.top_menu_bar, tearoff=0)
        self.file_menu.add_command(label="New Route")
        self.file_menu.add_command(label="Load Route")
        self.file_menu.add_command(label="Save Route")

        self.top_menu_bar.add_cascade(label="File", menu=self.file_menu)

        # main container for everything to sit in... might be unnecessary?
        self.primary_window = tk.Frame(self)
        self.primary_window.pack(fill=tk.BOTH, expand=True)

        self.top_controls = tk.Frame(self.primary_window)
        self.top_controls.pack(fill=tk.BOTH)
        self.top_controls.pack_propagate(False)

        self.top_left_controls = tk.Frame(self.top_controls)
        self.top_left_controls.grid(row=0, column=0, sticky=tk.NSEW)
        self.run_status_label = tk.Label(self.top_left_controls, text="Run Status: Valid", background=const.VALID_COLOR, anchor=tk.W, padx=10, pady=10)
        self.run_status_label.grid(row=0, column=0, sticky=tk.W)

        self.group_controls = tk.Frame(self.top_left_controls)
        self.group_controls.grid(row=0, column=1)
        self.top_left_controls.columnconfigure(1, weight=1)
        self.top_left_controls.rowconfigure(0, weight=1)

        self.move_group_up_button = custom_tkinter.SimpleButton(self.group_controls, text='Move Event Up', command=self.move_group_up, width=15)
        self.move_group_up_button.grid(row=0, column=0, padx=5, pady=1)
        self.move_group_down_button = custom_tkinter.SimpleButton(self.group_controls, text='Move Event Down', command=self.move_group_down, width=15)
        self.move_group_down_button.grid(row=1, column=0, padx=5, pady=1)

        self.new_event_button = custom_tkinter.SimpleButton(self.group_controls, text='New Event', command=self.open_new_event_window, width=15)
        self.new_event_button.grid(row=0, column=1, padx=5, pady=1)
        self.delete_event_button = custom_tkinter.SimpleButton(self.group_controls, text='Delete Event', command=self.delete_group, width=15)
        self.delete_event_button.grid(row=1, column=1, padx=5, pady=1)

        self.transfer_event_button = custom_tkinter.SimpleButton(self.group_controls, text='Transfer Event', command=self.open_transfer_event_window, width=15)
        self.transfer_event_button.grid(row=0, column=2, padx=5, pady=1)
        self.rename_folder_button = custom_tkinter.SimpleButton(self.group_controls, text='Rename Folder', command=self.rename_folder, width=15)
        self.rename_folder_button.grid(row=1, column=2, padx=5, pady=1)

        self.new_folder_button = custom_tkinter.SimpleButton(self.group_controls, text='New Folder', command=self.open_new_folder_window, width=15)
        self.new_folder_button.grid(row=0, column=3, padx=5, pady=1)

        self.top_right_controls = tk.Frame(self.top_controls)
        self.top_right_controls.grid(row=0, column=1, sticky=tk.E)
        self.top_controls.columnconfigure(0, weight=1)
        self.top_controls.columnconfigure(1, weight=1)

        self.solo_selector_label = tk.Label(self.top_right_controls, text="Solo Pokemon:")
        self.solo_selector_label.grid(row=0, column=0)
        self.solo_selector = custom_tkinter.SimpleOptionMenu(self.top_right_controls, pkmn_db.pkmn_db.get_all_names(), callback=self.new_solo_pkmn)
        self.solo_selector.config(width=20)
        self.solo_selector.grid(row=0, column=1)
        self.pkmn_filter_label = tk.Label(self.top_right_controls, text="Solo Pokemon Filter:")
        self.pkmn_filter_label.grid(row=0, column=2)
        self.pkmn_filter = custom_tkinter.SimpleEntry(self.top_right_controls, callback=self._pkmn_filter_callback)
        self.pkmn_filter.config(width=30)
        self.pkmn_filter.grid(row=0, column=3)

        self.min_battles_selector_label = tk.Label(self.top_right_controls, text="Reset to Minimum Battles:")
        self.min_battles_selector_label.grid(row=0, column=4)
        self.min_battles_selector = custom_tkinter.SimpleOptionMenu(self.top_right_controls, pkmn_db.min_battles_db.data, callback=self.reset_to_min_battles)
        self.min_battles_selector.grid(row=0, column=5)
        self.route_export_button = tk.Button(self.top_right_controls, text="Export to RouteOne", command=self.open_export_window)
        self.route_export_button.grid(row=1, column=0)
        self.route_save_button = tk.Button(self.top_right_controls, text="Save Route", command=self.save_route)
        self.route_save_button.grid(row=1, column=1)
        self.route_name_label = tk.Label(self.top_right_controls, text="Route Name")
        self.route_name_label.grid(row=1, column=2)
        self.route_name = tk.Entry(self.top_right_controls)
        self.route_name.grid(row=1, column=3)
        self.route_name.config(width=30)
        self.previous_route_label = tk.Label(self.top_right_controls, text="Previous Routes")
        self.previous_route_label.grid(row=1, column=4)
        self.previous_route_names = custom_tkinter.SimpleOptionMenu(self.top_right_controls, ["N/A"], callback=self.update_route_name)
        self.previous_route_names.grid(row=1, column=5)
        self.previous_route_names.config(width=25)

        self.info_panel = tk.Frame(self.primary_window)
        self.info_panel.pack(expand=True, fill=tk.BOTH)

        self.left_info_panel = tk.Frame(self.info_panel)
        self.left_info_panel.grid(row=0, column=0, sticky="nsew")

        # create the main thingy
        self.event_list = pkmn_components.RouteList(self._data, self.left_info_panel)
        self.event_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True, side="left")
        self.scroll_bar = tk.Scrollbar(self.left_info_panel, orient="vertical", command=self.event_list.yview)
        self.scroll_bar.pack(side="right", fill=tk.BOTH)
        self.event_list.configure(yscrollcommand=self.scroll_bar.set)

        self.right_info_panel = tk.Frame(self.info_panel)
        self.right_info_panel.grid(row=0, column=1, sticky="nsew")

        self.stat_info_label = tk.Label(self.right_info_panel, text="Stats with * are calculated with a badge boost")
        self.stat_info_label.config(bg="white")
        self.stat_info_label.pack()

        self.pre_state_frame = tk.Frame(self.right_info_panel)
        self.pre_state_frame.pack(fill=tk.X)
        self.state_pre_label = tk.Label(self.pre_state_frame, text="Pre-event State Display Mode:")
        self.state_pre_label.grid(column=1, row=0, padx=10, pady=10)
        self.pre_state_selector = custom_tkinter.SimpleOptionMenu(self.pre_state_frame, [const.STATE_SUMMARY_LABEL, const.BADGE_BOOST_LABEL], callback=self._pre_state_display_mode_callback)
        self.pre_state_selector.grid(column=2, row=0, padx=10, pady=10)
        self.state_pre_viewer = pkmn_components.StateViewer(self.pre_state_frame)
        self.state_pre_viewer.grid(column=1, row=1, padx=10, pady=10, columnspan=2)
        self.badge_boost_viewer = pkmn_components.BadgeBoostViewer(self.pre_state_frame)
        # centering contents with padded columns that expand
        # NOTE: will have to update the index of the right-most column here if we add more columns in the future
        self.pre_state_frame.columnconfigure(0, weight=1)
        self.pre_state_frame.columnconfigure(3, weight=1)

        self.event_details_frame = tk.Frame(self.right_info_panel, highlightbackground="black", highlightthickness=2)
        self.event_details_frame.pack(anchor=tk.N, fill=tk.BOTH, expand=True, padx=10)
        self.event_details_button = custom_tkinter.SimpleButton(self.event_details_frame, text="Update Event", command=self.update_existing_event)
        self.event_details_button.pack()
        self.event_details_button.disable()

        self.event_editor_lookup = route_event_components.EventEditorFactory(self.event_details_frame, self.event_details_button)
        self.current_event_editor = None

        self.trainer_notes = self.event_editor_lookup.get_editor(
            route_event_components.EditorParams(
                const.TASK_NOTES_ONLY,
                self._data.defeated_trainers,
                None
            )
        )
        self.trainer_notes.pack()
        self.enemy_team_viewer = pkmn_components.EnemyPkmnTeam(self.event_details_frame)
        self.enemy_team_viewer.pack()

        self.post_state_frame = tk.Frame(self.right_info_panel)
        self.post_state_frame.pack()
        self.state_post_label = tk.Label(self.post_state_frame, text="Post-event State:")
        self.state_post_label.grid(column=1, row=0, padx=10, pady=10)
        self.state_post_viewer = pkmn_components.StateViewer(self.post_state_frame)
        self.state_post_viewer.grid(column=1, row=1, padx=10, pady=10)

        self.info_panel.grid_rowconfigure(0, weight=1)
        # these uniform values don't have to be a specific value, they just have to match
        self.info_panel.grid_columnconfigure(0, weight=1, uniform="test")
        self.info_panel.grid_columnconfigure(1, weight=1, uniform="test")

        # keybindings
        self.bind('<Control-r>', self.event_list.refresh)
        self.bind("<<TreeviewSelect>>", self.show_event_details)
        self.bind(const.ROUTE_LIST_REFRESH_EVENT, self.update_run_status)

        self.refresh_existing_routes()
        self.event_list.refresh()
        self.new_event_window = None

    def update_run_status(self, *args, **kwargs):
        if self._data.root_folder.has_errors():
            self.run_status_label.config(text="Run Status: Invalid", bg=const.ERROR_COLOR)
        else:
            self.run_status_label.config(text="Run Status: Valid", bg=const.VALID_COLOR)
    
    def run(self):
        self.mainloop()

    def _pkmn_filter_callback(self, *args, **kwargs):
        self.solo_selector.new_values(pkmn_db.pkmn_db.get_filtered_names(filter_val=self.pkmn_filter.get().strip()))
    
    def _pre_state_display_mode_callback(self, *args, **kwargs):
        if self.pre_state_selector.get() == const.BADGE_BOOST_LABEL:
            self.state_pre_viewer.grid_forget()
            self.badge_boost_viewer.grid(column=1, row=1, padx=10, pady=10, columnspan=2)
        else:
            self.badge_boost_viewer.grid_forget()
            self.state_pre_viewer.grid(column=1, row=1, padx=10, pady=10, columnspan=2)
    
    def save_route(self, *args, **kwargs):
        self._data.save(self.route_name.get())
        self.refresh_existing_routes()
    
    def update_route_name(self, *args, **kwargs):
        self.route_name.delete(0, tk.END)
        self.route_name.insert(0, self.previous_route_names.get())
        self.load_route()

    def refresh_existing_routes(self, *args, **kwargs):
        loaded_routes = []
        if os.path.exists(const.SAVED_ROUTES_DIR):
            for fragment in os.listdir(const.SAVED_ROUTES_DIR):
                name, ext = os.path.splitext(fragment)
                if ext != ".json":
                    continue
                loaded_routes.append(name)
        
        self.previous_route_names.new_values(loaded_routes, default_val=self.route_name.get())

    def _show_event_details_none(self):
        self.event_details_button.pack_forget()
        self.trainer_notes.pack_forget()
        self.enemy_team_viewer.pack_forget()
        self.enemy_team_viewer.set_team(None)
        self.state_pre_viewer.set_state(self._data.init_route_state)
        self.badge_boost_viewer.set_state(self._data.init_route_state)
        self.state_post_viewer.set_state(self._data.get_final_state())
        if self.current_event_editor is not None:
            self.current_event_editor.pack_forget()
    
    def _show_event_details_non_folder(self, event_obj):
        self.state_pre_viewer.set_state(event_obj.init_state)
        self.badge_boost_viewer.set_state(event_obj.init_state)
        self.state_post_viewer.set_state(event_obj.final_state)
        self.rename_folder_button.disable()
        self.event_details_button.pack()
        if self.current_event_editor is not None:
            self.current_event_editor.pack_forget()
            self.current_event_editor = None

        if isinstance(event_obj, EventItem):
            self.move_group_down_button.disable()
            self.move_group_up_button.disable()
            self.delete_event_button.disable()
            if (
                event_obj.event_definition.learn_move is None or
                event_obj.event_definition.learn_move.source != const.MOVE_SOURCE_LEVELUP
            ):
                self.event_details_button.disable()
                event_obj = event_obj.parent
            else:
                self.event_details_button.enable()
        else:
            self.event_details_button.enable()
            self.move_group_down_button.enable()
            self.move_group_up_button.enable()
            self.delete_event_button.enable()

        if event_obj.event_definition.trainer_name is not None:
            self.trainer_notes.pack()
            self.trainer_notes.load_event(event_obj.event_definition)
            self.enemy_team_viewer.pack()
            self.enemy_team_viewer.set_team(event_obj.event_definition.get_trainer_obj().pkmn, cur_state=event_obj.init_state)
        else:
            self.trainer_notes.pack_forget()
            self.enemy_team_viewer.pack_forget()
            self.enemy_team_viewer.set_team(None)

            # TODO: fix this gross ugly hack
            if isinstance(event_obj, EventGroup) or event_obj.event_definition.get_event_type() == const.TASK_LEARN_MOVE_LEVELUP:
                self.current_event_editor = self.event_editor_lookup.get_editor(
                    route_event_components.EditorParams(
                        event_obj.event_definition.get_event_type(),
                        self._data.defeated_trainers,
                        event_obj.init_state,
                    )
                )
                self.current_event_editor.load_event(event_obj.event_definition)
                self.current_event_editor.pack()
    
    def _show_event_details_folder(self, event_folder_obj:EventFolder):
        self.state_pre_viewer.set_state(event_folder_obj.init_state)
        self.badge_boost_viewer.set_state(event_folder_obj.init_state)
        self.state_post_viewer.set_state(event_folder_obj.final_state)
        self.trainer_notes.pack_forget()
        self.enemy_team_viewer.pack_forget()

        self.move_group_down_button.enable()
        self.move_group_up_button.enable()
        self.rename_folder_button.enable()
        self.event_details_button.pack_forget()
        self.trainer_notes.pack_forget()
        self.enemy_team_viewer.set_team(None)
        if self.current_event_editor is not None:
            self.current_event_editor.pack_forget()
        if len(event_folder_obj.children) == 0:
            self.delete_event_button.enable()
        else:
            self.delete_event_button.disable()
    
    def show_event_details(self, *args, **kwargs):
        event_group = self._data.get_event_obj(self.event_list.get_selected_event_id())
        
        if event_group is None:
            self._show_event_details_none()
        elif isinstance(event_group, EventFolder):
            self._show_event_details_folder(event_group)
        else:
            self._show_event_details_non_folder(event_group)

    def update_existing_event(self, *args, **kwargs):
        if self.current_event_editor is None:
            cur_event = self._data.get_event_obj(self.event_list.get_selected_event_id())
            if isinstance(cur_event, EventGroup) and cur_event.event_definition.trainer_name is not None:
                self._data.replace_event_group(
                    self.event_list.get_selected_event_id(),
                    EventDefinition(
                        trainer_name=cur_event.event_definition.trainer_name,
                        notes=self.trainer_notes.get_event().notes
                    )
                )
            else:
                raise ValueError(f"Cannot update existing event when no event is being edited!")
        
        else:
            self._data.replace_event_group(self.event_list.get_selected_event_id(), self.current_event_editor.get_event())

        self.event_list.refresh()
        self.show_event_details()
    
    def load_route(self, *args, **kwargs):
        if self.route_name.get():
            self._data.load(self.route_name.get())
            self.event_list.refresh()

    def new_solo_pkmn(self, *args, **kwargs):
        self._data.set_solo_pkmn(self.solo_selector.get())
        self.event_list.refresh()

    def reset_to_min_battles(self, *args, **kwargs):
        self._data.load(self.min_battles_selector.get(), min_battles=True)
        self.event_list.refresh()

    def move_group_up(self, event=None):
        self._data.move_event_object(self.event_list.get_selected_event_id(), True)
        self.event_list.refresh()

    def move_group_down(self, event=None):
        self._data.move_event_object(self.event_list.get_selected_event_id(), False)
        self.event_list.refresh()

    def delete_group(self, event=None):
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
            self.new_event_window = TransferEventWindow(
                self,
                event_group_id,
                list(self._data.folder_lookup.keys()),
                self._data.get_event_obj(event_group_id).parent.name,
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
                state = self._data.get_final_state()
            else:
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


class NewFolderWindow(custom_tkinter.Popup):
    def __init__(self, main_window: Main, cur_folder_names, prev_folder_name, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        if main_window is None:
            raise ValueError('Must set main_window when creating NewFolderWindow')
        
        self._cur_folder_names = cur_folder_names
        self._prev_folder_name = prev_folder_name

        self._label = tk.Label(self)
        self._folder_name = custom_tkinter.SimpleEntry(self, callback=self.folder_name_update)
        self._label.grid(row=0, column=0)
        self._folder_name.grid(row=0, column=1)
        self._add_button = custom_tkinter.SimpleButton(self, command=self.create)
        self._cancel_button = custom_tkinter.SimpleButton(self, text="Cancel", command=self._main_window.cancel_new_event)
        self._add_button.grid(row=1, column=0)
        self._cancel_button.grid(row=1, column=1)

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
        self._main_window.finalize_new_folder(self._folder_name.get(), prev_folder_name=self._prev_folder_name)


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
        self._folder_name = custom_tkinter.SimpleOptionMenu(self, option_list=[x for x in self._cur_folder_names if x != prev_folder_name])
        self._new_folder_label.grid(row=1, column=0, padx=10, pady=10)
        self._folder_name.grid(row=1, column=1, padx=10, pady=10)

        self._add_button = custom_tkinter.SimpleButton(self, command=self.transfer, text="Update Folder")
        self._cancel_button = custom_tkinter.SimpleButton(self, text="Cancel", command=self._main_window.cancel_new_event)
        self._add_button.grid(row=2, column=0, padx=10, pady=10)
        self._cancel_button.grid(row=2, column=1, padx=10, pady=10)
    
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

        self.bind('<Control-Return>', self._new_event)
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

        # do the damn thing, zhu li
        self._final_config_path, self._final_route_path, self._final_output_path = \
            route_one_utils.export_to_route_one(self._main_window._data, self._cur_route_name)

        self._config_file_label = tk.Label(self, text=f"Config generated: {self._final_config_path}")
        self._config_file_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self._route_file_label = tk.Label(self, text=f"Route generated: {self._final_route_path}")
        self._route_file_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self._route_jar_label = tk.Label(self, text=f"RouteOne jar Path: {config.get_route_one_path()}")
        self._route_jar_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self._set_jar_button = custom_tkinter.SimpleButton(self, text=f"Set R1 jar path", command=self.set_jar_path)
        self._set_jar_button.grid(row=3, column=0, padx=10, pady=10)
        self._run_route_one_button = custom_tkinter.SimpleButton(self, text=f"Run RouteOne", command=self.run_route_one)
        self._run_route_one_button.grid(row=3, column=1, padx=10, pady=10)

        self._route_one_results_label = tk.Label(self, text=f"")
        self._route_one_results_label.grid(row=4, column=0, padx=10, pady=10)

        self._close_button = custom_tkinter.SimpleButton(self, text="Close", command=self._main_window.cancel_new_event)
        self._close_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def set_jar_path(self, *args, **kwargs):
        jar_path = filedialog.askopenfile().name
        self._route_jar_label.config(text=f"RouteOne jar Path: {jar_path}")
        config.set_route_one_path(jar_path)
        self.lift()

    def run_route_one(self, *args, **kwargs):
        if not config.get_route_one_path():
            self._route_one_results_label.config(text="No RouteOne jar path set, cannot run...")
            return
        
        try:
            result = subprocess.run(
                ["java", "-jar", config.get_route_one_path(), self._final_config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            if result.returncode == 0:
                self._route_one_results_label.config(text=f"RouteOne finished: {self._final_output_path}\nDouble check top of output file for errors")
            else:
                self._route_one_results_label.config(text=f"Error encountered: {result.stdout}")
        except Exception as e:
            self._route_one_results_label.config(text=f"Exception encountered: {type(e)}: {e}")
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
