import logging

import tkinter as tk
from tkinter import ttk
from controllers.main_controller import MainController

from gui import custom_components
from pkmn.universal_data_objects import Trainer
from pkmn import universal_utils
from routing.route_events import \
    EventDefinition, EventItem, HoldItemEventDefinition, InventoryEventDefinition, LearnMoveEventDefinition, \
    RareCandyEventDefinition, TrainerEventDefinition, VitaminEventDefinition, WildPkmnEventDefinition, \
    SaveEventDefinition, HealEventDefinition, BlackoutEventDefinition

from utils.constants import const
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


class QuickTrainerAdd(ttk.LabelFrame):
    def __init__(self, controller:MainController, *args, **kwargs):
        kwargs['text'] = "Trainers"
        kwargs['padding'] = 5
        super().__init__(*args, **kwargs)
        self._controller = controller
        self._ignore_preview = False

        self.padx = 5
        self.pady = 1
        self.option_menu_width = 27

        self._dropdowns = ttk.Frame(self)
        self._dropdowns.pack()

        self._cur_row = 0
        self._trainers_by_loc_label = tk.Label(self._dropdowns, text="Location:", justify=tk.LEFT)
        self._trainers_by_loc = custom_components.SimpleOptionMenu(self._dropdowns, [const.ALL_TRAINERS], callback=self.trainer_filter_callback)
        self._trainers_by_loc.configure(width=self.option_menu_width)
        self._trainers_by_loc_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._trainers_by_loc.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._trainers_by_class_label = tk.Label(self._dropdowns, text="Trainer Class:", justify=tk.LEFT)
        self._trainers_by_class = custom_components.SimpleOptionMenu(self._dropdowns, [const.ALL_TRAINERS], callback=self.trainer_filter_callback)
        self._trainers_by_class.configure(width=self.option_menu_width)
        self._trainers_by_class_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._trainers_by_class.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._trainer_names_label = tk.Label(self._dropdowns, text="Trainer:", justify=tk.LEFT)
        self._trainer_names = custom_components.SimpleOptionMenu(self._dropdowns, [const.NO_TRAINERS], callback=self._trainer_name_callback)
        self._trainer_names.configure(width=self.option_menu_width)
        self._trainer_names_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._trainer_names.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._rematches_label = custom_components.CheckboxLabel(self._dropdowns, text="Show Rematches:", flip=True, toggle_command=self.trainer_filter_callback)
        self._rematches_label.configure(width=self.option_menu_width)
        self._rematches_label.grid(row=self._cur_row, column=0, columnspan=2, padx=self.padx, pady=self.pady, sticky=tk.EW)
        self._cur_row += 1

        self._buttons = ttk.Frame(self)
        self._buttons.pack(fill=tk.X, anchor=tk.CENTER, side=tk.BOTTOM)
        self._btn_width = 8

        self._add_trainer = custom_components.SimpleButton(self._buttons, text="Add Trainer", command=self.add_trainer)
        self._add_trainer.grid(row=0, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.E)
        self._add_area = custom_components.SimpleButton(self._buttons, text="Add Area", command=self.add_area)
        self._add_area.grid(row=0, column=1, padx=self.padx, pady=self.pady + 1, sticky=tk.W)
        self.bind(self._controller.register_event_selection(self), self.update_button_status)
        self.bind(self._controller.register_version_change(self), self.update_pkmn_version)
        self.bind(self._controller.register_route_change(self), self.route_change_callback)
        self.update_button_status()

    def update_button_status(self, *args, **kwargs):
        if not self._controller.can_insert_after_current_selection():
            self._add_trainer.disable()
            self._add_area.disable()
            return
        
        selected_trainer = self._get_trainer_name()
        if selected_trainer == const.NO_TRAINERS:
            self._add_trainer.disable()
            self._add_area.disable()
        else:
            self._add_trainer.enable()
            loc_filter = self._trainers_by_loc.get()
            if loc_filter == const.ALL_TRAINERS:
                self._add_area.disable()
            else:
                self._add_area.enable()
    
    def update_pkmn_version(self, *args, **kwargs):
        self._trainers_by_loc.new_values([const.ALL_TRAINERS] + sorted(current_gen_info().trainer_db().get_all_locations()))
        self._trainers_by_class.new_values([const.ALL_TRAINERS] + sorted(current_gen_info().trainer_db().get_all_classes()))
        self._trainer_name_callback()
    
    def route_change_callback(self, *args, **kwargs):
        self.trainer_filter_callback(ignore_trainer_preview=True)
    
    @staticmethod
    def _custom_trainer_name(trainer_obj:Trainer):
        # custom name to inject exp per sec into name results
        return f"({universal_utils.experience_per_second(current_gen_info().get_trainer_timing_info(), trainer_obj)}) {trainer_obj.name}"
        return f"{trainer_obj.name} ({universal_utils.experience_per_second(current_gen_info().get_trainer_timing_info(), trainer_obj)})"
    
    def _get_trainer_name(self):
        # extract raw trainer name from value in list that has exp per sec
        # basically undoing the function above
        name_with_exp_per_sec = self._trainer_names.get()
        return name_with_exp_per_sec[name_with_exp_per_sec.find(')') + 1:].strip()
        return name_with_exp_per_sec[:name_with_exp_per_sec.rfind('(')].strip()

    def trainer_filter_callback(self, *args, ignore_trainer_preview=False, **kwargs):
        loc_filter = self._trainers_by_loc.get()
        class_filter = self._trainers_by_class.get()

        self._ignore_preview = ignore_trainer_preview
        valid_trainers = current_gen_info().trainer_db().get_valid_trainers(
            trainer_class=class_filter,
            trainer_loc=loc_filter,
            defeated_trainers=self._controller.get_defeated_trainers(),
            show_rematches=self._rematches_label.is_checked(),
            custom_name_fn=self._custom_trainer_name
        )
        if not valid_trainers:
            valid_trainers.append(const.NO_TRAINERS)

        self._trainer_names.new_values(valid_trainers)
        self.update_button_status()
        self._ignore_preview = False

    def _trainer_name_callback(self, *args, **kwargs):
        self.update_button_status()
        selected_trainer = self._get_trainer_name()
        if selected_trainer == const.NO_TRAINERS:
            return

        if not self._ignore_preview:
            self._controller.set_preview_trainer(selected_trainer)
    
    def add_trainer(self, *args, **kwargs):
        self._controller.new_event(
            EventDefinition(trainer_def=TrainerEventDefinition(self._get_trainer_name())),
            insert_after=self._controller.get_single_selected_event_id()
        )
    
    def add_area(self, *args, **kwargs):
        insert_after = self._controller.get_single_selected_event_id()
        if insert_after is None:
            return
        
        self._controller.add_area(
            self._trainers_by_loc.get(),
            self._rematches_label.is_checked(),
            insert_after
        )


class QuickWildPkmn(ttk.LabelFrame):
    def __init__(self, controller:MainController, *args, **kwargs):
        kwargs['text'] = "Wild Pkmn"
        kwargs['padding'] = 5
        super().__init__(*args, **kwargs)

        self._controller = controller

        self.padx = 5
        self.pady = 1
        self.option_menu_width = 20

        self._dropdowns = ttk.Frame(self)
        self._dropdowns.pack()

        self._cur_row = 0
        self._pkmn_filter_label = tk.Label(self._dropdowns, text="Filter:", justify=tk.LEFT)
        self._pkmn_filter = custom_components.SimpleEntry(self._dropdowns, callback=self._pkmn_filter_callback)
        self._pkmn_filter.configure(width=self.option_menu_width)
        self._pkmn_filter_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._pkmn_filter.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._pkmn_types_label = tk.Label(self._dropdowns, text="Wild Pkmn:", justify=tk.LEFT)
        self._pkmn_types = custom_components.SimpleOptionMenu(self._dropdowns, [const.NO_POKEMON])
        self._pkmn_types.configure(width=self.option_menu_width)
        self._pkmn_types_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._pkmn_types.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._level_label = tk.Label(self._dropdowns, text="Pkmn Level:", justify=tk.LEFT)
        self._level_val = custom_components.AmountEntry(self._dropdowns, min_val=2, max_val=100, callback=self._update_button_callback_wrapper)
        self._level_val._amount.configure(width=self.option_menu_width - 15)
        self._level_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._level_val.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._quantity_label = tk.Label(self._dropdowns, text="Quantity:", justify=tk.LEFT)
        self._quantity_val = custom_components.AmountEntry(self._dropdowns, min_val=1, callback=self._update_button_callback_wrapper)
        self._quantity_val._amount.configure(width=self.option_menu_width - 15)
        self._quantity_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._quantity_val.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._buttons = ttk.Frame(self)
        self._buttons.pack(fill=tk.X, anchor=tk.CENTER, side=tk.BOTTOM)
        self._btn_width = 8

        self._add_wild_pkmn = custom_components.SimpleButton(self._buttons, text="Add Wild Pkmn", command=self.add_wild_pkmn_cmd)
        self._add_wild_pkmn.grid(row=0, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.W)
        self._add_trainer_pkmn = custom_components.SimpleButton(self._buttons, text="Add Trainer Pkmn", command=self.add_trainer_pkmn_cmd)
        self._add_trainer_pkmn.grid(row=0, column=1, padx=self.padx, pady=self.pady + 1, sticky=tk.W)

        self._level_val.set(5)
        self.bind(self._controller.register_event_selection(self), self.update_button_status)
        self.bind(self._controller.register_version_change(self), self.update_pkmn_version)
        self.update_button_status()

    def update_button_status(self, *args, **kwargs):
        if not self._controller.can_insert_after_current_selection():
            self._add_wild_pkmn.disable()
            self._add_trainer_pkmn.disable()
            return
        
        valid = True
        if self._pkmn_types.get().strip().startswith(const.NO_POKEMON):
            valid = False

        try:
            level = int(self._level_val.get().strip())
            if level < 2 or level > 100:
                raise ValueError
        except Exception:
            valid = False

        try:
            quantity = int(self._quantity_val.get().strip())
            if quantity < 1:
                raise ValueError
        except Exception:
            valid = False

        if not valid:
            self._add_wild_pkmn.disable()
            self._add_trainer_pkmn.disable()
        else:
            self._add_wild_pkmn.enable()
            self._add_trainer_pkmn.enable()

    def update_pkmn_version(self, *args, **kwargs):
        self._pkmn_types.new_values(current_gen_info().pkmn_db().get_all_names())

    def _pkmn_filter_callback(self, *args, **kwargs):
        self._pkmn_types.new_values(current_gen_info().pkmn_db().get_filtered_names(filter_val=self._pkmn_filter.get().strip()))
        self.update_button_status()
    
    def _update_button_callback_wrapper(self, *args, **kwargs):
        self.update_button_status()

    def add_wild_pkmn_cmd(self, *args, **kwargs):
        self._controller.new_event(
            EventDefinition(
                wild_pkmn_info=WildPkmnEventDefinition(
                    self._pkmn_types.get(),
                    int(self._level_val.get().strip()),
                    quantity=int(self._quantity_val.get().strip()),
                )
            ),
            insert_after=self._controller.get_single_selected_event_id()
        )

    def add_trainer_pkmn_cmd(self, *args, **kwargs):
        self._controller.new_event(
            EventDefinition(
                wild_pkmn_info=WildPkmnEventDefinition(
                    self._pkmn_types.get(),
                    int(self._level_val.get().strip()),
                    quantity=int(self._quantity_val.get().strip()),
                    trainer_pkmn=True
                )
            ),
            insert_after=self._controller.get_single_selected_event_id()
        )


class QuickItemAdd(ttk.LabelFrame):
    def __init__(self, controller:MainController, *args, **kwargs):
        kwargs['text'] = "Items"
        kwargs['padding'] = 5
        super().__init__(*args, **kwargs)
        self._controller = controller

        self._cur_row = 0
        self.padx = 2
        self.pady = 1
        self.option_menu_width = 15

        self._dropdowns = ttk.Frame(self)
        self._dropdowns.pack()

        self._item_filter_label = tk.Label(self._dropdowns, text="Search:")
        self._item_filter = custom_components.SimpleEntry(self._dropdowns, callback=self.item_filter_callback, width=self.option_menu_width + 5)
        self._item_filter_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_filter.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)

        self._item_type_label = tk.Label(self._dropdowns, text="Item Type:")
        self._item_type_selector = custom_components.SimpleOptionMenu(self._dropdowns, const.ITEM_TYPES, callback=self.item_filter_callback)
        self._item_type_selector.configure(width=self.option_menu_width)
        self._item_type_label.grid(row=self._cur_row, column=2, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_type_selector.grid(row=self._cur_row, column=3, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._item_selector_label = tk.Label(self._dropdowns, text="Item:")
        self._item_selector = custom_components.SimpleOptionMenu(self._dropdowns, [const.NO_ITEM], callback=self.item_selector_callback)
        self._item_selector.configure(width=self.option_menu_width)
        self._item_selector_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_selector.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)

        self._item_mart_label = tk.Label(self._dropdowns, text="Mart:")
        self._item_mart_selector = custom_components.SimpleOptionMenu(self._dropdowns, [const.ITEM_TYPE_ALL_ITEMS], callback=self.item_filter_callback)
        self._item_mart_selector.configure(width=self.option_menu_width)
        self._item_mart_label.grid(row=self._cur_row, column=2, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_mart_selector.grid(row=self._cur_row, column=3, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._item_amount_label = tk.Label(self._dropdowns, text="Quantity:")
        self._item_amount = custom_components.AmountEntry(self._dropdowns, min_val=1, callback=self.item_selector_callback)
        self._item_amount._amount.configure(width=self.option_menu_width - 10)
        self._item_amount_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        self._item_amount.grid(row=self._cur_row, column=1, padx=self.padx, pady=self.pady, sticky=tk.E)
        self._cur_row += 1

        self._purchase_cost_label = tk.Label(self._dropdowns, text="Purchase:")
        self._purchase_cost_amt = tk.Label(self._dropdowns)
        self._purchase_cost_label.grid(row=self._cur_row, column=0, padx=self.padx, pady=2*self.pady, sticky=tk.W)
        self._purchase_cost_amt.grid(row=self._cur_row, column=1, padx=self.padx, pady=2*self.pady, sticky=tk.E)

        self._sell_cost_label = tk.Label(self._dropdowns, text="Sell Price:")
        self._sell_cost_amt = tk.Label(self._dropdowns)
        self._sell_cost_label.grid(row=self._cur_row, column=2, padx=self.padx, pady=2*self.pady, sticky=tk.W)
        self._sell_cost_amt.grid(row=self._cur_row, column=3, padx=self.padx, pady=2*self.pady, sticky=tk.E)
        self._cur_row += 1

        self._buttons = ttk.Frame(self)
        self._buttons.pack(fill=tk.X, anchor=tk.CENTER, side=tk.BOTTOM)
        self._btn_width = 6

        self._acquire_button = custom_components.SimpleButton(self._buttons, text="Get", width=self._btn_width, command=self._acquire_item)
        self._acquire_button.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self._drop_button = custom_components.SimpleButton(self._buttons, text="Drop", width=self._btn_width, command=self._drop_item)
        self._drop_button.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self._use_button = custom_components.SimpleButton(self._buttons, text="Use", width=self._btn_width, command=self._use_item)
        self._use_button.grid(row=0, column=3, padx=self.padx, pady=self.pady)
        self._hold_button = custom_components.SimpleButton(self._buttons, text="Hold", width=self._btn_width, command=self._hold_item)
        self._hold_button.grid(row=0, column=4, padx=self.padx, pady=self.pady)
        self._tm_hm_button = custom_components.SimpleButton(self._buttons, text="TM/HM", width=self._btn_width, command=self._learn_move)
        self._tm_hm_button.grid(row=0, column=5, padx=self.padx, pady=self.pady)

        self._buy_button = custom_components.SimpleButton(self._buttons, text="Buy", width=self._btn_width, command=self._buy_item)
        self._buy_button.grid(row=0, column=7, padx=self.padx, pady=self.pady)
        self._sell_button = custom_components.SimpleButton(self._buttons, text="Sell", width=self._btn_width, command=self._sell_item)
        self._sell_button.grid(row=0, column=8, padx=self.padx, pady=self.pady)

        self._buttons.columnconfigure(2, weight=1)
        self._buttons.columnconfigure(6, weight=1)
        self.bind(self._controller.register_event_selection(self), self.update_button_status)
        self.bind(self._controller.register_version_change(self), self.update_pkmn_version)
        self.update_button_status()
    
    def update_pkmn_version(self, *args, **kwargs):
        self._item_selector.new_values(current_gen_info().item_db().get_filtered_names())
        self._item_mart_selector.new_values([const.ITEM_TYPE_ALL_ITEMS] + sorted(list(current_gen_info().item_db().mart_items.keys())))

    def update_button_status(self, *args, **kwargs):
        if not self._controller.can_insert_after_current_selection():
            self._acquire_button.disable()
            self._drop_button.disable()
            self._use_button.disable()
            self._hold_button.disable()
            self._tm_hm_button.disable()
            self._buy_button.disable()
            self._sell_button.disable()
            return
        
        cur_item = current_gen_info().item_db().get_item(self._item_selector.get())

        if cur_item is None:
            self._acquire_button.disable()
            self._drop_button.disable()
            self._use_button.disable()
            self._hold_button.disable()
            self._tm_hm_button.disable()
            self._buy_button.disable()
            self._sell_button.disable()
        else:
            if cur_item.move_name is None:
                self._tm_hm_button.disable()
            else:
                self._tm_hm_button.enable()
            
            if cur_item.name in current_gen_info().get_valid_vitamins() or cur_item.name == const.RARE_CANDY:
                self._use_button.enable()
            else:
                self._use_button.disable()

            if current_gen_info().get_generation() != 1:
                self._hold_button.enable()
            else:
                self._hold_button.disable()

            self._acquire_button.enable()
            self._drop_button.enable()
            self._buy_button.enable()
            self._sell_button.enable()

    def item_filter_callback(self, *args, **kwargs):
        item_type = self._item_type_selector.get()
        backpack_filter = False
        if item_type == const.ITEM_TYPE_BACKPACK_ITEMS:
            item_type = const.ITEM_TYPE_ALL_ITEMS
            backpack_filter = True
        
        new_vals = current_gen_info().item_db().get_filtered_names(
            item_type=item_type,
            source_mart=self._item_mart_selector.get()
        )

        if backpack_filter:
            cur_state = self._controller.get_active_state()
            if cur_state is None:
                new_vals = []
            else:
                backpack_items = [x.base_item.name for x in cur_state.inventory.cur_items]
                new_vals = [x for x in new_vals if x in backpack_items]
        
        item_filter_val = self._item_filter.get().strip().lower()
        if item_filter_val:
            new_vals = [x for x in new_vals if item_filter_val in x.lower()]
        
        if not new_vals:
            new_vals.append(const.NO_ITEM)

        self._item_selector.new_values(new_vals)

    def item_selector_callback(self, *args, **kwargs):
        cur_item = current_gen_info().item_db().get_item(self._item_selector.get())

        try:
            item_amt = int(self._item_amount.get())
            cur_item = current_gen_info().item_db().get_item(self._item_selector.get())
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
        if cur_item in current_gen_info().get_valid_vitamins():
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
    
    def _hold_item(self, *arg, **kwargs):
        cur_item = self._item_selector.get()
        self._create_event(
            EventDefinition(
                hold_item=HoldItemEventDefinition(cur_item)
            )
        )

    def _learn_move(self, *arg, **kwargs):
        try:
            cur_item = self._item_selector.get()
            move_name = current_gen_info().item_db().get_item(cur_item).move_name
            cur_state = self._controller.get_active_state()
            
            if cur_item in current_gen_info().item_db().tms:
                self._create_event(
                    EventDefinition(
                        learn_move=LearnMoveEventDefinition(
                            move_name,
                            cur_state.solo_pkmn.get_move_destination(move_name, None)[0],
                            cur_item,
                            const.LEVEL_ANY
                        )
                    )
                )
        except Exception as e:
            logger.error(f"Silently ignoring error when trying to learn move")
            logger.exception(e)

    def _create_event(self, event_def):
        self._controller.new_event(
            event_def,
            self._controller.get_single_selected_event_id()
        )


class QuickMiscEvents(ttk.LabelFrame):
    def __init__(self, controller:MainController, *args, **kwargs):
        kwargs['text'] = "Misc"
        kwargs['padding'] = 5
        super().__init__(*args, **kwargs)
        self._controller = controller
        self._uninitialized = True

        self.padx = 5
        self.pady = 1
        self.option_menu_width = 15

        self._buttons = ttk.Frame(self)
        self._buttons.pack(fill=tk.BOTH, anchor=tk.CENTER)
        self._btn_width = 8

        self._btn_move_tutor = custom_components.SimpleButton(self._buttons, text="Tutor Move", command=self.add_move)
        self._btn_move_tutor.grid(row=0, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.EW)
        self._btn_add_save = custom_components.SimpleButton(self._buttons, text="Add Save", command=self.add_save)
        self._btn_add_save.grid(row=1, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.EW)
        self._btn_add_heal = custom_components.SimpleButton(self._buttons, text="Add Heal", command=self.add_heal)
        self._btn_add_heal.grid(row=2, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.EW)
        self._btn_add_black_out = custom_components.SimpleButton(self._buttons, text="Add Black Out", command=self.add_black_out)
        self._btn_add_black_out.grid(row=3, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.EW)
        self._btn_add_notes = custom_components.SimpleButton(self._buttons, text="Add Notes", command=self.add_notes)
        self._btn_add_notes.grid(row=4, column=0, padx=self.padx, pady=self.pady + 1, sticky=tk.EW)

        self.bind(self._controller.register_event_selection(self), self.update_button_status)
        self.bind(self._controller.register_version_change(self), self.update_pkmn_version)
        self.update_button_status()

    def update_button_status(self, *args, **kwargs):
        if not self._controller.can_insert_after_current_selection() or self._uninitialized:
            self._btn_move_tutor.disable()
            self._btn_add_save.disable()
            self._btn_add_heal.disable()
            self._btn_add_black_out.disable()
            self._btn_add_notes.disable()
            return

        self._btn_move_tutor.enable()
        self._btn_add_save.enable()
        self._btn_add_heal.enable()
        self._btn_add_black_out.enable()
        self._btn_add_notes.enable()
    
    def update_pkmn_version(self, *args, **kwargs):
        self._uninitialized = False

    def add_save(self, *args, **kwargs):
        self._controller.new_event(
            EventDefinition(save=SaveEventDefinition()),
            insert_after=self._controller.get_single_selected_event_id()
        )

    def add_heal(self, *args, **kwargs):
        self._controller.new_event(
            EventDefinition(heal=HealEventDefinition()),
            insert_after=self._controller.get_single_selected_event_id()
        )

    def add_black_out(self, *args, **kwargs):
        self._controller.new_event(
            EventDefinition(blackout=BlackoutEventDefinition()),
            insert_after=self._controller.get_single_selected_event_id()
        )

    def add_move(self, *args, **kwargs):
        cur_state = self._controller.get_active_state()
        self._controller.new_event(
            EventDefinition(learn_move=LearnMoveEventDefinition(
                None,
                cur_state.solo_pkmn.get_move_destination(None, None)[0],
                const.MOVE_SOURCE_TUTOR
            )),
            insert_after=self._controller.get_single_selected_event_id()
        )

    def add_notes(self, *args, **kwargs):
        self._controller.new_event(EventDefinition(), insert_after=self._controller.get_single_selected_event_id())
    
