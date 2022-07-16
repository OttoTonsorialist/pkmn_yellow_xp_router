import tkinter as tk
from tkinter import ttk

from pip import main

import custom_tkinter
from constants import const
import database
import gui_backend


class Main(object):
    def __init__(self, root):
        self._data = gui_backend.Router()

        self._root = root
        self._root.minsize(2000, 1200)

        # fix tkinter bug
        style = ttk.Style()
        style.map("Treeview", foreground=fixed_map("foreground", style), background=fixed_map("background", style))

        # main container for everything to sit in... might be unnecessary?
        self.primary_window = tk.Frame(self._root)
        self.primary_window.pack(fill=tk.BOTH, expand=True)

        self.top_controls = tk.Frame(self.primary_window)
        self.top_controls.pack(expand=False)

        self.solo_selector_label = tk.Label(self.top_controls, text="Solo Species:")
        self.solo_selector_label.grid(row=0, column=0)
        self.solo_selector = custom_tkinter.SimpleOptionMenu(self.top_controls, list(database.pkmn_db.data.keys()), callback=self.new_solo_pkmn)
        self.solo_selector.grid(row=0, column=1)
        self.min_battles_selector_label = tk.Label(self.top_controls, text="Reset to Minimum Battles:")
        self.min_battles_selector_label.grid(row=1, column=0)
        self.min_battles_selector = custom_tkinter.SimpleOptionMenu(self.top_controls, list(database.min_battles_db.data.keys()), callback=self.reset_to_min_battles)
        self.min_battles_selector.grid(row=1, column=1)
        self.route_save_button = tk.Button(self.top_controls, text="Save Route", command=self.save_route)
        self.route_save_button.grid(row=2, column=0)
        self.route_load_button = tk.Button(self.top_controls, text="Load Route", command=self.load_route)
        self.route_load_button.grid(row=2, column=1)
        self.route_name_label = tk.Label(self.top_controls, text="Route Name")
        self.route_name_label.grid(row=3, column=0)
        self.route_name = tk.Entry(self.top_controls)
        self.route_name.grid(row=3, column=1)
        self.previous_route_names = custom_tkinter.SimpleOptionMenu(self.top_controls, ["N/A"], callback=self.update_route_name)
        self.previous_route_names.grid(row=3, column=2)

        self.info_panel = tk.Frame(self.primary_window)
        self.info_panel.pack(expand=True, fill=tk.BOTH)

        self.left_info_panel = tk.Frame(self.info_panel)
        self.left_info_panel.grid(row=0, column=0, sticky="nsew")

        # create the main thingy
        self.event_list = custom_tkinter.RouteList(self.left_info_panel)
        self.event_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.right_info_panel = tk.Frame(self.info_panel)
        self.right_info_panel.grid(row=0, column=1, sticky="nsew")

        self.solo_pkmn_frame = tk.Frame(self.right_info_panel)
        self.solo_pkmn_frame.pack()

        self.solo_pkmn_pre_label = tk.Label(self.solo_pkmn_frame, text="Pre-event Solo Pokemon:")
        self.solo_pkmn_pre_label.grid(column=0, row=0, padx=10, pady=10)
        self.solo_pkmn_pre_viewer = custom_tkinter.PkmnViewer(self.solo_pkmn_frame)
        self.solo_pkmn_pre_viewer.grid(column=0, row=1, padx=10, pady=10)
        self.solo_pkmn_post_label = tk.Label(self.solo_pkmn_frame, text="Post-event Solo Pokemon:")
        self.solo_pkmn_post_label.grid(column=1, row=0, padx=10, pady=10)
        self.solo_pkmn_post_viewer = custom_tkinter.PkmnViewer(self.solo_pkmn_frame)
        self.solo_pkmn_post_viewer.grid(column=1, row=1, padx=10, pady=10)

        self.enemy_team_label = tk.Label(self.right_info_panel, text="Enemy Team:")
        self.enemy_team_label.pack()
        self.enemy_team_viewer = custom_tkinter.EnemyPkmnTeam(self.right_info_panel, highlightbackground="black", highlightthickness=2)
        self.enemy_team_viewer.pack()

        self.info_panel.grid_rowconfigure(0, weight=1)
        # these uniform values don't have to be a specific value, they just have to match
        self.info_panel.grid_columnconfigure(0, weight=1, uniform="test")
        self.info_panel.grid_columnconfigure(1, weight=1, uniform="test")

        self.bottom_controls = tk.Frame(self.primary_window)
        self.bottom_controls.pack(expand=False)

        self.move_up_button = tk.Button(self.bottom_controls, text='Move Up', command=self.move_task_up)
        self.move_up_button.grid(row=0, column=0)

        self.move_down_button = tk.Button(self.bottom_controls, text='Move Down', command=self.move_task_down)
        self.move_down_button.grid(row=0, column=1)

        self.move_down_button = tk.Button(self.bottom_controls, text='Clear Selection', command=self.clear_selection)
        self.move_down_button.grid(row=0, column=2)

        self.new_event_button = tk.Button(self.bottom_controls, text='New Event', command=self.open_new_event_window)
        self.new_event_button.grid(row=1, column=0)

        self.delete_event_button = tk.Button(self.bottom_controls, text='Delete Event', command=self.delete_task)
        self.delete_event_button.grid(row=1, column=1)

        # keybindings
        self._root.bind('<Control-n>', self.open_new_event_window)
        self._root.bind('<Control-r>', self.refresh_event_list)
        self._root.bind("<<TreeviewSelect>>", self.show_event_details)

        self.refresh_existing_routes()
        self.refresh_event_list()
        self.new_event_window = None

    def refresh_event_list(self, event=None):
        self.event_list.refresh(self._data.all_events)
        name = None
        try:
            name = self._data.solo_pkmn_base.name
        except Exception:
            pass
        self.solo_pkmn_pre_label.config(text=f"Pre-event Solo Pokemon: {name}")
        self.solo_pkmn_post_label.config(text=f"Post-event Solo Pokemon: {name}")
    
    def run(self):
        self._root.mainloop()
    
    def save_route(self, *args, **kwargs):
        self._data.save(self.route_name.get())
        self.refresh_existing_routes()
    
    def update_route_name(self, *args, **kwargs):
        self.route_name.delete(0, tk.END)
        self.route_name.insert(0, self.previous_route_names.get())

    def refresh_existing_routes(self, *args, **kwargs):
        self.previous_route_names.new_values(self._data.refresh_existing_routes(), default_val=self.route_name.get())
    
    def get_event_group_id(self):
        cur_selection = self.event_list.selection()
        if len(cur_selection) == 0:
            return None
        return self.event_list.item(cur_selection[0])['text']

    def show_event_details(self, *args, **kwargs):
        event_group = self._data.get_event_group_info(self.get_event_group_id())[0]
        if event_group is None:
            self.enemy_team_viewer.set_team(None)
            self.solo_pkmn_pre_viewer.set_pkmn(self._data.solo_pkmn_base.get_renderable_pkmn())
            self.solo_pkmn_post_viewer.set_pkmn(self._data.get_final_solo_pkmn().get_renderable_pkmn())
        else:
            self.enemy_team_viewer.set_team(event_group.trainer_obj)
            self.solo_pkmn_pre_viewer.set_pkmn(event_group.init_solo_pkmn.get_renderable_pkmn())
            self.solo_pkmn_post_viewer.set_pkmn(event_group.final_solo_pkmn.get_renderable_pkmn())

    def load_route(self, *args, **kwargs):
        self._data.load(self.route_name.get())
        self.refresh_event_list()

    def new_solo_pkmn(self, *args, **kwargs):
        self._data.set_solo_pkmn(self.solo_selector.get())
        self.refresh_event_list()

    def reset_to_min_battles(self, *args, **kwargs):
        self._data.bulk_fight_trainers(database.min_battles_db.data[self.min_battles_selector.get()])
        self.refresh_event_list()

    def move_task_up(self, event=None):
        self._data.move_group_up(self.get_event_group_id())
        self.refresh_event_list()

    def move_task_down(self, event=None):
        self._data.move_group_down(self.get_event_group_id())
        self.refresh_event_list()

    def clear_selection(self, event=None):
        for sel in self.event_list.selection():
            self.event_list.selection_remove(sel)

    def delete_task(self, event=None):
        self._data.remove_group(self.get_event_group_id())
        self.refresh_event_list()

    def open_new_event_window(self, event=None):
        if self._is_active_window():
            self.new_event_window = NewEventWindow(self, self._data.defeated_trainers, self._root)

    def cancel_new_event(self, event=None):
        if self.new_event_window is not None:
            self.new_event_window.destroy()
            self.new_event_window = None
    
    def new_event(self, trainer_name=None, is_rare_candy=False, vitamin=None):
        self._data.add_event(
            is_rare_candy=is_rare_candy,
            vitamin=vitamin,
            trainer_name=trainer_name,
            insert_before=self.get_event_group_id()
        )
        self.new_event_window.destroy()
        self.new_event_window = None
        self.refresh_event_list()
    
    def _is_active_window(self):
        # returns true if the current window is active (i.e. no sub-windows exist)
        if self.new_event_window is not None and tk.Toplevel.winfo_exists(self.new_event_window):
            return False
        return True


class NewEventWindow(tk.Toplevel):
    def __init__(self, main_window: Main, cur_defeated_trainers, *args,  task=None, **kwargs):
        super().__init__(*args, **kwargs, width=800, height=600)
        if main_window is None:
            raise ValueError('Must set main_window when creating RoutingWindow')
        self._main_window = main_window
        self._cur_defeated_trainers = cur_defeated_trainers

        self._input_frame = tk.Frame(self, width=1000, height=600)
        self._input_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self._input_frame.grid_propagate(0)

        # elements going inside the frame
        self._task_type_label = tk.Label(self._input_frame, text="Event:")
        self._task_type_label.grid(row=0, column=0)
        self._task_type = custom_tkinter.SimpleOptionMenu(self._input_frame, const.ROUTE_EVENT_TYPES, callback=self._task_type_callback)
        self._task_type.grid(row=0, column=1)

        self._vitamin_label = tk.Label(self._input_frame, text="Vitamin Type:")
        self._vitamin_types = custom_tkinter.SimpleOptionMenu(self._input_frame, const.VITAMIN_TYPES, callback=self._vitamin_type_callback)

        self._trainers_by_loc_label = tk.Label(self._input_frame, text="Trainer Location Filter:")
        trainer_locs = [const.ALL_TRAINERS] + sorted(database.trainer_db.get_all_locations())
        self._trainers_by_loc = custom_tkinter.SimpleOptionMenu(self._input_frame, trainer_locs, callback=self._trainer_filter_callback)

        self._trainers_by_class_label = tk.Label(self._input_frame, text="Trainer Class Filter:")
        trainer_classes = [const.ALL_TRAINERS] + sorted(database.trainer_db.get_all_classes())
        self._trainers_by_class = custom_tkinter.SimpleOptionMenu(self._input_frame, trainer_classes, callback=self._trainer_filter_callback)

        self._trainer_names_label = tk.Label(self._input_frame, text="Trainer Name:")
        self._trainer_names = custom_tkinter.SimpleOptionMenu(self._input_frame, list(database.trainer_db.data.keys()), callback=self._trainer_name_callback)

        self._trainer_team = custom_tkinter.EnemyPkmnTeam(self._input_frame)

        self._create_new_event_button = custom_tkinter.SimpleButton(self, text="Add Event", command=self._new_event)
        self._create_new_event_button.grid(row=1, column=0)
        self._create_new_event_button.disable()

        self._cancel_button = custom_tkinter.SimpleButton(self, text="Cancel", command=self._main_window.cancel_new_event)
        self._cancel_button.grid(row=1, column=1)
        self._cancel_button.enable()

        self.bind('<Control-Return>', self._new_event)
        self.bind('<Escape>', self._main_window.cancel_new_event)
        self._task_type.focus_set()
        self._task_type_callback()
    
    def _hide_trainers(self):
        self._trainers_by_loc_label.grid_remove()
        self._trainers_by_loc.grid_remove()
        self._trainers_by_class_label.grid_remove()
        self._trainers_by_class.grid_remove()
        self._trainer_names_label.grid_remove()
        self._trainer_names.grid_remove()
        self._trainer_team.grid_remove()

    def _show_trainers(self):
        self._trainers_by_loc_label.grid(row=2, column=0)
        self._trainers_by_loc.grid(row=2, column=1)
        self._trainers_by_class_label.grid(row=3, column=0)
        self._trainers_by_class.grid(row=3, column=1)
        self._trainer_names_label.grid(row=4, column=0)
        self._trainer_names.grid(row=4, column=1)
        self._trainer_team.grid(row=5, column=0, columnspan=2)

    def _hide_vitamins(self):
        self._vitamin_label.grid_remove()
        self._vitamin_types.grid_remove()

    def _show_vitamins(self):
        self._vitamin_label.grid(row=1, column=0)
        self._vitamin_types.grid(row=1, column=1)
    
    def _trainer_filter_callback(self, *args, **kwargs):
        loc_filter = self._trainers_by_loc.get()
        class_filter = self._trainers_by_class.get()

        valid_trainers = database.trainer_db.get_valid_trainers(
            trainer_class=class_filter,
            trainer_loc=loc_filter,
            defeated_trainers=self._cur_defeated_trainers
        )
        if not valid_trainers:
            valid_trainers.append(const.NO_TRAINERS)

        self._trainer_names.new_values(valid_trainers)

    def _trainer_name_callback(self, *args, **kwargs):
        if self._trainer_names.get() != const.NO_TRAINERS:
            self._create_new_event_button.enable()
            self._trainer_team.grid(row=5, column=0, columnspan=2)
            self._trainer_team.set_team(database.trainer_db.data.get(self._trainer_names.get()))
        else:
            self._create_new_event_button.disable()
            self._trainer_team.grid_forget()
    
    def _vitamin_type_callback(self, *args, **kwargs):
        self._create_new_event_button.enable()
    
    def _task_type_callback(self, *args, **kwargs):
        task_type = self._task_type.get()
        if task_type == const.TASK_TRAINER_BATTLE:
            self._show_trainers()
            self._hide_vitamins()
            self._create_new_event_button.disable()

        elif task_type == const.TASK_RARE_CANDY:
            self._hide_trainers()
            self._hide_vitamins()
            self._create_new_event_button.enable()

        elif task_type == const.TASK_VITAMIN:
            self._hide_trainers()
            self._show_vitamins()
            self._create_new_event_button.disable()

        else:
            raise ValueError(f"Unexpected task type: {task_type}")

    def _new_event(self, *args, **kwargs):
        task_type = self._task_type.get()
        if task_type == const.TASK_TRAINER_BATTLE:
            self._main_window.new_event(trainer_name=self._trainer_names.get())

        elif task_type == const.TASK_RARE_CANDY:
            self._main_window.new_event(is_rare_candy=True)

        elif task_type == const.TASK_VITAMIN:
            self._main_window.new_event(vitamin=self._vitamin_types.get())

        else:
            raise ValueError(f"Unexpected task type: {task_type}")
        

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
    Main(tk.Tk()).run()
