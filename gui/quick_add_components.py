import tkinter as tk

from gui import custom_tkinter
from pkmn.route_events import EventDefinition, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, TrainerEventDefinition, VitaminEventDefinition, WildPkmnEventDefinition
from pkmn.router import Router
from utils.constants import const
import pkmn.pkmn_db as pkmn_db


class QuickTrainerAdd(tk.Frame):
    def __init__(self, *args, router:Router=None, trainer_select_callback=None, trainer_add_callback=None, area_add_callback=None, **kwargs):
        super().__init__(*args, **kwargs, highlightbackground="black", highlightthickness=2)

        self.router = router
        self.trainer_select_callback = trainer_select_callback
        self.trainer_add_callback = trainer_add_callback
        self.area_add_callback = area_add_callback
        self.force_disable = True

        self.padx = 5
        self.pady = 1
        self.option_menu_width = 15

        self._dropdowns = tk.Frame(self)
        self._dropdowns.pack()

        self._cur_row = 0
        self._trainers_by_loc_label = tk.Label(self._dropdowns, text="Location:", justify=tk.LEFT)
        self._trainers_by_loc = custom_tkinter.SimpleOptionMenu(self._dropdowns, [const.ALL_TRAINERS], callback=self.trainer_filter_callback)
        self._trainers_by_loc.configure(width=self.option_menu_width)
        self._trainers_by_loc_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._trainers_by_loc.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._trainers_by_class_label = tk.Label(self._dropdowns, text="Trainer Class:", justify=tk.LEFT)
        self._trainers_by_class = custom_tkinter.SimpleOptionMenu(self._dropdowns, [const.ALL_TRAINERS], callback=self.trainer_filter_callback)
        self._trainers_by_class.configure(width=self.option_menu_width)
        self._trainers_by_class_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._trainers_by_class.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._trainer_names_label = tk.Label(self._dropdowns, text="Trainer:", justify=tk.LEFT)
        self._trainer_names = custom_tkinter.SimpleOptionMenu(self._dropdowns, [const.NO_TRAINERS], callback=self._trainer_name_callback)
        self._trainer_names.configure(width=self.option_menu_width)
        self._trainer_names_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._trainer_names.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._buttons = tk.Frame(self)
        self._buttons.pack(fill=tk.X, anchor=tk.CENTER, side=tk.BOTTOM)
        self._btn_width = 8

        self._add_trainer = custom_tkinter.SimpleButton(self._buttons, text="Add Trainer", command=self.add_trainer)
        self._add_trainer.grid(row=0, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.E)
        self._add_area = custom_tkinter.SimpleButton(self._buttons, text="Add Area", command=self.add_area)
        self._add_area.grid(row=0, column=1, padx=self.padx, pady=self.pady + 1, sticky=tk.W)
        self.update_button_status()

    def update_button_status(self, allow_enable=None):
        if allow_enable is not None:
            self.force_disable = not allow_enable

        if self.force_disable:
            self._add_trainer.disable()
            self._add_area.disable()
            return
        
        loc_filter = self._trainers_by_loc.get()
        if loc_filter == const.ALL_TRAINERS:
            self._add_area.disable()
        else:
            self._add_area.enable()

        selected_trainer = self._trainer_names.get() 
        if selected_trainer == const.NO_TRAINERS:
            self._add_trainer.disable()
        else:
            self._add_trainer.enable()
    
    def update_pkmn_version(self):
        self._trainers_by_loc.new_values([const.ALL_TRAINERS] + sorted(pkmn_db.trainer_db.get_all_locations()))
        self._trainers_by_class.new_values([const.ALL_TRAINERS] + sorted(pkmn_db.trainer_db.get_all_classes()))

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
        self.update_button_status()

    def _trainer_name_callback(self, *args, **kwargs):
        self.update_button_status()
        selected_trainer = self._trainer_names.get() 
        if selected_trainer == const.NO_TRAINERS:
            return

        if self.trainer_select_callback is not None:
            self.trainer_select_callback(selected_trainer)
    
    def add_trainer(self, *args, **kwargs):
        if self.trainer_add_callback is not None:
            self.trainer_add_callback(EventDefinition(trainer_def=TrainerEventDefinition(self._trainer_names.get())))
    
    def add_area(self, *args, **kwargs):
        if self.area_add_callback is not None:
            self.area_add_callback(self._trainers_by_loc.get())


class QuickWildPkmn(tk.Frame):
    def __init__(self, *args, router:Router=None, event_creation_callback=None, **kwargs):
        super().__init__(*args, **kwargs, highlightbackground="black", highlightthickness=2)

        self.router = router
        self.event_creation_callback = event_creation_callback
        self.force_disable = True

        self.padx = 5
        self.pady = 1
        self.option_menu_width = 15

        self._dropdowns = tk.Frame(self)
        self._dropdowns.pack()

        self._cur_row = 0
        self._pkmn_filter_label = tk.Label(self._dropdowns, text="Filter:", justify=tk.LEFT)
        self._pkmn_filter = custom_tkinter.SimpleEntry(self._dropdowns, callback=self._pkmn_filter_callback)
        self._pkmn_filter.configure(width=self.option_menu_width)
        self._pkmn_filter_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._pkmn_filter.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._pkmn_types_label = tk.Label(self._dropdowns, text="Wild Pkmn:", justify=tk.LEFT)
        self._pkmn_types = custom_tkinter.SimpleOptionMenu(self._dropdowns, [const.NO_POKEMON])
        self._pkmn_types.configure(width=self.option_menu_width)
        self._pkmn_types_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._pkmn_types.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._level_label = tk.Label(self._dropdowns, text="Pkmn Level:", justify=tk.LEFT)
        self._level_val = custom_tkinter.AmountEntry(self._dropdowns, callback=self._pkmn_level_callback)
        self._level_val.configure(width=self.option_menu_width - 5)
        self._level_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._level_val.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._buttons = tk.Frame(self)
        self._buttons.pack(fill=tk.X, anchor=tk.CENTER, side=tk.BOTTOM)
        self._btn_width = 8

        self._add_wild_pkmn = custom_tkinter.SimpleButton(self._buttons, text="Add Wild Pkmn", command=self.add_pkmn_cmd)
        self._add_wild_pkmn.grid(row=0, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.W)
        self.update_button_status()

    def update_button_status(self, allow_enable=None):
        if allow_enable is not None:
            self.force_disable = not allow_enable

        if self.force_disable:
            self._add_wild_pkmn.disable()
            return
        
        if self._pkmn_types.get().strip().startswith(const.NO_POKEMON):
            self._add_wild_pkmn.disable()
        else:
            self._add_wild_pkmn.enable()
    
    def update_pkmn_version(self):
        self._pkmn_types.new_values(pkmn_db.pkmn_db.get_all_names())

    def _pkmn_filter_callback(self, *args, **kwargs):
        self._pkmn_types.new_values(pkmn_db.pkmn_db.get_filtered_names(filter_val=self._pkmn_filter.get().strip()))
        self.update_button_status()

    def _pkmn_level_callback(self, *args, **kwargs):
        try:
            val = int(self._level_val.get().strip())
            if val < 2 or val > 100:
                raise ValueError
        except Exception:
            self._add_wild_pkmn.disable()
            return
        
        self.update_button_status()

    def add_pkmn_cmd(self, *args, **kwargs):
        if self.event_creation_callback is not None:
            self.event_creation_callback(
                EventDefinition(
                    wild_pkmn_info=WildPkmnEventDefinition(
                        self._pkmn_types.get(),
                        int(self._level_val.get().strip())
                    )
                )
            )


class QuickItemAdd(tk.Frame):
    def __init__(self, *args, event_creation_callback=None, **kwargs):
        super().__init__(*args, **kwargs, highlightbackground="black", highlightthickness=2)

        self.cur_state = None
        self.event_creation_callback = event_creation_callback

        self._cur_row = 0
        self.padx = 5
        self.pady = 1
        self.option_menu_width = 20
        self.force_disable = True

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
        self._item_selector = custom_tkinter.SimpleOptionMenu(self._dropdowns, [const.NO_ITEM], callback=self.item_selector_callback)
        self._item_selector.configure(width=self.option_menu_width)
        self._item_selector_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_selector.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)

        self._item_mart_label = tk.Label(self._dropdowns, text="Mart:")
        self._item_mart_selector = custom_tkinter.SimpleOptionMenu(self._dropdowns, [const.ITEM_TYPE_ALL_ITEMS], callback=self.item_filter_callback)
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
        self.update_button_status()

    def update_button_status(self, allow_enable=None):
        if allow_enable is not None:
            self.force_disable = not allow_enable

        if self.force_disable:
            self._acquire_button.disable()
            self._drop_button.disable()
            self._use_button.disable()
            self._tm_hm_button.disable()
            self._buy_button.disable()
            self._sell_button.disable()
            return
        
        cur_item = pkmn_db.item_db.get_item(self._item_selector.get())

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
    
    def update_pkmn_version(self):
        self._item_selector.new_values(pkmn_db.item_db.get_filtered_names())
        self._item_mart_selector.new_values([const.ITEM_TYPE_ALL_ITEMS] + sorted(list(pkmn_db.item_db.mart_items.keys())))

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
        
        self.update_button_status()
    
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