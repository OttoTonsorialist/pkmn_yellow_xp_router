from ctypes import alignment
import tkinter as tk

from gui import custom_tkinter
from pkmn.route_events import EventDefinition, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, VitaminEventDefinition
from pkmn.router import Router
from utils.constants import const
import pkmn.pkmn_db as pkmn_db


class QuickTrainerComponent(tk.Frame):
    def __init__(self, *args, router:Router=None, trainer_select_callback=None, trainer_add_callback=None, add_wild_pkmn_callback=None, **kwargs):
        super().__init__(*args, **kwargs, highlightbackground="black", highlightthickness=2)

        self.router = router
        self.trainer_select_callback = trainer_select_callback
        self.trainer_add_callback = trainer_add_callback
        self.add_wild_pkmn_callback = add_wild_pkmn_callback

        self.padx = 5
        self.pady = 1
        self.option_menu_width = 20

        self._dropdowns = tk.Frame(self)
        self._dropdowns.pack()

        self._cur_row = 0
        self._trainers_by_loc_label = tk.Label(self._dropdowns, text="Location:", justify=tk.LEFT)
        trainer_locs = [const.ALL_TRAINERS] + sorted(pkmn_db.trainer_db.get_all_locations())
        self._trainers_by_loc = custom_tkinter.SimpleOptionMenu(self._dropdowns, trainer_locs, callback=self.trainer_filter_callback)
        self._trainers_by_loc.configure(width=self.option_menu_width)
        self._trainers_by_loc_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._trainers_by_loc.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._trainers_by_class_label = tk.Label(self._dropdowns, text="Trainer Class:", justify=tk.LEFT)
        trainer_classes = [const.ALL_TRAINERS] + sorted(pkmn_db.trainer_db.get_all_classes())
        self._trainers_by_class = custom_tkinter.SimpleOptionMenu(self._dropdowns, trainer_classes, callback=self.trainer_filter_callback)
        self._trainers_by_class.configure(width=self.option_menu_width)
        self._trainers_by_class_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._trainers_by_class.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._trainer_names_label = tk.Label(self._dropdowns, text="Trainer:", justify=tk.LEFT)
        self._trainer_names = custom_tkinter.SimpleOptionMenu(self._dropdowns, pkmn_db.trainer_db.get_valid_trainers(), callback=self._trainer_name_callback)
        self._trainer_names.configure(width=self.option_menu_width)
        self._trainer_names_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._trainer_names.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._buttons = tk.Frame(self)
        self._buttons.pack(fill=tk.X, anchor=tk.CENTER, side=tk.BOTTOM)
        self._btn_width = 8

        self._add_wild_pkmn = custom_tkinter.SimpleButton(self._buttons, text="Add Wild Pkmn", command=self.add_pkmn_cmd)
        self._add_wild_pkmn.grid(row=0, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.W)
        self._add_trainer = custom_tkinter.SimpleButton(self._buttons, text="Add Trainer", command=self.add_trainer)
        self._add_trainer.grid(row=0, column=1, padx=self.padx, pady=self.pady + 1, sticky=tk.E)

    def trainer_filter_callback(self, *args, **kwargs):
        loc_filter = self._trainers_by_loc.get()
        class_filter = self._trainers_by_class.get()

        valid_trainers = pkmn_db.trainer_db.get_valid_trainers(
            trainer_class=class_filter,
            trainer_loc=loc_filter,
            defeated_trainers=self.router.defeated_trainers
        )
        if not valid_trainers:
            valid_trainers.append(const.NO_TRAINERS)

        self._trainer_names.new_values(valid_trainers)

    def _trainer_name_callback(self, *args, **kwargs):
        if self._trainer_names.get() != const.NO_TRAINERS:
            self._add_trainer.enable()
        else:
            self._add_trainer.disable()

        if self.trainer_select_callback is not None:
            self.trainer_select_callback(pkmn_db.trainer_db.get_trainer(self._trainer_names.get()))
    
    def add_pkmn_cmd(self, *args, **kwargs):
        if self.add_wild_pkmn_callback is not None:
            self.add_wild_pkmn_callback()
    
    def add_trainer(self, *args, **kwargs):
        if self.trainer_add_callback is not None:
            self.trainer_add_callback(EventDefinition(trainer_name=self._trainer_names.get()))


class QuickItemAdd(tk.Frame):
    def __init__(self, *args, event_creation_callback=None, **kwargs):
        super().__init__(*args, **kwargs, highlightbackground="black", highlightthickness=2)

        self.cur_state = None
        self.event_creation_callback = event_creation_callback

        self._cur_row = 0
        self.padx = 5
        self.pady = 1
        self.option_menu_width = 20

        self._dropdowns = tk.Frame(self)
        self._dropdowns.pack()

        self._item_filter_label = tk.Label(self._dropdowns, text="Search:")
        self._item_filter = custom_tkinter.SimpleEntry(self._dropdowns, callback=self.item_filter_callback, width=self.option_menu_width + 5)
        self._item_filter_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_filter.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)

        self._item_type_label = tk.Label(self._dropdowns, text="Item Type:")
        self._item_type_selector = custom_tkinter.SimpleOptionMenu(self._dropdowns, const.ITEM_TYPES, callback=self.item_filter_callback)
        self._item_type_selector.configure(width=self.option_menu_width)
        self._item_type_label.grid(row=self._cur_row, column=2, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_type_selector.grid(row=self._cur_row, column=3, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._item_selector_label = tk.Label(self._dropdowns, text="Item:")
        self._item_selector = custom_tkinter.SimpleOptionMenu(self._dropdowns, pkmn_db.item_db.get_filtered_names(), callback=self.item_selector_callback)
        self._item_selector.configure(width=self.option_menu_width)
        self._item_selector_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_selector.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)

        self._item_mart_label = tk.Label(self._dropdowns, text="Mart:")
        self._item_mart_selector = custom_tkinter.SimpleOptionMenu(self._dropdowns, [const.ITEM_TYPE_ALL_ITEMS] + sorted(list(pkmn_db.item_db.mart_items.keys())), callback=self.item_filter_callback)
        self._item_mart_selector.configure(width=self.option_menu_width)
        self._item_mart_label.grid(row=self._cur_row, column=2, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_mart_selector.grid(row=self._cur_row, column=3, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._item_amount_label = tk.Label(self._dropdowns, text="Quantity:")
        self._item_amount = custom_tkinter.AmountEntry(self._dropdowns, callback=self.item_selector_callback)
        self._item_amount.configure(width=self.option_menu_width - 5)
        self._item_amount_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_amount.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._purchase_cost_label = tk.Label(self._dropdowns, text="Purchase Cost:")
        self._purchase_cost_amt = tk.Label(self._dropdowns)
        self._purchase_cost_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=2*self.pady, sticky=tk.W)
        self._purchase_cost_amt.grid(row=self._cur_row, column=1, padx=self.padx, pady=2*self.pady, sticky=tk.E)

        self._sell_cost_label = tk.Label(self._dropdowns, text="Sell Cost:")
        self._sell_cost_amt = tk.Label(self._dropdowns)
        self._sell_cost_label.grid(row=self._cur_row, column=2, padx=self.padx, pady=2*self.pady, sticky=tk.W)
        self._sell_cost_amt.grid(row=self._cur_row, column=3, padx=self.padx, pady=2*self.pady, sticky=tk.E)
        self._cur_row += 1

        self._buttons = tk.Frame(self)
        self._buttons.pack(fill=tk.X, anchor=tk.CENTER, side=tk.BOTTOM)
        self._btn_width = 8

        self._acquire_button = custom_tkinter.SimpleButton(self._buttons, text="Acquire", width=self._btn_width, command=self._acquire_item)
        self._acquire_button.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self._drop_button = custom_tkinter.SimpleButton(self._buttons, text="Drop", width=self._btn_width, command=self._drop_item)
        self._drop_button.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self._use_button = custom_tkinter.SimpleButton(self._buttons, text="Use", width=self._btn_width, command=self._use_item)
        self._use_button.grid(row=0, column=3, padx=self.padx, pady=self.pady)
        self._tm_hm_button = custom_tkinter.SimpleButton(self._buttons, text="TM/HM", width=self._btn_width, command=self._learn_move)
        self._tm_hm_button.grid(row=0, column=4, padx=self.padx, pady=self.pady)

        self._buy_button = custom_tkinter.SimpleButton(self._buttons, text="Buy", width=self._btn_width, command=self._buy_item)
        self._buy_button.grid(row=0, column=6, padx=self.padx, pady=self.pady)
        self._sell_button = custom_tkinter.SimpleButton(self._buttons, text="Sell", width=self._btn_width, command=self._sell_item)
        self._sell_button.grid(row=0, column=7, padx=self.padx, pady=self.pady)

        self._buttons.columnconfigure(2, weight=1)
        self._buttons.columnconfigure(5, weight=1)
        self.item_selector_callback()

    def item_filter_callback(self, *args, **kwargs):
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
            if self.cur_state is None:
                new_vals = []
            else:
                backpack_items = [x.base_item.name for x in self.cur_state.inventory.cur_items]
                new_vals = [x for x in new_vals if x in backpack_items]
        
        item_filter_val = self._item_filter.get().strip().lower()
        if item_filter_val:
            new_vals = [x for x in new_vals if item_filter_val in x.lower()]
        
        if not new_vals:
            new_vals.append(const.NO_ITEM)

        self._item_selector.new_values(new_vals)

    def item_selector_callback(self, *args, **kwargs):
        cur_item = pkmn_db.item_db.get_item(self._item_selector.get())

        try:
            item_amt = int(self._item_amount.get())
            cur_item = pkmn_db.item_db.get_item(self._item_selector.get())
            self._purchase_cost_amt.config(text=f"{cur_item.purchase_price * item_amt}")
            self._sell_cost_amt.config(text=f"{cur_item.sell_price * item_amt}")
        except Exception as e:
            self._purchase_cost_amt.config(text="")
            self._sell_cost_amt.config(text="")
        
        if cur_item is None:
            self._acquire_button.disable()
            self._drop_button.disable()
            self._use_button.disable()
            self._tm_hm_button.disable()
            self._buy_button.disable()
            self._sell_button.disable()
        else:
            if cur_item.move_name is None:
                self._tm_hm_button.disable()
            else:
                self._tm_hm_button.enable()
            
            if cur_item.name in const.VITAMIN_TYPES or cur_item.name == const.RARE_CANDY:
                self._use_button.enable()
            else:
                self._use_button.disable()

            self._acquire_button.enable()
            self._drop_button.enable()
            self._buy_button.enable()
            self._sell_button.enable()

        
        
    
    def _acquire_item(self, *arg, **kwargs):
        self._create_event(
            EventDefinition(
                item_event_def=InventoryEventDefinition(
                    self._item_selector.get(),
                    int(self._item_amount.get()),
                    True,
                    False
                )
            )
        )

    def _drop_item(self, *arg, **kwargs):
        self._create_event(
            EventDefinition(
                item_event_def=InventoryEventDefinition(
                    self._item_selector.get(),
                    int(self._item_amount.get()),
                    False,
                    False
                )
            )
        )

    def _buy_item(self, *arg, **kwargs):
        self._create_event(
            EventDefinition(
                item_event_def=InventoryEventDefinition(
                    self._item_selector.get(),
                    int(self._item_amount.get()),
                    True,
                    True
                )
            )
        )

    def _sell_item(self, *arg, **kwargs):
        self._create_event(
            EventDefinition(
                item_event_def=InventoryEventDefinition(
                    self._item_selector.get(),
                    int(self._item_amount.get()),
                    False,
                    True
                )
            )
        )
    
    def _use_item(self, *arg, **kwargs):
        cur_item = self._item_selector.get()
        if cur_item in const.VITAMIN_TYPES:
            self._create_event(
                EventDefinition(
                    vitamin=VitaminEventDefinition(cur_item, int(self._item_amount.get()))
                )
            )
        elif cur_item == const.RARE_CANDY:
            self._create_event(
                EventDefinition(
                    rare_candy=RareCandyEventDefinition(int(self._item_amount.get()))
                )
            )

    def _learn_move(self, *arg, **kwargs):
        try:
            cur_item = self._item_selector.get()
            move_name = pkmn_db.item_db.get_item(cur_item).move_name
            
            if cur_item in pkmn_db.item_db.tms:
                self._create_event(
                    EventDefinition(
                        learn_move=LearnMoveEventDefinition(
                            move_name,
                            self.cur_state.solo_pkmn.get_move_destination(move_name, None)[0],
                            cur_item,
                            const.LEVEL_ANY
                        )
                    )
                )
        except Exception as e:
            pass

    def _create_event(self, event_def):
        if self.event_creation_callback is not None:
            self.event_creation_callback(event_def)