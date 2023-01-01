import tkinter as tk
import customtkinter as ctk

from gui import custom_components
from gui.pkmn_components import EnemyPkmnTeam
from utils.constants import const
import pkmn
from routing.route_events import BlackoutEventDefinition, EventDefinition, HealEventDefinition, HoldItemEventDefinition, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, SaveEventDefinition, VitaminEventDefinition, WildPkmnEventDefinition
from utils.config_manager import config


class EditorParams:
    def __init__(self, event_type, cur_defeated_trainers, cur_state):
        self.event_type = event_type
        self.cur_defeated_trainers = cur_defeated_trainers
        self.cur_state = cur_state


class EventEditorBase(ctk.CTkFrame):
    def __init__(self, parent, event_button, editor_params: EditorParams, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, bg_color=config.get_background_color())
        self.event_button = event_button
        self.event_button.disable()
        self.editor_params = editor_params

        self._cur_row = 0
    
    def configure(self, editor_params):
        self.editor_params = editor_params
        self.event_button.enable()
    
    def load_event(self, event_def:EventDefinition):
        pass

    def get_event(self) -> EventDefinition:
        return None


class NotesEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._notes_label = ctk.CTkLabel(self, text="Notes:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._notes_label.grid(row=self._cur_row, column=0, sticky=tk.W, padx=5, pady=5)
        self._stat_label = ctk.CTkLabel(self, text="Stats with * are calculated with a badge boost", bg_color=config.get_contrast_color(), fg_color=config.get_text_color())
        self._stat_label.grid(row=self._cur_row, column=1, sticky=tk.W, padx=5, pady=5)
        self._padding_label = ctk.CTkLabel(self, text="", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._padding_label.grid(row=self._cur_row, column=2, sticky=tk.W, padx=5, pady=5)
        self._cur_row += 1

        self._notes = tk.Text(self, height=8)
        self._notes.grid(row=self._cur_row, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self._cur_row += 1

        self.columnconfigure(0, weight=1, uniform="padding")
        self.columnconfigure(2, weight=1, uniform="padding")
    
    def configure(self, editor_params):
        self.editor_params = editor_params
        self.event_button.enable()
    
    def load_event(self, event_def:EventDefinition):
        self._notes.delete(1.0, tk.END)
        if event_def is not None:
            self._notes.insert(1.0, event_def.notes)

    def get_event(self) -> EventDefinition:
        return EventDefinition(notes=self._notes.get(1.0, tk.END).strip())


class TrainerFightEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cached_defeated_trainers = self.editor_params.cur_defeated_trainers

        self._trainers_by_loc_label = ctk.CTkLabel(self, text="Trainer Location Filter:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        trainer_locs = [const.ALL_TRAINERS] + sorted(pkmn.current_gen_info().trainer_db().get_all_locations())
        self._trainers_by_loc = custom_components.SimpleOptionMenu(self, trainer_locs, callback=self._trainer_filter_callback)
        self._trainers_by_loc_label.grid(row=self._cur_row, column=0)
        self._trainers_by_loc.grid(row=self._cur_row, column=1)
        self._cur_row += 1

        self._trainers_by_class_label = ctk.CTkLabel(self, text="Trainer Class Filter:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        trainer_classes = [const.ALL_TRAINERS] + sorted(pkmn.current_gen_info().trainer_db().get_all_classes())
        self._trainers_by_class = custom_components.SimpleOptionMenu(self, trainer_classes, callback=self._trainer_filter_callback)

        self._trainer_names_label = ctk.CTkLabel(self, text="Trainer Name:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._trainer_names = custom_components.SimpleOptionMenu(self, pkmn.current_gen_info().trainer_db().get_valid_trainers(), callback=self._trainer_name_callback)
        self._trainer_team = EnemyPkmnTeam(self)

        self._trainers_by_class_label.grid(row=self._cur_row, column=0)
        self._trainers_by_class.grid(row=self._cur_row, column=1)
        self._cur_row += 1

        self._trainer_names_label.grid(row=self._cur_row, column=0)
        self._trainer_names.grid(row=self._cur_row, column=1)
        self._cur_row += 1

        self._trainer_team.grid(row=self._cur_row, column=0, columnspan=2)
        self._cur_row += 1

    def _trainer_filter_callback(self, *args, **kwargs):
        loc_filter = self._trainers_by_loc.get()
        class_filter = self._trainers_by_class.get()

        valid_trainers = pkmn.current_gen_info().trainer_db().get_valid_trainers(
            trainer_class=class_filter,
            trainer_loc=loc_filter,
            defeated_trainers=self.cached_defeated_trainers
        )
        if not valid_trainers:
            valid_trainers.append(const.NO_TRAINERS)

        self._trainer_names.new_values(valid_trainers)

    def _trainer_name_callback(self, *args, **kwargs):
        if self._trainer_names.get() != const.NO_TRAINERS:
            self.event_button.enable()
            self._trainer_team.grid(row=5, column=0, columnspan=2)
            trainer = pkmn.current_gen_info().trainer_db().get_trainer(self._trainer_names.get())
            if trainer is not None:
                self._trainer_team.set_team(trainer.pkmn, cur_state=self.editor_params.cur_state)
            else:
                self._trainer_team.set_team(None)
        else:
            self.event_button.disable()
            self._trainer_team.grid_forget()
    
    def _trainer_filter_callback(self, *args, **kwargs):
        loc_filter = self._trainers_by_loc.get()
        class_filter = self._trainers_by_class.get()

        valid_trainers = pkmn.current_gen_info().trainer_db().get_valid_trainers(
            trainer_class=class_filter,
            trainer_loc=loc_filter,
            defeated_trainers=self.cached_defeated_trainers
        )
        if not valid_trainers:
            valid_trainers.append(const.NO_TRAINERS)

        self._trainer_names.new_values(valid_trainers)
    
    def configure(self, editor_params):
        super().configure(editor_params)
        self._trainers_by_loc.set(const.ALL_TRAINERS)
        self._trainers_by_class.set(const.ALL_TRAINERS)
        self._trainer_names.set("")
        self._trainer_filter_callback()
    
    def load_event(self, event_def):
        super().load_event(event_def)
        # note, by the current route, the trainer of the even we are loading is guaranteed to be "defeated"
        # So, we have to manually hide it to the list of all defeated trainers
        self.cached_defeated_trainers = self.editor_params.cur_defeated_trainers.difference(set(event_def.trainer_def.trainer_name))
        self._trainers_by_loc.set(const.ALL_TRAINERS)
        self._trainers_by_class.set(const.ALL_TRAINERS)
        self._trainer_names.set(event_def.trainer_def.trainer_name)
    
    def get_event(self):
        return EventDefinition(trainer_def=TrainerFightEditor(self._trainer_names.get()))


class VitaminEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._vitamin_label = ctk.CTkLabel(self, text="Vitamin Type:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._vitamin_types = custom_components.SimpleOptionMenu(self, const.VITAMIN_TYPES)
        self._vitamin_label.grid(row=self._cur_row, column=0)
        self._vitamin_types.grid(row=self._cur_row, column=1)
        self._cur_row += 1

        self._item_amount_label = ctk.CTkLabel(self, text="Num Vitamins:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_amount = custom_components.AmountEntry(self, callback=self._amount_update, bg_color=config.get_background_color())
        self._item_amount_label.grid(row=self._cur_row, column=0)
        self._item_amount.grid(row=self._cur_row, column=1)
        self._cur_row += 1

    def _amount_update(self, *args, **kwargs):
        val = self._item_amount.get()
        try:
            val = int(val)
            if val > 0:
                self.event_button.enable()
            else:
                self.event_button.disable()
        except Exception as e:
            self.event_button.disable()
    
    def load_event(self, event_def):
        super().load_event(event_def)
        self._vitamin_types.set(event_def.vitamin.vitamin)
        self._item_amount.set(str(event_def.vitamin.amount))

    def get_event(self):
        return EventDefinition(vitamin=VitaminEventDefinition(self._vitamin_types.get(), int(self._item_amount.get())))


class RareCandyEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_button.enable()
        self._item_amount_label = ctk.CTkLabel(self, text="Num Rare Candies:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_amount = custom_components.AmountEntry(self, callback=self._amount_update, bg_color=config.get_background_color())
        self._item_amount_label.grid(row=self._cur_row, column=0)
        self._item_amount.grid(row=self._cur_row, column=1)
        self._cur_row += 1
    
    def _amount_update(self, *args, **kwargs):
        val = self._item_amount.get()
        try:
            val = int(val)
            if val > 0:
                self.event_button.enable()
            else:
                self.event_button.disable()
        except Exception as e:
            self.event_button.disable()
    
    def load_event(self, event_def):
        super().load_event(event_def)
        self._item_amount.set(str(event_def.rare_candy.amount))

    def get_event(self):
        return EventDefinition(rare_candy=RareCandyEventDefinition(int(self._item_amount.get())))


class LearnMoveEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._source_label = ctk.CTkLabel(self, bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._source_label.grid(row=self._cur_row, column=0, columnspan=2)
        self._cur_row += 1

        self._move_name_label = ctk.CTkLabel(self, bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._move_name_label.grid(row=self._cur_row, column=0, columnspan=2)
        self._cur_row += 1

        self._destination_label = ctk.CTkLabel(self, text="Move Destination:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._destination = custom_components.SimpleOptionMenu(self, [None])
        self._destination_label.grid(row=self._cur_row, column=0)
        self._destination.grid(row=self._cur_row, column=1)
        self._cur_row += 1

        # Not a visual component, but we want a way to be able to pull the current move being referenced
        self._move = None
        self._level = const.LEVEL_ANY

        self._item_type_label = ctk.CTkLabel(self, text="Item Type:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_type_selector = custom_components.SimpleOptionMenu(self, [const.ITEM_TYPE_ALL_ITEMS, const.ITEM_TYPE_BACKPACK_ITEMS, const.ITEM_TYPE_TM], callback=self._item_filter_callback)
        self._item_type_row = self._cur_row
        self._cur_row += 1

        self._item_filter_label = ctk.CTkLabel(self, text="Item Name Filter:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_filter = custom_components.SimpleEntry(self, callback=self._item_filter_callback)
        self._item_filter_row = self._cur_row
        self._cur_row += 1

        self._item_selector_label = ctk.CTkLabel(self, text="Move:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_selector = custom_components.SimpleOptionMenu(self, [None], callback=self._move_selected_callback)
        self._item_selector_row = self._cur_row
        self._cur_row += 1

    def _item_filter_callback(self, *args, **kwargs):
        item_type = self._item_type_selector.get()
        backpack_filter = False
        if item_type == const.ITEM_TYPE_BACKPACK_ITEMS:
            item_type = const.ITEM_TYPE_TM
            backpack_filter = True
        
        new_vals = pkmn.current_gen_info().item_db().get_filtered_names(item_type=item_type)

        if backpack_filter:
            backpack_items = [x.base_item.name for x in self.editor_params.cur_state.inventory.cur_items]
            new_vals = [x for x in new_vals if x in backpack_items]
        
        item_filter_val = self._item_filter.get().strip().lower()
        if item_filter_val:
            new_vals = [x for x in new_vals if item_filter_val in x.lower()]
        
        if not new_vals:
            new_vals = [const.NO_ITEM]

        self._item_selector.new_values(new_vals)
    
    def _move_selected_callback(self, *args, **kwargs):
        if self.editor_params.event_type == const.TASK_LEARN_MOVE_TM:
            item_obj = pkmn.current_gen_info().item_db().get_item(self._item_selector.get())
            if item_obj is not None:
                self._move = item_obj.move_name
            else:
                self._move = None
            self._move_name_label.configure(text=f"Move: {self._move}")
        
        if self._move is None:
            self.event_button.disable()
            return
        
        learn_move_info = self.editor_params.cur_state.solo_pkmn.get_move_destination(self._move, None)
        if not learn_move_info[1]:
            if learn_move_info[0] is None:
                self._destination.set(const.MOVE_DONT_LEARN)
            else:
                self._destination.set(const.MOVE_SLOT_TEMPLATE.format(learn_move_info[0] + 1, None))
            self._destination.disable()
            self.event_button.enable()
        else:
            self._destination.enable()
            self.event_button.enable()

    def configure(self, editor_params):
        super().configure(editor_params)
        self._destination.new_values(
            [const.MOVE_DONT_LEARN] +
            [
                const.MOVE_SLOT_TEMPLATE.format(idx + 1, x) for idx, x in
                enumerate(self.editor_params.cur_state.solo_pkmn.move_list)
            ]
        )
        if self.editor_params.event_type == const.TASK_LEARN_MOVE_LEVELUP:
            self._source_label.configure(text="Source: Levelup")
            self._item_type_label.grid_forget()
            self._item_type_selector.grid_forget()
            self._item_filter_label.grid_forget()
            self._item_filter.grid_forget()
            self._item_selector_label.grid_forget()
            self._item_selector.grid_forget()
        else:
            self._source_label.configure(text="Source: TM/HM")
            self._item_type_label.grid(row=self._item_type_row, column=0)
            self._item_type_selector.grid(row=self._item_type_row, column=1)
            self._item_filter_label.grid(row=self._item_filter_row, column=1)
            self._item_filter.grid(row=self._item_filter_row, column=1)
            self._item_selector_label.grid(row=self._item_selector_row, column=0)
            self._item_selector.grid(row=self._item_selector_row, column=1)

        self._item_filter_callback()
    
    def load_event(self, event_def):
        super().load_event(event_def)
        if self.editor_params.event_type == const.TASK_LEARN_MOVE_LEVELUP:
            self._move = event_def.learn_move.move_to_learn
            self._move_name_label.configure(text=f"Move: {self._move}")
            self._level = event_def.learn_move.level
        else:
            self._item_type_selector.set(const.ITEM_TYPE_TM)
            self._item_filter.set("")
            self._item_selector.set(event_def.learn_move.source)
            self._level = const.LEVEL_ANY
        
        self._move_selected_callback()
        if event_def.learn_move.destination is None:
            self._destination.set(const.MOVE_DONT_LEARN)
        else:
            self._destination.set(self._destination.cur_options[event_def.learn_move.destination + 1])

    def get_event(self):
        dest = self._destination.get()
        if dest == const.MOVE_DONT_LEARN:
            dest = None
        else:
            # ugly, but wtv. Extract the number from that big string. It's always 1 digit, following the '#'
            try:
                dest = int(dest.split('#')[1][0]) - 1
            except Exception:
                raise ValueError(f"Failed to extract slot destination from string '{dest}'")
        
        source = const.MOVE_SOURCE_LEVELUP if self.editor_params.event_type == const.TASK_LEARN_MOVE_LEVELUP else self._item_selector.get()

        return EventDefinition(learn_move=LearnMoveEventDefinition(self._move, dest, source, level=self._level))
    

class WildPkmnEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pkmn_label = ctk.CTkLabel(self, text="Wild Pokemon Type:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._pkmn_types = custom_components.SimpleOptionMenu(self, pkmn.current_gen_info().pkmn_db().get_all_names())
        self._pkmn_label.grid(row=self._cur_row, column=0)
        self._pkmn_types.grid(row=self._cur_row, column=1)
        self._cur_row += 1

        self._pkmn_filter_label = ctk.CTkLabel(self, text="Wild Pokemon Type Filter:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._pkmn_filter = custom_components.SimpleEntry(self, callback=self._pkmn_filter_callback)
        self._pkmn_filter_label.grid(row=self._cur_row, column=0)
        self._pkmn_filter.grid(row=self._cur_row, column=1)
        self._cur_row += 1

        self._pkmn_level_label = ctk.CTkLabel(self, text="Wild Pokemon Level:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._pkmn_level = custom_components.AmountEntry(self, callback=self._update_button_status, bg_color=config.get_background_color())
        self._pkmn_level_label.grid(row=self._cur_row, column=0)
        self._pkmn_level.grid(row=self._cur_row, column=1)
        self._cur_row += 1

        self._quantity_label = ctk.CTkLabel(self, text="Num Pkmn:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._quantity = custom_components.AmountEntry(self, callback=self._update_button_status, bg_color=config.get_background_color())
        self._quantity_label.grid(row=self._cur_row, column=0)
        self._quantity.grid(row=self._cur_row, column=1)
        self._cur_row += 1

        self._pkmn_trainer_flag = custom_components.CheckboxLabel(self, text="Is Trainer Pkmn?", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._pkmn_trainer_flag.grid(row=self._cur_row, column=0, columnspan=2)
        self._cur_row += 1
    
    def _update_button_status(self, *args, **kwargs):
        valid = True
        try:
            pkmn_level = int(self._pkmn_level.get().strip())
            if pkmn_level < 2 or pkmn_level > 100:
                raise ValueError
        except Exception:
            valid = False

        if self._pkmn_types.get().strip().startswith(const.NO_POKEMON):
            valid = False

        try:
            quantity = int(self._quantity.get().strip())
            if quantity < 1:
                raise ValueError
        except Exception:
            valid = False
        
        if valid:
            self.event_button.enable()
        else:
            self.event_button.disable()

    def _pkmn_filter_callback(self, *args, **kwargs):
        self._pkmn_types.new_values(pkmn.current_gen_info().pkmn_db().get_filtered_names(filter_val=self._pkmn_filter.get().strip()))
        self._update_button_status()

    def configure(self, editor_params):
        super().configure(editor_params)
        self._pkmn_filter.set("")
        self._pkmn_level.set("1")
        self._quantity.set("1")
        self._pkmn_trainer_flag.set_checked(False)
    
    def load_event(self, event_def):
        super().load_event(event_def)
        self._pkmn_filter.set("")
        self._pkmn_level.set(str(event_def.wild_pkmn_info.level))
        self._pkmn_types.set(event_def.wild_pkmn_info.name)
        self._quantity.set(str(event_def.wild_pkmn_info.quantity))
        self._pkmn_trainer_flag.set_checked(event_def.wild_pkmn_info.trainer_pkmn)

    def get_event(self):
        return EventDefinition(
            wild_pkmn_info=WildPkmnEventDefinition(
                self._pkmn_types.get(),
                int(self._pkmn_level.get().strip()),
                quantity=int(self._quantity.get().strip()),
                trainer_pkmn=self._pkmn_trainer_flag.is_checked()
            )
        )


class InventoryEventEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._item_type_label = ctk.CTkLabel(self, text="Item Type:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_type_selector = custom_components.SimpleOptionMenu(self, const.ITEM_TYPES, callback=self._item_filter_callback)
        self._item_type_row = self._cur_row
        self._cur_row += 1

        self._item_mart_label = ctk.CTkLabel(self, text="Mart:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_mart_selector = custom_components.SimpleOptionMenu(self, [const.ITEM_TYPE_ALL_ITEMS] + sorted(list(pkmn.current_gen_info().item_db().mart_items.keys())), callback=self._item_filter_callback)
        self._item_mart_row = self._cur_row
        self._cur_row += 1

        self._item_filter_label = ctk.CTkLabel(self, text="Item Name Filter:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_filter = custom_components.SimpleEntry(self, callback=self._item_filter_callback)
        self._item_filter_row = self._cur_row
        self._cur_row += 1

        self._item_selector_label = ctk.CTkLabel(self, text="Item:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_selector = custom_components.SimpleOptionMenu(self, pkmn.current_gen_info().item_db().get_filtered_names(), callback=self._item_selector_callback)
        self._item_selector_row = self._cur_row
        self._cur_row += 1

        self._item_amount_label = ctk.CTkLabel(self, text="Num Items:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_amount = custom_components.AmountEntry(self, callback=self._item_selector_callback, bg_color=config.get_background_color())
        self._item_amount_row = self._cur_row
        self._cur_row += 1

        self._item_cost_label = ctk.CTkLabel(self, text="Total Cost:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._item_cost_row = self._cur_row
        self._cur_row += 1

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
        self._item_type_label.grid(row=self._item_type_row, column=0)
        self._item_type_selector.grid(row=self._item_type_row, column=1)
        self._item_filter_label.grid(row=self._item_filter_row, column=0)
        self._item_filter.grid(row=self._item_filter_row, column=1)
        self._item_selector_label.grid(row=self._item_selector_row, column=0)
        self._item_selector.grid(row=self._item_selector_row, column=1)
        self._item_amount_label.grid(row=self._item_amount_row, column=0)
        self._item_amount.grid(row=self._item_amount_row, column=1)

    def _show_purchase_item(self):
        self._item_type_label.grid(row=self._item_type_row, column=0)
        self._item_type_selector.grid(row=self._item_type_row, column=1)
        self._item_mart_label.grid(row=self._item_mart_row, column=0)
        self._item_mart_selector.grid(row=self._item_mart_row, column=1)
        self._item_filter_label.grid(row=self._item_filter_row, column=0)
        self._item_filter.grid(row=self._item_filter_row, column=1)
        self._item_selector_label.grid(row=self._item_selector_row, column=0)
        self._item_selector.grid(row=self._item_selector_row, column=1)
        self._item_amount_label.grid(row=self._item_amount_row, column=0)
        self._item_amount.grid(row=self._item_amount_row, column=1)
        self._item_cost_label.grid(row=self._item_cost_row, column=0, columnspan=2)
    
    def _show_use_item(self):
        self._item_type_label.grid(row=self._item_type_row, column=0)
        self._item_type_selector.grid(row=self._item_type_row, column=1)
        self._item_filter_label.grid(row=self._item_filter_row, column=0)
        self._item_filter.grid(row=self._item_filter_row, column=1)
        self._item_selector_label.grid(row=self._item_selector_row, column=0)
        self._item_selector.grid(row=self._item_selector_row, column=1)
        self._item_amount_label.grid(row=self._item_amount_row, column=0)
        self._item_amount.grid(row=self._item_amount_row, column=1)

    def _show_sell_item(self):
        self._item_type_label.grid(row=self._item_type_row, column=0)
        self._item_type_selector.grid(row=self._item_type_row, column=1)
        self._item_filter_label.grid(row=self._item_filter_row, column=0)
        self._item_filter.grid(row=self._item_filter_row, column=1)
        self._item_selector_label.grid(row=self._item_selector_row, column=0)
        self._item_selector.grid(row=self._item_selector_row, column=1)
        self._item_amount_label.grid(row=self._item_amount_row, column=0)
        self._item_amount.grid(row=self._item_amount_row, column=1)
        self._item_cost_label.grid(row=self._item_cost_row, column=0, columnspan=2)
    
    def _show_hold_item(self):
        self._item_type_label.grid(row=self._item_type_row, column=0)
        self._item_type_selector.grid(row=self._item_type_row, column=1)
        self._item_filter_label.grid(row=self._item_filter_row, column=0)
        self._item_filter.grid(row=self._item_filter_row, column=1)
        self._item_selector_label.grid(row=self._item_selector_row, column=0)
        self._item_selector.grid(row=self._item_selector_row, column=1)

    def _item_filter_callback(self, *args, **kwargs):
        item_type = self._item_type_selector.get()
        backpack_filter = False
        if item_type == const.ITEM_TYPE_BACKPACK_ITEMS:
            item_type = const.ITEM_TYPE_ALL_ITEMS
            backpack_filter = True
        
        new_vals = pkmn.current_gen_info().item_db().get_filtered_names(
            item_type=item_type,
            source_mart=self._item_mart_selector.get()
        )

        if backpack_filter:
            backpack_items = [x.base_item.name for x in self.editor_params.cur_state.inventory.cur_items]
            new_vals = [x for x in new_vals if x in backpack_items]
        
        item_filter_val = self._item_filter.get().strip().lower()
        if item_filter_val:
            new_vals = [x for x in new_vals if item_filter_val in x.lower()]
        
        if not new_vals:
            new_vals = [const.NO_ITEM]

        self._item_selector.new_values(new_vals)

    def _item_selector_callback(self, *args, **kwargs):
        try:
            # first, get the amount the user wants. We always do this to make sure it's actually an int
            # even if we aren't calcing the cost here, it has to be a valid number
            item_amt = int(self._item_amount.get())
            cur_item = pkmn.current_gen_info().item_db().get_item(self._item_selector.get())
            if self.editor_params.event_type == const.TASK_PURCHASE_ITEM:
                # update the cost if purchasing
                cost = cur_item.purchase_price
                cost *= item_amt
                self._item_cost_label.configure(text=f"Total Cost: {cost}")
            elif self.editor_params.event_type == const.TASK_SELL_ITEM:
                # update the cost if purchasing
                cost = cur_item.sell_price
                cost *= item_amt
                self._item_cost_label.configure(text=f"Total Profit: {cost}")

            self.event_button.enable()
        except Exception as e:
            self.event_button.disable()
    
    def set_event_type(self, event_type):
        if event_type == const.TASK_GET_FREE_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_acquire_item()
            self.event_button.enable()
            return True

        elif event_type == const.TASK_PURCHASE_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_purchase_item()
            self.event_button.enable()
            return True

        elif event_type == const.TASK_USE_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_use_item()
            self.event_button.enable()
            return True

        elif event_type == const.TASK_SELL_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_sell_item()
            self.event_button.enable()
            return True

        elif event_type == const.TASK_HOLD_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_hold_item()
            self.event_button.enable()
            return True

        return False

    def configure(self, editor_params):
        super().configure(editor_params)
        self._item_filter.set("")
        self._item_mart_selector.set(const.ITEM_TYPE_ALL_ITEMS)
        self._item_type_selector.set(const.ITEM_TYPE_ALL_ITEMS)
        self._item_amount.set("1")
        self.set_event_type(self.editor_params.event_type)

    def load_event(self, event_def):
        super().load_event(event_def)
        self._item_filter.set("")
        self._item_mart_selector.set(const.ITEM_TYPE_ALL_ITEMS)
        self._item_type_selector.set(const.ITEM_TYPE_ALL_ITEMS)
        self.set_event_type(event_def.get_event_type())

        if self.event_type != const.TASK_HOLD_ITEM:
            self._item_selector.set(event_def.item_event_def.item_name)
            self._item_amount.set(event_def.item_event_def.item_amount)
        else:
            self._item_selector.set(event_def.hold_item.item_name)

    def get_event(self):
        if self.event_type == const.TASK_GET_FREE_ITEM:
            return EventDefinition(
                item_event_def=InventoryEventDefinition(
                    self._item_selector.get(),
                    int(self._item_amount.get()),
                    True,
                    False
                )
            )

        elif self.event_type == const.TASK_PURCHASE_ITEM:
            return EventDefinition(
                item_event_def=InventoryEventDefinition(
                    self._item_selector.get(),
                    int(self._item_amount.get()),
                    True,
                    True
                )
            )

        elif self.event_type == const.TASK_USE_ITEM:
            return EventDefinition(
                item_event_def=InventoryEventDefinition(
                    self._item_selector.get(),
                    int(self._item_amount.get()),
                    False,
                    False
                )
            )

        elif self.event_type == const.TASK_SELL_ITEM:
            return EventDefinition(
                item_event_def=InventoryEventDefinition(
                    self._item_selector.get(),
                    int(self._item_amount.get()),
                    False,
                    True
                )
            )
        
        elif self.event_type == const.TASK_HOLD_ITEM:
            return EventDefinition(
                hold_item=HoldItemEventDefinition(self._item_selector.get())
            )
        
        raise ValueError(f"Cannot generate inventory event for event type: {self.editor_params.event_type}")


class SaveEventEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_button.enable()
        self._location_label = ctk.CTkLabel(self, text="Save Location", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._location_value = custom_components.SimpleEntry(self)
        self._location_label.grid(row=self._cur_row, column=0)
        self._location_value.grid(row=self._cur_row, column=1)
        self._cur_row += 1
    
    def load_event(self, event_def):
        super().load_event(event_def)
        self._location_value.set(str(event_def.save.location))

    def get_event(self):
        return EventDefinition(save=SaveEventDefinition(location=self._location_value.get()))


class HealEventEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_button.enable()
        self._location_label = ctk.CTkLabel(self, text="Heal Location", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._location_value = custom_components.SimpleEntry(self)
        self._location_label.grid(row=self._cur_row, column=0)
        self._location_value.grid(row=self._cur_row, column=1)
        self._cur_row += 1
    
    def load_event(self, event_def):
        super().load_event(event_def)
        self._location_value.set(str(event_def.heal.location))

    def get_event(self):
        return EventDefinition(heal=HealEventDefinition(location=self._location_value.get()))


class BlackoutEventEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_button.enable()
        self._location_label = ctk.CTkLabel(self, text="Black Out back to:", bg_color=config.get_background_color(), fg_color=config.get_text_color())
        self._location_value = custom_components.SimpleEntry(self)
        self._location_label.grid(row=self._cur_row, column=0)
        self._location_value.grid(row=self._cur_row, column=1)
        self._cur_row += 1
    
    def load_event(self, event_def):
        super().load_event(event_def)
        self._location_value.set(str(event_def.blackout.location))

    def get_event(self):
        return EventDefinition(blackout=BlackoutEventDefinition(location=self._location_value.get()))


class EventEditorFactory:
    # NOTE: any event type that we want to support must have an entry in this map
    # NOTE: otherwise, you won't be able to get a visual editor for it
    TYPE_MAP = {
        const.TASK_TRAINER_BATTLE: TrainerFightEditor,
        const.TASK_RARE_CANDY: RareCandyEditor,
        const.TASK_VITAMIN: VitaminEditor,
        const.TASK_FIGHT_WILD_PKMN: WildPkmnEditor,
        const.TASK_GET_FREE_ITEM: InventoryEventEditor,
        const.TASK_PURCHASE_ITEM: InventoryEventEditor,
        const.TASK_USE_ITEM: InventoryEventEditor,
        const.TASK_SELL_ITEM: InventoryEventEditor,
        const.TASK_HOLD_ITEM: InventoryEventEditor,
        const.TASK_LEARN_MOVE_LEVELUP: LearnMoveEditor,
        const.TASK_LEARN_MOVE_TM: LearnMoveEditor,
        const.TASK_SAVE: SaveEventEditor,
        const.TASK_HEAL: HealEventEditor,
        const.TASK_BLACKOUT: BlackoutEventEditor,
        const.TASK_NOTES_ONLY: NotesEditor,
    }

    def __init__(self, tk_container, event_button):
        self._lookup = {}
        self._tk_container = tk_container
        self._event_button = event_button

    def get_editor(self, editor_params:EditorParams) -> EventEditorBase:
        if editor_params.event_type in self._lookup:
            result = self._lookup[editor_params.event_type]
            result.configure(editor_params)
            return result

        editor_type = self.TYPE_MAP.get(editor_params.event_type)
        if editor_type is None:
            raise ValueError(f"Could not find visual editor for event type: {editor_params.event_type}")

        result = editor_type(self._tk_container, self._event_button, editor_params)
        result.configure(editor_params)
        self._lookup[editor_params.event_type] = result

        # dumb hack, but wtv. Use the same editor for all item events
        if editor_params.event_type in const.ITEM_ROUTE_EVENT_TYPES:
            for other_event_type in const.ITEM_ROUTE_EVENT_TYPES:
                self._lookup[other_event_type] = result
        
        return result

