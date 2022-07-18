import argparse
from asyncio import constants
from subprocess import call

import tkinter as tk
from tkinter import ANCHOR, ttk
from turtle import back

from gui import custom_tkinter
from pkmn.route_events import EventDefinition, InventoryEventDefinition, WildPkmnEventDefinition
from utils.constants import const
import pkmn.pkmn_db as pkmn_db
import pkmn.router as router


class Main(object):
    def __init__(self, root):
        self._data = router.Router()

        self._root = root
        self._root.minsize(2000, 1200)
        self._root.title("Pokemon Yellow XP Router")

        # fix tkinter bug
        style = ttk.Style()
        style.map("Treeview", foreground=fixed_map("foreground", style), background=fixed_map("background", style))

        # main container for everything to sit in... might be unnecessary?
        self.primary_window = tk.Frame(self._root)
        self.primary_window.pack(fill=tk.BOTH, expand=True)

        self.top_controls = tk.Frame(self.primary_window)
        self.top_controls.pack(expand=False)

        self.solo_selector_label = tk.Label(self.top_controls, text="Solo Pokemon:")
        self.solo_selector_label.grid(row=0, column=0)
        self.solo_selector = custom_tkinter.SimpleOptionMenu(self.top_controls, list(pkmn_db.pkmn_db.data.keys()), callback=self.new_solo_pkmn)
        self.solo_selector.config(width=20)
        self.solo_selector.grid(row=0, column=1)
        self.pkmn_filter_label = tk.Label(self.top_controls, text="Solo Pokemon Filter:")
        self.pkmn_filter_label.grid(row=0, column=2)
        self.pkmn_filter = custom_tkinter.SimpleEntry(self.top_controls, callback=self._pkmn_filter_callback)
        self.pkmn_filter.config(width=30)
        self.pkmn_filter.grid(row=0, column=3)

        self.min_battles_selector_label = tk.Label(self.top_controls, text="Reset to Minimum Battles:")
        self.min_battles_selector_label.grid(row=0, column=4)
        self.min_battles_selector = custom_tkinter.SimpleOptionMenu(self.top_controls, pkmn_db.min_battles_db.data, callback=self.reset_to_min_battles)
        self.min_battles_selector.grid(row=0, column=5)
        self.route_save_button = tk.Button(self.top_controls, text="Save Route", command=self.save_route)
        self.route_save_button.grid(row=1, column=1)
        self.route_name_label = tk.Label(self.top_controls, text="Route Name")
        self.route_name_label.grid(row=1, column=2)
        self.route_name = tk.Entry(self.top_controls)
        self.route_name.grid(row=1, column=3)
        self.route_name.config(width=30)
        self.previous_route_label = tk.Label(self.top_controls, text="Previous Routes")
        self.previous_route_label.grid(row=1, column=4)
        self.previous_route_names = custom_tkinter.SimpleOptionMenu(self.top_controls, ["N/A"], callback=self.update_route_name)
        self.previous_route_names.grid(row=1, column=5)
        self.previous_route_names.config(width=25)

        self.info_panel = tk.Frame(self.primary_window)
        self.info_panel.pack(expand=True, fill=tk.BOTH)

        self.left_info_panel = tk.Frame(self.info_panel)
        self.left_info_panel.grid(row=0, column=0, sticky="nsew")

        # create the main thingy
        self.event_list = custom_tkinter.RouteList(self.left_info_panel)
        self.event_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True, side="left")
        self.scroll_bar = tk.Scrollbar(self.left_info_panel, orient="vertical", command=self.event_list.yview)
        self.scroll_bar.pack(side="right", fill=tk.BOTH)
        self.event_list.configure(yscrollcommand=self.scroll_bar.set)

        self.right_info_panel = tk.Frame(self.info_panel)
        self.right_info_panel.grid(row=0, column=1, sticky="nsew")

        self.stat_info_label = tk.Label(self.right_info_panel, text="Stats with * are calculated with a badge boost")
        self.stat_info_label.config(bg="white")
        self.stat_info_label.pack()

        self.solo_pkmn_frame = tk.Frame(self.right_info_panel)
        self.solo_pkmn_frame.pack()

        self.state_pre_label = tk.Label(self.solo_pkmn_frame, text="Pre-event State:")
        self.state_pre_label.grid(column=0, row=0, padx=10, pady=10)
        self.state_pre_viewer = custom_tkinter.StateViewer(self.solo_pkmn_frame)
        self.state_pre_viewer.grid(column=0, row=1, padx=10, pady=10)
        self.state_post_label = tk.Label(self.solo_pkmn_frame, text="Post-event State:")
        self.state_post_label.grid(column=1, row=0, padx=10, pady=10)
        self.state_post_viewer = custom_tkinter.StateViewer(self.solo_pkmn_frame)
        self.state_post_viewer.grid(column=1, row=1, padx=10, pady=10)

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
        self.state_pre_label.config(text=f"Pre-event state:")
        self.state_post_label.config(text=f"Post-event state:")
    
    def run(self):
        self._root.mainloop()

    def _pkmn_filter_callback(self, *args, **kwargs):
        self.solo_selector.new_values(pkmn_db.pkmn_db.get_filtered_names(filter_val=self.pkmn_filter.get().strip()))
    
    def save_route(self, *args, **kwargs):
        self._data.save(self.route_name.get())
        self.refresh_existing_routes()
    
    def update_route_name(self, *args, **kwargs):
        self.route_name.delete(0, tk.END)
        self.route_name.insert(0, self.previous_route_names.get())
        self.load_route()

    def refresh_existing_routes(self, *args, **kwargs):
        self.previous_route_names.new_values(self._data.refresh_existing_routes(), default_val=self.route_name.get())
    
    def get_event_group_id(self):
        cur_selection = self.event_list.selection()
        if len(cur_selection) == 0:
            return None
        return self.event_list.item(cur_selection[0])['text']

    def show_event_details(self, *args, **kwargs):
        event_group = self._data._get_event_group_info(self.get_event_group_id())[0]
        if event_group is None:
            self.enemy_team_viewer.set_team(None)
            self.state_pre_viewer.set_state(self._data.init_route_state)
            self.state_post_viewer.set_state(self._data.get_final_state())
        else:
            if event_group.event_definition.trainer_name is not None:
                self.enemy_team_viewer.set_team(event_group.event_definition.get_trainer_obj().pkmn)
            elif event_group.event_definition.wild_pkmn_info is not None:
                self.enemy_team_viewer.set_team([event_group.event_definition.get_wild_pkmn()])
            else:
                self.enemy_team_viewer.set_team(None)
            
            self.state_pre_viewer.set_state(event_group.init_state)
            self.state_post_viewer.set_state(event_group.final_state)

    def load_route(self, *args, **kwargs):
        if self.route_name.get():
            self._data.load(self.route_name.get())
            self.refresh_event_list()

    def new_solo_pkmn(self, *args, **kwargs):
        self._data.set_solo_pkmn(self.solo_selector.get())
        self.refresh_event_list()

    def reset_to_min_battles(self, *args, **kwargs):
        self._data.load_min_battle(self.min_battles_selector.get())
        self.refresh_event_list()

    def move_task_up(self, event=None):
        self._data.move_group(self.get_event_group_id(), True)
        self.refresh_event_list()

    def move_task_down(self, event=None):
        self._data.move_group(self.get_event_group_id(), False)
        self.refresh_event_list()

    def clear_selection(self, event=None):
        for sel in self.event_list.selection():
            self.event_list.selection_remove(sel)

    def delete_task(self, event=None):
        self._data.remove_group(self.get_event_group_id())
        self.refresh_event_list()

    def open_new_event_window(self, event=None):
        if self._is_active_window():
            event_group_id = self.get_event_group_id()

            if event_group_id is None:
                state = self._data.get_final_state()
            else:
                state = self._data._get_event_group_info(self.get_event_group_id())[0].init_state

            self.new_event_window = NewEventWindow(self, self._data.defeated_trainers, state, self._root)

    def cancel_new_event(self, event=None):
        if self.new_event_window is not None:
            self.new_event_window.destroy()
            self.new_event_window = None
    
    def new_event(self, event_def):
        self._data.add_event(event_def, insert_before=self.get_event_group_id())
        self.new_event_window.destroy()
        self.new_event_window = None
        self.refresh_event_list()
    
    def _is_active_window(self):
        # returns true if the current window is active (i.e. no sub-windows exist)
        if self.new_event_window is not None and tk.Toplevel.winfo_exists(self.new_event_window):
            return False
        return True


class NewEventWindow(tk.Toplevel):
    def __init__(self, main_window: Main, cur_defeated_trainers, cur_state, *args, **kwargs):
        super().__init__(*args, **kwargs, width=800, height=600)
        if main_window is None:
            raise ValueError('Must set main_window when creating RoutingWindow')
        self.title("Create New Event")
        self._main_window = main_window
        self._cur_defeated_trainers = cur_defeated_trainers
        self._cur_state = cur_state

        self._top_pane = tk.Frame(self, width=1000, height=600)
        self._top_pane.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self._top_pane.grid_propagate(0)

        self._input_frame = tk.Frame(self._top_pane, width=650, height=600)
        self._input_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self._input_frame.grid_propagate(0)

        self._state_viewer = custom_tkinter.StateViewer(self._top_pane)
        self._state_viewer.grid(row=0, column=1, sticky=tk.NSEW)
        self._state_viewer.set_state(cur_state)

        # elements going inside the frame
        self._task_type_label = tk.Label(self._input_frame, text="Event:")
        self._task_type_label.grid(row=0, column=0)
        self._task_type = custom_tkinter.SimpleOptionMenu(self._input_frame, const.ROUTE_EVENT_TYPES, callback=self._task_type_callback)
        self._task_type.grid(row=0, column=1)

        self._vitamin_label = tk.Label(self._input_frame, text="Vitamin Type:")
        self._vitamin_types = custom_tkinter.SimpleOptionMenu(self._input_frame, const.VITAMIN_TYPES, callback=self._vitamin_type_callback)

        self._pkmn_label = tk.Label(self._input_frame, text="Wild Pokemon Type:")
        self._pkmn_types = custom_tkinter.SimpleOptionMenu(self._input_frame, list(pkmn_db.pkmn_db.data.keys()))
        self._pkmn_filter_label = tk.Label(self._input_frame, text="Wild Pokemon Type Filter:")
        self._pkmn_filter = custom_tkinter.SimpleEntry(self._input_frame, callback=self._pkmn_filter_callback)

        self._pkmn_level_label = tk.Label(self._input_frame, text="Wild Pokemon Level:")
        self._pkmn_level = custom_tkinter.SimpleEntry(self._input_frame, callback=self._pkmn_level_callback)

        self._trainers_by_loc_label = tk.Label(self._input_frame, text="Trainer Location Filter:")
        trainer_locs = [const.ALL_TRAINERS] + sorted(pkmn_db.trainer_db.get_all_locations())
        self._trainers_by_loc = custom_tkinter.SimpleOptionMenu(self._input_frame, trainer_locs, callback=self._trainer_filter_callback)

        self._trainers_by_class_label = tk.Label(self._input_frame, text="Trainer Class Filter:")
        trainer_classes = [const.ALL_TRAINERS] + sorted(pkmn_db.trainer_db.get_all_classes())
        self._trainers_by_class = custom_tkinter.SimpleOptionMenu(self._input_frame, trainer_classes, callback=self._trainer_filter_callback)

        self._trainer_names_label = tk.Label(self._input_frame, text="Trainer Name:")
        self._trainer_names = custom_tkinter.SimpleOptionMenu(self._input_frame, list(pkmn_db.trainer_db.data.keys()), callback=self._trainer_name_callback)
        self._trainer_team = custom_tkinter.EnemyPkmnTeam(self._input_frame)

        self._item_type_label = tk.Label(self._input_frame, text="Item Type:")
        self._item_type_selector = custom_tkinter.SimpleOptionMenu(self._input_frame, const.ITEM_TYPES, callback=self._item_filter_callback)
        self._item_mart_label = tk.Label(self._input_frame, text="Mart:")
        self._item_mart_selector = custom_tkinter.SimpleOptionMenu(self._input_frame, [const.ITEM_TYPE_ALL_ITEMS] + sorted(list(pkmn_db.item_db.mart_items.keys())), callback=self._item_filter_callback)
        self._item_filter_label = tk.Label(self._input_frame, text="Item Name Filter:")
        self._item_filter = custom_tkinter.SimpleEntry(self._input_frame, callback=self._item_filter_callback)
        self._item_selector_label = tk.Label(self._input_frame, text="Item:")
        self._item_selector = custom_tkinter.SimpleOptionMenu(self._input_frame, list(pkmn_db.item_db.data.keys()), callback=self._item_selector_callback)
        self._item_amount_label = tk.Label(self._input_frame, text="Num Items:")
        self._item_amount = custom_tkinter.AmountEntry(self._input_frame, callback=self._item_selector_callback)
        self._item_cost_label = tk.Label(self._input_frame, text="Total Cost:")

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
    
    def _hide_wild_pkmn(self):
        self._pkmn_label.grid_remove()
        self._pkmn_types.grid_remove()
        self._pkmn_filter_label.grid_remove()
        self._pkmn_filter.grid_remove()
        self._pkmn_level_label.grid_remove()
        self._pkmn_level.grid_remove()

    def _show_wild_pkmn(self):
        self._pkmn_label.grid(row=1, column=0)
        self._pkmn_types.grid(row=1, column=1)
        self._pkmn_filter_label.grid(row=2, column=0)
        self._pkmn_filter.grid(row=2, column=1)
        self._pkmn_level_label.grid(row=3, column=0)
        self._pkmn_level.grid(row=3, column=1)
    
    def _hide_all_item_obj(self):
        self._item_type_label.grid_remove()
        self._item_type_selector.grid_remove()
        self._item_mart_label.grid_remove()
        self._item_mart_selector.grid_remove()
        self._item_selector_label.grid_remove()
        self._item_selector.grid_remove()
        self._item_filter_label.grid_remove()
        self._item_filter.grid_remove()
        self._item_amount_label.grid_remove()
        self._item_amount.grid_remove()
        self._item_cost_label.grid_remove()
    
    def _show_acquire_item(self):
        self._item_type_label.grid(row=1, column=0)
        self._item_type_selector.grid(row=1, column=1)
        self._item_filter_label.grid(row=2, column=0)
        self._item_filter.grid(row=2, column=1)
        self._item_selector_label.grid(row=3, column=0)
        self._item_selector.grid(row=3, column=1)
        self._item_amount_label.grid(row=4, column=0)
        self._item_amount.grid(row=4, column=1)

    def _show_purchase_item(self):
        self._item_type_label.grid(row=1, column=0)
        self._item_type_selector.grid(row=1, column=1)
        self._item_mart_label.grid(row=2, column=0)
        self._item_mart_selector.grid(row=2, column=1)
        self._item_filter_label.grid(row=3, column=0)
        self._item_filter.grid(row=3, column=1)
        self._item_selector_label.grid(row=4, column=0)
        self._item_selector.grid(row=4, column=1)
        self._item_amount_label.grid(row=5, column=0)
        self._item_amount.grid(row=5, column=1)
        self._item_cost_label.grid(row=6, column=0, columnspan=2)
    
    def _show_use_item(self):
        self._item_type_label.grid(row=1, column=0)
        self._item_type_selector.grid(row=1, column=1)
        self._item_type_selector.set(const.ITEM_TYPE_BACKPACK_ITEMS)
        self._item_filter_label.grid(row=2, column=0)
        self._item_filter.grid(row=2, column=1)
        self._item_selector_label.grid(row=3, column=0)
        self._item_selector.grid(row=3, column=1)
        self._item_amount_label.grid(row=4, column=0)
        self._item_amount.grid(row=4, column=1)

    def _show_sell_item(self):
        self._item_type_label.grid(row=1, column=0)
        self._item_type_selector.grid(row=1, column=1)
        self._item_type_selector.set(const.ITEM_TYPE_BACKPACK_ITEMS)
        self._item_filter_label.grid(row=2, column=0)
        self._item_filter.grid(row=2, column=1)
        self._item_selector_label.grid(row=3, column=0)
        self._item_selector.grid(row=3, column=1)
        self._item_amount_label.grid(row=4, column=0)
        self._item_amount.grid(row=4, column=1)
        self._item_cost_label.grid(row=5, column=0, columnspan=2)
    
    def _trainer_filter_callback(self, *args, **kwargs):
        loc_filter = self._trainers_by_loc.get()
        class_filter = self._trainers_by_class.get()

        valid_trainers = pkmn_db.trainer_db.get_valid_trainers(
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
            trainer = pkmn_db.trainer_db.data.get(self._trainer_names.get())
            if trainer is not None:
                self._trainer_team.set_team(trainer.pkmn)
            else:
                self._trainer_team.set_team(None)
        else:
            self._create_new_event_button.disable()
            self._trainer_team.grid_forget()
    
    def _vitamin_type_callback(self, *args, **kwargs):
        self._create_new_event_button.enable()

    def _pkmn_filter_callback(self, *args, **kwargs):
        self._pkmn_types.new_values(pkmn_db.pkmn_db.get_filtered_names(filter_val=self._pkmn_filter.get().strip()))

    def _pkmn_level_callback(self, *args, **kwargs):
        try:
            val = int(self._pkmn_level.get().strip())
            if val < 2 or val > 100:
                raise ValueError
        except Exception:
            self._create_new_event_button.disable()
            return
        
        if self._pkmn_types.get().strip().startswith(const.NO_POKEMON):
            self._create_new_event_button.disable()
        else:
            self._create_new_event_button.enable()
    
    def _item_filter_callback(self, *args, **kwargs):
        item_type = self._item_type_selector.get()
        backpack_filter = False
        if item_type == const.ITEM_TYPE_BACKPACK_ITEMS:
            item_type = const.ITEM_TYPE_ALL_ITEMS
            backpack_filter = True
        
        new_vals = pkmn_db.item_db.get_filtered_names(
            item_type=item_type,
            source_mart=self._item_mart_selector.get()
        )

        if backpack_filter:
            backpack_items = [x.base_item.name for x in self._cur_state.inventory.cur_items]
            new_vals = [x for x in new_vals if x in backpack_items]
        
        item_filter_val = self._item_filter.get().strip().lower()
        if item_filter_val:
            new_vals = [x for x in new_vals if item_filter_val in x.lower()]

        self._item_selector.new_values(new_vals)

    def _item_selector_callback(self, *args, **kwargs):
        try:
            # first, get the amount the user wants. We always do this to make sure it's actually an int
            # even if we aren't calcing the cost here, it has to be a valid number
            item_amt = int(self._item_amount.get())
            task_type = self._task_type.get()
            if task_type == const.TASK_PURCHASE_ITEM:
                # update the cost if purchasing
                cost = pkmn_db.item_db.data[self._item_selector.get()].purchase_price
                cost *= item_amt
                self._item_cost_label.config(text=f"Total Cost: {cost}")
            elif task_type == const.TASK_SELL_ITEM:
                # update the cost if purchasing
                cost = pkmn_db.item_db.data[self._item_selector.get()].sell_price
                cost *= item_amt
                self._item_cost_label.config(text=f"Total Profit: {cost}")

            self._create_new_event_button.enable()
        except Exception as e:
            self._create_new_event_button.disable()
    
    def _task_type_callback(self, *args, **kwargs):
        task_type = self._task_type.get()
        self._hide_trainers()
        self._hide_vitamins()
        self._hide_all_item_obj()
        self._hide_wild_pkmn()

        if task_type == const.TASK_TRAINER_BATTLE:
            self._show_trainers()
            self._create_new_event_button.disable()

        elif task_type == const.TASK_RARE_CANDY:
            self._create_new_event_button.enable()

        elif task_type == const.TASK_VITAMIN:
            self._show_vitamins()
            self._create_new_event_button.disable()

        elif task_type == const.TASK_FIGHT_WILD_PKMN:
            self._show_wild_pkmn()
            self._create_new_event_button.disable()
        
        elif task_type == const.TASK_GET_FREE_ITEM:
            self._show_acquire_item()
            self._create_new_event_button.enable()

        elif task_type == const.TASK_PURCHASE_ITEM:
            self._show_purchase_item()
            self._create_new_event_button.enable()

        elif task_type == const.TASK_USE_ITEM:
            self._show_use_item()
            self._create_new_event_button.enable()

        elif task_type == const.TASK_SELL_ITEM:
            self._show_sell_item()
            self._create_new_event_button.enable()

        else:
            raise ValueError(f"Unexpected task type: {task_type}")

    def _new_event(self, *args, **kwargs):
        task_type = self._task_type.get()
        if task_type == const.TASK_TRAINER_BATTLE:
            self._main_window.new_event(EventDefinition(trainer_name=self._trainer_names.get()))

        elif task_type == const.TASK_RARE_CANDY:
            self._main_window.new_event(EventDefinition(is_rare_candy=True))

        elif task_type == const.TASK_VITAMIN:
            self._main_window.new_event(EventDefinition(vitamin=self._vitamin_types.get()))

        elif task_type == const.TASK_FIGHT_WILD_PKMN:
            self._main_window.new_event(
                EventDefinition(
                    wild_pkmn_info=WildPkmnEventDefinition(
                        self._pkmn_types.get(),
                        int(self._pkmn_level.get().strip()),
                    )
                )
            )
        
        elif task_type == const.TASK_GET_FREE_ITEM:
            self._main_window.new_event(
                EventDefinition(
                    item_event_def=InventoryEventDefinition(
                        self._item_selector.get(),
                        int(self._item_amount.get()),
                        True,
                        False
                    )
                )
            )

        elif task_type == const.TASK_PURCHASE_ITEM:
            self._main_window.new_event(
                EventDefinition(
                    item_event_def=InventoryEventDefinition(
                        self._item_selector.get(),
                        int(self._item_amount.get()),
                        True,
                        True
                    )
                )
            )

        elif task_type == const.TASK_USE_ITEM:
            self._main_window.new_event(
                EventDefinition(
                    item_event_def=InventoryEventDefinition(
                        self._item_selector.get(),
                        int(self._item_amount.get()),
                        False,
                        False
                    )
                )
            )

        elif task_type == const.TASK_SELL_ITEM:
            self._main_window.new_event(
                EventDefinition(
                    item_event_def=InventoryEventDefinition(
                        self._item_selector.get(),
                        int(self._item_amount.get()),
                        False,
                        True
                    )
                )
            )

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if args.debug:
        const.DEBUG_MODE = True

    Main(tk.Tk()).run()
