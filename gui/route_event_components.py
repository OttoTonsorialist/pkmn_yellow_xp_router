from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import logging
from typing import List

from gui import custom_components
from gui.pkmn_components import EnemyPkmnTeam, PkmnViewer
from utils.constants import const
from pkmn.gen_factory import current_gen_info
from pkmn import universal_data_objects
from routing.route_events import BlackoutEventDefinition, EventDefinition, HealEventDefinition, HoldItemEventDefinition, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, SaveEventDefinition, TrainerEventDefinition, VitaminEventDefinition, WildPkmnEventDefinition
from routing import full_route_state

logger = logging.getLogger(__name__)


def ignore_updates(load_fn):
    # must wrap an instance method from the EventEditorBase class
    def wrapper(*args, **kwargs):
        editor:EventEditorBase = args[0]
        editor._ignoring_updates = True
        try:
            load_fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Trying to run function: {load_fn}, got error: {e}")
            logger.exception(e)
            raise e
        finally:
            editor._ignoring_updates = False
    
    return wrapper


class EditorParams:
    def __init__(self, event_type, cur_defeated_trainers, cur_state):
        self.event_type = event_type
        self.cur_defeated_trainers = cur_defeated_trainers
        self.cur_state = cur_state


class EventEditorBase(ttk.Frame):
    def __init__(self, parent, editor_params: EditorParams, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.editor_params = editor_params
        self._save_callback = None
        self._ignoring_updates = False

        self._cur_row = 0
    
    def configure(self, editor_params, save_callback=None):
        self._save_callback = save_callback
        self.editor_params = editor_params
    
    def _trigger_save(self, *args, **kwargs):
        if self._ignoring_updates:
            return

        if self._save_callback is not None:
            self._save_callback()
    
    def enable(self):
        pass

    def disable(self):
        pass
    
    def load_event(self, event_def:EventDefinition):
        pass

    def get_event(self) -> EventDefinition:
        return None


class NotesEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._notes_label = ttk.Label(self, text="Notes:")
        self._notes_label.grid(row=self._cur_row, column=0, sticky=tk.W, padx=5, pady=5)
        self._stat_label = ttk.Label(self, text="Stats with * are calculated with a badge boost", style="Contrast.TLabel")
        self._stat_label.grid(row=self._cur_row, column=1, sticky=tk.W, padx=5, pady=5)
        self._padding_label = ttk.Label(self, text="")
        self._padding_label.grid(row=self._cur_row, column=2, sticky=tk.W, padx=5, pady=5)
        self._cur_row += 1

        self._notes = custom_components.SimpleText(self, height=8)
        self._notes.bind("<<TextModified>>", self._trigger_save)
        self._notes.grid(row=self._cur_row, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self._cur_row += 1

        self.columnconfigure(0, weight=1, uniform="padding")
        self.columnconfigure(2, weight=1, uniform="padding")
    
    @ignore_updates
    def configure(self, editor_params, save_callback=None):
        super().configure(editor_params, save_callback=save_callback)
    
    @ignore_updates
    def load_event(self, event_def:EventDefinition):
        self._notes.delete(1.0, tk.END)
        if event_def is not None:
            self._notes.insert(1.0, event_def.notes)

    def get_event(self) -> EventDefinition:
        return EventDefinition(notes=self._notes.get(1.0, tk.END).strip())
    
    def enable(self):
        self._notes.enable()
    
    def disable(self):
        self._notes.disable()


class TrainerFightEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # just holding onto the name for convenience
        self._cur_trainer = None
        self._num_pkmn = 0
        self._all_pkmn = [PkmnViewer(self, font_size=10) for _ in range(6)]
        self._all_exp_labels = [ttk.Label(self, text="Exp Split:") for _ in range(6)]
        self._all_exp_splits = [
            custom_components.SimpleOptionMenu(self, option_list=[1, 2, 3, 4, 5, 6], callback=self._trigger_save) for _ in range(6)
        ]

    @ignore_updates
    def configure(self, editor_params, save_callback=None):
        super().configure(editor_params, save_callback=save_callback)
    
    @ignore_updates
    def load_event(self, event_def):
        self._cur_trainer = event_def.trainer_def.trainer_name
        enemy_pkmn = event_def.get_pokemon_list()
        self._num_pkmn = len(enemy_pkmn)
        cur_state:full_route_state.RouteState = self.editor_params.cur_state

        idx = -1
        for idx, cur_pkmn in enumerate(enemy_pkmn):
            if cur_state is not None:
                if cur_state.solo_pkmn.cur_stats.speed > cur_pkmn.cur_stats.speed:
                    speed_style = "Success"
                elif cur_state.solo_pkmn.cur_stats.speed == cur_pkmn.cur_stats.speed:
                    speed_style = "Warning"
                else:
                    speed_style = "Failure"
                cur_state = cur_state.defeat_pkmn(cur_pkmn)[0]
            else:
                speed_style = "Contrast"

            row_idx = 2 * (idx // 3)
            col_idx = 2 * (idx % 3)

            self._all_pkmn[idx].set_pkmn(cur_pkmn, speed_style=speed_style)
            self._all_pkmn[idx].grid(row=row_idx, column=col_idx, columnspan=2, padx=5, pady=5)
            self._all_exp_labels[idx].grid(row=row_idx + 1, column=col_idx, padx=2, pady=(5, 10))
            self._all_exp_splits[idx].grid(row=row_idx + 1, column=col_idx + 1, padx=2, pady=(5, 10))
        
        for missing_idx in range(idx+1, 6):
            self._all_pkmn[missing_idx].grid_forget()
            self._all_exp_labels[missing_idx].grid_forget()
            self._all_exp_splits[missing_idx].grid_forget()
    
    def get_event(self):
        exp_split = [int(self._all_exp_splits[x].get()) for x in range(self._num_pkmn)]
        return EventDefinition(trainer_def=TrainerEventDefinition(self._cur_trainer, exp_split=exp_split))
    
    def enable(self):
        for cur_split in self._all_exp_splits:
            cur_split.enable()
    
    def disable(self):
        for cur_split in self._all_exp_splits:
            cur_split.disable()


class VitaminEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._vitamin_label = ttk.Label(self, text="Vitamin Type:")
        self._vitamin_types = custom_components.SimpleOptionMenu(self, const.VITAMIN_TYPES, callback=self._trigger_save)
        self._vitamin_label.grid(row=self._cur_row, column=0, pady=2)
        self._vitamin_types.grid(row=self._cur_row, column=1, pady=2)
        self._cur_row += 1

        self._item_amount_label = ttk.Label(self, text="Num Vitamins:")
        self._item_amount = custom_components.AmountEntry(self, min_val=1, callback=self._amount_update, width=5)
        self._item_amount_label.grid(row=self._cur_row, column=0, pady=2)
        self._item_amount.grid(row=self._cur_row, column=1, pady=2)
        self._cur_row += 1

    def _amount_update(self, *args, **kwargs):
        val = self._item_amount.get()
        try:
            if int(val) > 0:
                self._trigger_save()
        except Exception as e:
            pass
    
    @ignore_updates
    def load_event(self, event_def):
        self._vitamin_types.set(event_def.vitamin.vitamin)
        self._item_amount.set(str(event_def.vitamin.amount))

    def get_event(self):
        return EventDefinition(vitamin=VitaminEventDefinition(self._vitamin_types.get(), int(self._item_amount.get())))
    
    def enable(self):
        self._vitamin_types.enable()
        self._item_amount.enable()
    
    def disable(self):
        self._vitamin_types.disable()
        self._item_amount.disable()


class RareCandyEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._item_amount_label = ttk.Label(self, text="Num Rare Candies:")
        self._item_amount = custom_components.AmountEntry(self, min_val=1, callback=self._amount_update, width=5)
        self._item_amount_label.grid(row=self._cur_row, column=0)
        self._item_amount.grid(row=self._cur_row, column=1)
        self._cur_row += 1
    
    def _amount_update(self, *args, **kwargs):
        val = self._item_amount.get()
        try:
            if int(val) > 0:
                self._trigger_save()
        except Exception as e:
            pass
    
    @ignore_updates
    def load_event(self, event_def):
        self._item_amount.set(str(event_def.rare_candy.amount))

    def get_event(self):
        return EventDefinition(rare_candy=RareCandyEventDefinition(int(self._item_amount.get())))
    
    def enable(self):
        self._item_amount.enable()
    
    def disable(self):
        self._item_amount.disable()


class LearnMoveEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        val_width = 25

        self._source_label = ttk.Label(self)
        self._source_label.grid(row=self._cur_row, column=0, columnspan=2, pady=2)
        self._cur_row += 1

        self._move_name_label = ttk.Label(self)
        self._move_name_label.grid(row=self._cur_row, column=0, columnspan=2, pady=2)
        self._cur_row += 1

        self._destination_label = ttk.Label(self, text="Move Destination:")
        self._destination = custom_components.SimpleOptionMenu(self, [""], width=val_width, callback=self._trigger_save)
        self._destination_label.grid(row=self._cur_row, column=0, pady=2)
        self._destination.grid(row=self._cur_row, column=1, pady=2)
        self._cur_row += 1

        # Not a visual component, but we want a way to be able to pull the current move being referenced
        self._move = None
        self._level = const.LEVEL_ANY

        self._item_type_label = ttk.Label(self, text="Item Type:")
        self._item_type_selector = custom_components.SimpleOptionMenu(self, [const.ITEM_TYPE_ALL_ITEMS, const.ITEM_TYPE_BACKPACK_ITEMS, const.ITEM_TYPE_TM], callback=self._item_filter_callback, width=val_width)
        self._item_type_row = self._cur_row
        self._cur_row += 1

        self._item_filter_label = ttk.Label(self, text="Item Name Filter:")
        self._item_filter = custom_components.SimpleEntry(self, callback=self._item_filter_callback, width=val_width)
        self._item_filter_row = self._cur_row
        self._cur_row += 1

        self._item_selector_label = ttk.Label(self, text="Move:")
        self._item_selector = custom_components.SimpleOptionMenu(self, [""], callback=self._move_selected_callback, width=val_width)
        self._item_selector_row = self._cur_row
        self._cur_row += 1

    def _item_filter_callback(self, *args, **kwargs):
        item_type = self._item_type_selector.get()
        backpack_filter = False
        if item_type == const.ITEM_TYPE_BACKPACK_ITEMS:
            item_type = const.ITEM_TYPE_TM
            backpack_filter = True
        
        new_vals = current_gen_info().item_db().get_filtered_names(item_type=item_type)

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
            item_obj = current_gen_info().item_db().get_item(self._item_selector.get())
            if item_obj is not None:
                self._move = item_obj.move_name
            else:
                self._move = None
            self._move_name_label.config(text=f"Move: {self._move}")
        
        if self._move is None:
            return
        
        learn_move_info = self.editor_params.cur_state.solo_pkmn.get_move_destination(self._move, None)
        if not learn_move_info[1]:
            if learn_move_info[0] is None:
                self._destination.set(const.MOVE_DONT_LEARN)
            else:
                self._destination.set(const.MOVE_SLOT_TEMPLATE.format(learn_move_info[0] + 1, None))
            self._destination.disable()
        else:
            self._destination.enable()

        self._trigger_save()

    @ignore_updates
    def configure(self, editor_params, save_callback=None):
        super().configure(editor_params, save_callback=save_callback)
        self._destination.new_values(
            [const.MOVE_DONT_LEARN] +
            [
                const.MOVE_SLOT_TEMPLATE.format(idx + 1, x) for idx, x in
                enumerate(self.editor_params.cur_state.solo_pkmn.move_list)
            ]
        )
        if self.editor_params.event_type == const.TASK_LEARN_MOVE_LEVELUP:
            self._source_label.config(text="Source: Levelup")
            self._item_type_label.grid_forget()
            self._item_type_selector.grid_forget()
            self._item_filter_label.grid_forget()
            self._item_filter.grid_forget()
            self._item_selector_label.grid_forget()
            self._item_selector.grid_forget()
        else:
            self._source_label.config(text="Source: TM/HM")
            self._item_type_label.grid(row=self._item_type_row, column=0, pady=2)
            self._item_type_selector.grid(row=self._item_type_row, column=1, pady=2)
            self._item_filter_label.grid(row=self._item_filter_row, column=1, pady=2)
            self._item_filter.grid(row=self._item_filter_row, column=1, pady=2)
            self._item_selector_label.grid(row=self._item_selector_row, column=0, pady=2)
            self._item_selector.grid(row=self._item_selector_row, column=1, pady=2)

        self._item_filter_callback()

    @ignore_updates
    def load_event(self, event_def):
        if self.editor_params.event_type == const.TASK_LEARN_MOVE_LEVELUP:
            self._move = event_def.learn_move.move_to_learn
            self._move_name_label.config(text=f"Move: {self._move}")
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
    
    def enable(self):
        self._item_type_selector.enable()
        self._item_filter.enable()
        self._item_selector.enable()

        # deliberately always set this to enabled first
        self._destination.enable()
        # looks weird, but use the decorator to call the move selected callback without saving
        # this will trigger the logic to update the destination status properly
        ignore_updates(self._move_selected_callback)(self)
    
    def disable(self):
        self._item_type_selector.disable()
        self._item_filter.disable()
        self._item_selector.disable()
        self._destination.disable()
    

class WildPkmnEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pkmn_label = ttk.Label(self, text="Wild Pokemon Type:")
        self._pkmn_types = custom_components.SimpleOptionMenu(self, current_gen_info().pkmn_db().get_all_names(), width=15, callback=self._trigger_save)
        self._pkmn_label.grid(row=self._cur_row, column=0, pady=2)
        self._pkmn_types.grid(row=self._cur_row, column=1, pady=2)
        self._cur_row += 1

        self._pkmn_filter_label = ttk.Label(self, text="Wild Pokemon Type Filter:")
        self._pkmn_filter = custom_components.SimpleEntry(self, callback=self._pkmn_filter_callback, width=15)
        self._pkmn_filter_label.grid(row=self._cur_row, column=0, pady=2)
        self._pkmn_filter.grid(row=self._cur_row, column=1, pady=2)
        self._cur_row += 1

        self._pkmn_level_label = ttk.Label(self, text="Wild Pokemon Level:")
        self._pkmn_level = custom_components.AmountEntry(self, min_val=2, max_val=100, callback=self._update_button_status, width=5)
        self._pkmn_level_label.grid(row=self._cur_row, column=0, pady=2)
        self._pkmn_level.grid(row=self._cur_row, column=1, pady=2)
        self._cur_row += 1

        self._quantity_label = ttk.Label(self, text="Num Pkmn:")
        self._quantity = custom_components.AmountEntry(self, min_val=1, callback=self._update_button_status, width=5)
        self._quantity_label.grid(row=self._cur_row, column=0, pady=2)
        self._quantity.grid(row=self._cur_row, column=1, pady=2)
        self._cur_row += 1

        self._pkmn_trainer_flag = custom_components.CheckboxLabel(self, text="Is Trainer Pkmn?", flip=True, toggle_command=self._trigger_save)
        self._pkmn_trainer_flag.grid(row=self._cur_row, column=0, columnspan=2, pady=2)
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
            self._trigger_save()

    def _pkmn_filter_callback(self, *args, **kwargs):
        self._pkmn_types.new_values(current_gen_info().pkmn_db().get_filtered_names(filter_val=self._pkmn_filter.get().strip()))
        self._update_button_status()

    @ignore_updates
    def configure(self, editor_params, save_callback=None):
        super().configure(editor_params, save_callback=save_callback)
        self._pkmn_filter.set("")
        self._pkmn_level.set("1")
        self._quantity.set("1")
        self._pkmn_trainer_flag.set_checked(False)
    
    @ignore_updates
    def load_event(self, event_def):
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
    
    def enable(self):
        self._pkmn_types.enable()
        self._pkmn_filter.enable()
        self._pkmn_level.enable()
        self._quantity.enable()
        self._pkmn_trainer_flag.enable()
    
    def disable(self):
        self._pkmn_types.disable()
        self._pkmn_filter.disable()
        self._pkmn_level.disable()
        self._quantity.disable()
        self._pkmn_trainer_flag.disable()


class InventoryEventEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        val_width = 23
        self._item_type_label = ttk.Label(self, text="Item Type:")
        self._item_type_selector = custom_components.SimpleOptionMenu(self, const.ITEM_TYPES, callback=self._item_filter_callback, width=val_width)
        self._item_type_row = self._cur_row
        self._cur_row += 1

        self._item_mart_label = ttk.Label(self, text="Mart:")
        self._item_mart_selector = custom_components.SimpleOptionMenu(
            self,
            [const.ITEM_TYPE_ALL_ITEMS] + sorted(list(current_gen_info().item_db().mart_items.keys())),
            callback=self._item_filter_callback,
            width=val_width
        )
        self._item_mart_row = self._cur_row
        self._cur_row += 1

        self._item_filter_label = ttk.Label(self, text="Item Name Filter:")
        self._item_filter = custom_components.SimpleEntry(self, callback=self._item_filter_callback, width=val_width)
        self._item_filter_row = self._cur_row
        self._cur_row += 1

        self._item_selector_label = ttk.Label(self, text="Item:")
        self._item_selector = custom_components.SimpleOptionMenu(self, current_gen_info().item_db().get_filtered_names(), callback=self._item_selector_callback, width=val_width)
        self._item_selector_row = self._cur_row
        self._cur_row += 1

        self._item_amount_label = ttk.Label(self, text="Num Items:")
        self._item_amount = custom_components.AmountEntry(self, min_val=1, callback=self._item_selector_callback, width=5)
        self._item_amount_row = self._cur_row
        self._cur_row += 1

        self._item_cost_label = ttk.Label(self, text="Total Cost:")
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
        self._item_type_label.grid(row=self._item_type_row, column=0, pady=2)
        self._item_type_selector.grid(row=self._item_type_row, column=1, pady=2)
        self._item_filter_label.grid(row=self._item_filter_row, column=0, pady=2)
        self._item_filter.grid(row=self._item_filter_row, column=1, pady=2)
        self._item_selector_label.grid(row=self._item_selector_row, column=0, pady=2)
        self._item_selector.grid(row=self._item_selector_row, column=1, pady=2)
        self._item_amount_label.grid(row=self._item_amount_row, column=0, pady=2)
        self._item_amount.grid(row=self._item_amount_row, column=1, pady=2)

    def _show_purchase_item(self):
        self._item_type_label.grid(row=self._item_type_row, column=0, pady=2)
        self._item_type_selector.grid(row=self._item_type_row, column=1, pady=2)
        self._item_mart_label.grid(row=self._item_mart_row, column=0, pady=2)
        self._item_mart_selector.grid(row=self._item_mart_row, column=1, pady=2)
        self._item_filter_label.grid(row=self._item_filter_row, column=0, pady=2)
        self._item_filter.grid(row=self._item_filter_row, column=1, pady=2)
        self._item_selector_label.grid(row=self._item_selector_row, column=0, pady=2)
        self._item_selector.grid(row=self._item_selector_row, column=1, pady=2)
        self._item_amount_label.grid(row=self._item_amount_row, column=0, pady=2)
        self._item_amount.grid(row=self._item_amount_row, column=1, pady=2)
        self._item_cost_label.grid(row=self._item_cost_row, column=0, columnspan=2, pady=2)
    
    def _show_use_item(self):
        self._item_type_label.grid(row=self._item_type_row, column=0, pady=2)
        self._item_type_selector.grid(row=self._item_type_row, column=1, pady=2)
        self._item_filter_label.grid(row=self._item_filter_row, column=0, pady=2)
        self._item_filter.grid(row=self._item_filter_row, column=1, pady=2)
        self._item_selector_label.grid(row=self._item_selector_row, column=0, pady=2)
        self._item_selector.grid(row=self._item_selector_row, column=1, pady=2)
        self._item_amount_label.grid(row=self._item_amount_row, column=0, pady=2)
        self._item_amount.grid(row=self._item_amount_row, column=1, pady=2)

    def _show_sell_item(self):
        self._item_type_label.grid(row=self._item_type_row, column=0, pady=2)
        self._item_type_selector.grid(row=self._item_type_row, column=1, pady=2)
        self._item_filter_label.grid(row=self._item_filter_row, column=0, pady=2)
        self._item_filter.grid(row=self._item_filter_row, column=1, pady=2)
        self._item_selector_label.grid(row=self._item_selector_row, column=0, pady=2)
        self._item_selector.grid(row=self._item_selector_row, column=1, pady=2)
        self._item_amount_label.grid(row=self._item_amount_row, column=0, pady=2)
        self._item_amount.grid(row=self._item_amount_row, column=1, pady=2)
        self._item_cost_label.grid(row=self._item_cost_row, column=0, columnspan=2, pady=2)
    
    def _show_hold_item(self):
        self._item_type_label.grid(row=self._item_type_row, column=0, pady=2)
        self._item_type_selector.grid(row=self._item_type_row, column=1, pady=2)
        self._item_filter_label.grid(row=self._item_filter_row, column=0, pady=2)
        self._item_filter.grid(row=self._item_filter_row, column=1, pady=2)
        self._item_selector_label.grid(row=self._item_selector_row, column=0, pady=2)
        self._item_selector.grid(row=self._item_selector_row, column=1, pady=2)

    def _item_filter_callback(self, *args, **kwargs):
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
            cur_item = current_gen_info().item_db().get_item(self._item_selector.get())
            if self.editor_params.event_type == const.TASK_PURCHASE_ITEM:
                # update the cost if purchasing
                cost = cur_item.purchase_price
                cost *= item_amt
                self._item_cost_label.config(text=f"Total Cost: {cost}")
            elif self.editor_params.event_type == const.TASK_SELL_ITEM:
                # update the cost if purchasing
                cost = cur_item.sell_price
                cost *= item_amt
                self._item_cost_label.config(text=f"Total Profit: {cost}")

            self._trigger_save()
        except Exception as e:
            pass
    
    def set_event_type(self, event_type):
        if event_type == const.TASK_GET_FREE_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_acquire_item()
            return True

        elif event_type == const.TASK_PURCHASE_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_purchase_item()
            return True

        elif event_type == const.TASK_USE_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_use_item()
            return True

        elif event_type == const.TASK_SELL_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_sell_item()
            return True

        elif event_type == const.TASK_HOLD_ITEM:
            self.event_type = event_type
            self._hide_all_item_obj()
            self._show_hold_item()
            return True

        return False

    @ignore_updates
    def configure(self, editor_params, save_callback=None):
        super().configure(editor_params, save_callback=save_callback)
        self._item_filter.set("")
        self._item_mart_selector.set(const.ITEM_TYPE_ALL_ITEMS)
        self._item_type_selector.set(const.ITEM_TYPE_ALL_ITEMS)
        self._item_amount.set("1")
        self.set_event_type(self.editor_params.event_type)

    @ignore_updates
    def load_event(self, event_def):
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
    
    def enable(self):
        self._item_type_selector.enable()
        self._item_mart_selector.enable()
        self._item_filter.enable()
        self._item_selector.enable()
        self._item_amount.enable()
    
    def disable(self):
        self._item_type_selector.disable()
        self._item_mart_selector.disable()
        self._item_filter.disable()
        self._item_selector.disable()
        self._item_amount.disable()


class SaveEventEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._location_label = ttk.Label(self, text="Save Location")
        self._location_value = custom_components.SimpleEntry(self, callback=self._trigger_save, width=20)
        self._location_label.grid(row=self._cur_row, column=0)
        self._location_value.grid(row=self._cur_row, column=1)
        self._cur_row += 1
    
    @ignore_updates
    def load_event(self, event_def):
        self._location_value.set(str(event_def.save.location))

    def get_event(self):
        return EventDefinition(save=SaveEventDefinition(location=self._location_value.get()))
    
    def enable(self):
        self._location_value.enable()

    def disable(self):
        self._location_value.disable()


class HealEventEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._location_label = ttk.Label(self, text="Heal Location")
        self._location_value = custom_components.SimpleEntry(self, callback=self._trigger_save, width=20)
        self._location_label.grid(row=self._cur_row, column=0)
        self._location_value.grid(row=self._cur_row, column=1)
        self._cur_row += 1
    
    @ignore_updates
    def load_event(self, event_def):
        self._location_value.set(str(event_def.heal.location))

    def get_event(self):
        return EventDefinition(heal=HealEventDefinition(location=self._location_value.get()))
    
    def enable(self):
        self._location_value.enable()

    def disable(self):
        self._location_value.disable()


class BlackoutEventEditor(EventEditorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._location_label = ttk.Label(self, text="Black Out back to:")
        self._location_value = custom_components.SimpleEntry(self, callback=self._trigger_save, width=20)
        self._location_label.grid(row=self._cur_row, column=0)
        self._location_value.grid(row=self._cur_row, column=1)
        self._cur_row += 1
    
    @ignore_updates
    def load_event(self, event_def):
        self._location_value.set(str(event_def.blackout.location))

    def get_event(self):
        return EventDefinition(blackout=BlackoutEventDefinition(location=self._location_value.get()))
    
    def enable(self):
        self._location_value.enable()

    def disable(self):
        self._location_value.disable()


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

    def __init__(self, tk_container):
        self._lookup = {}
        self._tk_container = tk_container

    def get_editor(self, editor_params:EditorParams, save_callback=None, is_enabled=True) -> EventEditorBase:
        if editor_params.event_type in self._lookup:
            result:EventEditorBase = self._lookup[editor_params.event_type]
            result.configure(editor_params, save_callback=save_callback)
            if is_enabled:
                result.enable()
            else:
                result.disable()

            return result

        editor_type = self.TYPE_MAP.get(editor_params.event_type)
        if editor_type is None:
            raise ValueError(f"Could not find visual editor for event type: {editor_params.event_type}")

        result = editor_type(self._tk_container, editor_params)
        result.configure(editor_params, save_callback=save_callback)
        self._lookup[editor_params.event_type] = result

        # dumb hack, but wtv. Use the same editor for all item events
        if editor_params.event_type in const.ITEM_ROUTE_EVENT_TYPES:
            for other_event_type in const.ITEM_ROUTE_EVENT_TYPES:
                self._lookup[other_event_type] = result
        
        return result

