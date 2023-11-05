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
        self._delayed_save_callback = None
        self._ignoring_updates = False

        self._cur_row = 0
    
    def configure(self, editor_params, save_callback=None, delayed_save_callback=None):
        self._save_callback = save_callback
        self._delayed_save_callback = delayed_save_callback
        self.editor_params = editor_params
    
    def _trigger_save(self, *args, **kwargs):
        if self._ignoring_updates:
            return

        if self._save_callback is not None:
            self._save_callback()
    
    def _trigger_delayed_save(self, *args, **kwargs):
        if self._ignoring_updates:
            return

        if self._delayed_save_callback is not None:
            self._delayed_save_callback()
    
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
        self._notes.bind("<<TextModified>>", self._trigger_delayed_save)
        self._notes.grid(row=self._cur_row, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self._cur_row += 1

        self.columnconfigure(0, weight=1, uniform="padding")
        self.columnconfigure(2, weight=1, uniform="padding")
    
    @ignore_updates
    def configure(self, editor_params, save_callback=None, delayed_save_callback=None):
        super().configure(editor_params, save_callback=save_callback, delayed_save_callback=delayed_save_callback)
    
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
    VAR_COUNTER = 0
    EXP_PER_SEC_TEXT = "Optimal exp per second (4x speed): "
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # just holding onto the name for convenience
        self._cur_trainer = None
        self._num_pkmn = 0
        self._header_frame = ttk.Frame(self)
        self._header_frame.pack(fill=tk.X)
        self._exp_per_sec_label = ttk.Label(self._header_frame, text=self.EXP_PER_SEC_TEXT)
        self._exp_per_sec_label.grid(column=4, row=0)
        self._pay_day_label = ttk.Label(self._header_frame, text="Pay Day Amount: ")
        self._pay_day_label.grid(column=1, row=0)
        self._pay_day_value = custom_components.SimpleEntry(self._header_frame, callback=self._trigger_save, width=8)
        self._pay_day_value.grid(column=2, row=0)
        self._header_frame.columnconfigure(0, weight=1, uniform="group")
        self._header_frame.columnconfigure(3, weight=1, uniform="group")
        self._header_frame.columnconfigure(5, weight=1, uniform="group")

        self._info_frame = ttk.Frame(self)
        self._info_frame.pack(fill=tk.BOTH)
        self._info_frame.columnconfigure(0, weight=1, uniform="group")
        self._info_frame.columnconfigure(13, weight=1, uniform="group")
        self._info_frame.rowconfigure(0, weight=1, uniform="group")
        self._info_frame.rowconfigure(5, weight=1, uniform="group")
        self._all_pkmn = [PkmnViewer(self._info_frame, font_size=10) for _ in range(6)]
        self._cached_definition_order = []
        self._all_exp_labels = [ttk.Label(self._info_frame, text="Exp Split:") for _ in range(6)]
        self._all_exp_splits = [
            custom_components.SimpleOptionMenu(self._info_frame, option_list=[1, 2, 3, 4, 5, 6], callback=self._trigger_save, width=5) for _ in range(6)
        ]
        self._all_order_labels = [ttk.Label(self._info_frame, text="Mon Order") for _ in range(6)]
        self._all_order_menus = [
            custom_components.SimpleOptionMenu(
                self._info_frame,
                option_list=[1, 2, 3, 4, 5, 6],
                callback=self._reorder_mons,
                var_name=f"TRAINER_MON_{self.VAR_COUNTER}_{idx}",
                width=5
            ) for idx in range(6)
        ]
        self._order_menu_lookup = {x._val._name: x for x in self._all_order_menus}
        self.VAR_COUNTER += 1

    @ignore_updates
    def configure(self, editor_params, save_callback=None, delayed_save_callback=None):
        super().configure(editor_params, save_callback=save_callback, delayed_save_callback=delayed_save_callback)
    
    @ignore_updates
    def load_event(self, event_def):
        self._cur_trainer = event_def.trainer_def.trainer_name
        try:
            pay_day_val = int(event_def.trainer_def.pay_day_amount)
        except Exception:
            pay_day_val = 0

        self._exp_per_sec_label.configure(text=f"{self.EXP_PER_SEC_TEXT} {event_def.experience_per_second()}")
        self._pay_day_value.set(pay_day_val)
        enemy_pkmn_ordered = event_def.get_pokemon_list()
        self._num_pkmn = len(enemy_pkmn_ordered)
        order_values = list(range(1, len(enemy_pkmn_ordered) + 1))

        self._cached_definition_order = [x.mon_order - 1 for x in event_def.get_pokemon_list(definition_order=True)]

        cur_state:full_route_state.RouteState = self.editor_params.cur_state
        idx = -1
        for idx, cur_pkmn in enumerate(enemy_pkmn_ordered):
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

            row_idx = (2 * (idx // 3)) + 1
            col_idx = 4 * (idx % 3) + 1

            self._all_pkmn[idx].set_pkmn(cur_pkmn, speed_style=speed_style)
            self._all_pkmn[idx].grid(row=row_idx, column=col_idx, columnspan=4, padx=5, pady=5)

            self._all_order_labels[idx].grid(row=row_idx + 1, column=col_idx, padx=2, pady=(5, 10))
            self._all_order_menus[idx].new_values(order_values)
            self._all_order_menus[idx].set(cur_pkmn.mon_order)
            self._all_order_menus[idx].grid(row=row_idx + 1, column=col_idx + 1, padx=2, pady=(5, 10))

            self._all_exp_labels[idx].grid(row=row_idx + 1, column=col_idx + 2, padx=2, pady=(5, 10))
            self._all_exp_splits[idx].set(cur_pkmn.exp_split)
            self._all_exp_splits[idx].grid(row=row_idx + 1, column=col_idx + 3, padx=2, pady=(5, 10))

        
        for missing_idx in range(idx+1, 6):
            self._all_pkmn[missing_idx].grid_forget()
            self._all_exp_labels[missing_idx].grid_forget()
            self._all_exp_splits[missing_idx].grid_forget()
            self._all_order_labels[missing_idx].grid_forget()
            self._all_order_menus[missing_idx].grid_forget()
            self._all_order_menus[missing_idx].set(-1)
    
    def _reorder_mons(self, updated_name, _, cmd):
        if self._ignoring_updates:
            return

        self._ignoring_updates = True
        try:
            # the use case for this is that we have one value, changed by the user
            # every other value is presumed to already be in order
            # so we should have something like this

            # user adjusted val 4 => 2
            # other vals: 1, 2, 3, 5, 6

            # so we have two goals. Push every mon after the new target val up
            # but also push every mon after the original val down
            # the easiest way to solve this is to acknowledge that the list is already sorted, except for the new value
            # so we extract the original ordering of the list (sans the user adjusted val)
            # then we blindly reassign the new ordered val, while skipping over the adjusted val (as it it already correct)

            # collect every other dropdown menu, in order based on the current ordering
            # remember that all the ordering values are 1-based
            ordered_elements = []
            names_ordered = []
            found_elements = {updated_name}
            while len(found_elements) < self._num_pkmn:
                cur_min = self._num_pkmn + 1
                min_el = None
                for cur_name, cur_menu in self._order_menu_lookup.items():
                    if cur_name in found_elements:
                        continue
                    test_val = int(cur_menu.get())
                    if test_val == -1:
                        continue
                    if test_val < cur_min:
                        min_el = cur_name
                        cur_min = test_val
            
                ordered_elements.append(self._order_menu_lookup[min_el])
                names_ordered.append(min_el)
                found_elements.add(min_el)

            # figure out the value that the user changed to
            adjusted_val = int(self._order_menu_lookup[updated_name].get())

            # now that we have every drop down in order, reset every value, starting from 1
            new_order_idx = 1
            while new_order_idx < (self._num_pkmn + 1):
                if new_order_idx == adjusted_val:
                    new_order_idx += 1
                    continue
                
                ordered_elements.pop(0).set(new_order_idx)
                new_order_idx += 1
            
        finally:
            self._ignoring_updates = False
        
        self._trigger_save()
        self.load_event(self.get_event())
    
    def get_event(self):
        exp_split = [int(self._all_exp_splits[x].get()) for x in self._cached_definition_order]
        mon_order = [int(self._all_order_menus[x].get()) for x in self._cached_definition_order]

        try:
            pay_day_amount = int(self._pay_day_value.get())
        except Exception:
            pay_day_amount = 0
        return EventDefinition(trainer_def=TrainerEventDefinition(self._cur_trainer, exp_split=exp_split, pay_day_amount=pay_day_amount, mon_order=mon_order))
    
    def enable(self):
        self._pay_day_value.enable()
        for cur_split in self._all_exp_splits:
            cur_split.enable()
        for cur_order in self._all_order_menus:
            cur_order.enable()
    
    def disable(self):
        self._pay_day_value.disable()
        for cur_split in self._all_exp_splits:
            cur_split.disable()
        for cur_order in self._all_order_menus:
            cur_order.disable()


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

        self._source_label = ttk.Label(self, text="Move Source")
        self._source = custom_components.SimpleOptionMenu(self, [""], width=val_width, callback=self._move_source_callback)
        self._source_label.grid(row=self._cur_row, column=0, pady=2)
        self._source.grid(row=self._cur_row, column=1, pady=2)
        self._cur_row += 1

        self._item_filter_label = ttk.Label(self, text="Item Name Filter:")
        self._item_filter = custom_components.SimpleEntry(self, callback=self._item_filter_callback, width=val_width)
        self._item_filter_row = self._cur_row
        self._cur_row += 1

        self._item_selector_label = ttk.Label(self, text="Move:")
        self._item_selector = custom_components.SimpleOptionMenu(self, [""], callback=self._move_selected_callback, width=val_width)
        self._item_selector_row = self._cur_row
        self._cur_row += 1

        self._move_filter_label = ttk.Label(self, text="Move Filter:")
        self._move_filter = custom_components.SimpleEntry(self, callback=self._move_filter_callback, width=val_width)
        self._move_filter_row = self._cur_row
        self._cur_row += 1

        self._move_selector_label = ttk.Label(self, text="Move:")
        self._move_selector = custom_components.SimpleOptionMenu(self, [""], callback=self._move_selected_callback, width=val_width)
        self._move_selector_row = self._cur_row
        self._cur_row += 1
    
    def _move_source_callback(self, *args, **kwargs):
        new_source = self._source.get()
        if new_source == const.MOVE_SOURCE_LEVELUP:
            return
        
        if new_source == const.MOVE_SOURCE_TM_HM:
            self._item_filter_label.grid(row=self._item_filter_row, column=0, pady=2)
            self._item_filter.grid(row=self._item_filter_row, column=1, pady=2)
            self._item_selector_label.grid(row=self._item_selector_row, column=0, pady=2)
            self._item_selector.grid(row=self._item_selector_row, column=1, pady=2)
            self._move_filter_label.grid_forget()
            self._move_filter.grid_forget()
            self._move_selector_label.grid_forget()
            self._move_selector.grid_forget()
            self._item_filter_callback()
        else:
            self._item_filter_label.grid_forget()
            self._item_filter.grid_forget()
            self._item_selector_label.grid_forget()
            self._item_selector.grid_forget()
            self._move_filter_label.grid(row=self._move_filter_row, column=0, pady=2)
            self._move_filter.grid(row=self._move_filter_row, column=1, pady=2)
            self._move_selector_label.grid(row=self._move_selector_row, column=0, pady=2)
            self._move_selector.grid(row=self._move_selector_row, column=1, pady=2)
            self._move_filter_callback()
        
        self._trigger_save()

    def _item_filter_callback(self, *args, **kwargs):
        new_vals = current_gen_info().item_db().get_filtered_names(item_type=const.ITEM_TYPE_TM)

        item_filter_val = self._item_filter.get().strip().lower()
        if item_filter_val:
            new_vals = [x for x in new_vals if item_filter_val in x.lower()]
        
        if not new_vals:
            new_vals = [const.NO_ITEM]

        self._item_selector.new_values(new_vals)

    def _move_filter_callback(self, *args, **kwargs):
        self._move_selector.new_values(
            current_gen_info().move_db().get_filtered_names(filter=self._move_filter.get(), include_delete_move=True)
        )
    
    def _move_selected_callback(self, *args, **kwargs):
        if self._source.get() == const.MOVE_SOURCE_TM_HM:
            item_obj = current_gen_info().item_db().get_item(self._item_selector.get())
            if item_obj is not None:
                self._move = item_obj.move_name
            else:
                self._move = None
            self._move_name_label.config(text=f"Move: {self._move}")
        elif self._source.get() == const.MOVE_SOURCE_TUTOR:
            self._move = self._move_selector.get()
            if self._move == const.DELETE_MOVE:
                self._move = None
            self._move_name_label.config(text=f"Move: {self._move}")
        
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
    def configure(self, editor_params, save_callback=None, delayed_save_callback=None):
        super().configure(editor_params, save_callback=save_callback, delayed_save_callback=delayed_save_callback)
        self._destination.new_values(
            [const.MOVE_DONT_LEARN] +
            [
                const.MOVE_SLOT_TEMPLATE.format(idx + 1, x) for idx, x in
                enumerate(self.editor_params.cur_state.solo_pkmn.move_list)
            ]
        )

        self._item_filter_label.grid_forget()
        self._item_filter.grid_forget()
        self._item_selector_label.grid_forget()
        self._item_selector.grid_forget()
        self._move_filter.grid_forget()
        self._move_selector.grid_forget()

        if self.editor_params.event_type == const.TASK_LEARN_MOVE_LEVELUP:
            self._source.new_values([const.MOVE_SOURCE_LEVELUP])
            self._source.disable()
        else:
            self._source.new_values([const.MOVE_SOURCE_TUTOR, const.MOVE_SOURCE_TM_HM])
            self._source.enable()

        self._item_filter_callback()
        self._move_selected_callback()

    @ignore_updates
    def load_event(self, event_def):
        if self.editor_params.event_type == const.TASK_LEARN_MOVE_LEVELUP:
            self._move = event_def.learn_move.move_to_learn
            self._move_name_label.config(text=f"Move: {self._move}")
            self._level = event_def.learn_move.level
        else:
            if event_def.learn_move.source == const.MOVE_SOURCE_TUTOR:
                self._source.set(const.MOVE_SOURCE_TUTOR)
                self._move_filter.set("")
                move = event_def.learn_move.move_to_learn
                if move is None:
                    move = const.DELETE_MOVE
                self._move_selector.set(move)
                self._level = const.LEVEL_ANY
            else:
                self._source.set(const.MOVE_SOURCE_TM_HM)
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
        
        if self.editor_params.event_type == const.TASK_LEARN_MOVE_LEVELUP:
            source = const.MOVE_SOURCE_LEVELUP
        elif self._source.get() == const.MOVE_SOURCE_TUTOR:
            source = const.MOVE_SOURCE_TUTOR
        else:
            source = self._item_selector.get()

        return EventDefinition(learn_move=LearnMoveEventDefinition(self._move, dest, source, level=self._level))
    
    def enable(self):
        self._item_filter.enable()
        self._item_selector.enable()
        self._move_filter.enable()
        self._move_selector.enable()

        # deliberately always set this to enabled first
        self._destination.enable()
        # looks weird, but use the decorator to call the move selected callback without saving
        # this will trigger the logic to update the destination status properly
        ignore_updates(self._move_selected_callback)(self)
    
    def disable(self):
        self._item_filter.disable()
        self._item_selector.disable()
        self._move_filter.disable()
        self._move_selector.disable()
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
    def configure(self, editor_params, save_callback=None, delayed_save_callback=None):
        super().configure(editor_params, save_callback=save_callback, delayed_save_callback=delayed_save_callback)
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
        self._allow_none_item = False

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

        self._consume_held_item = custom_components.CheckboxLabel(self, text="Consume previously held item?", toggle_command=self._trigger_save, width=15, flip=True)
        self._consume_held_item_row = self._cur_row
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
        self._consume_held_item.grid_remove()
    
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
        self._consume_held_item.grid(row=self._consume_held_item_row, column=0, columnspan=2, pady=2)

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
            if self._allow_none_item:
                new_vals = [None]
            else:
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

            if cur_item is None:
                return
            self._trigger_save()
        except Exception as e:
            pass
    
    def set_event_type(self, event_type):
        if event_type == const.TASK_GET_FREE_ITEM:
            self.event_type = event_type
            self._allow_none_item = False
            self._hide_all_item_obj()
            self._show_acquire_item()
            return True

        elif event_type == const.TASK_PURCHASE_ITEM:
            self.event_type = event_type
            self._allow_none_item = False
            self._hide_all_item_obj()
            self._show_purchase_item()
            return True

        elif event_type == const.TASK_USE_ITEM:
            self.event_type = event_type
            self._allow_none_item = False
            self._hide_all_item_obj()
            self._show_use_item()
            return True

        elif event_type == const.TASK_SELL_ITEM:
            self.event_type = event_type
            self._allow_none_item = False
            self._hide_all_item_obj()
            self._show_sell_item()
            return True

        elif event_type == const.TASK_HOLD_ITEM:
            self.event_type = event_type
            self._allow_none_item = True
            self._hide_all_item_obj()
            self._show_hold_item()
            return True

        return False

    @ignore_updates
    def configure(self, editor_params, save_callback=None, delayed_save_callback=None):
        super().configure(editor_params, save_callback=save_callback, delayed_save_callback=delayed_save_callback)
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
            self._consume_held_item.set_checked(event_def.hold_item.consumed)

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
                hold_item=HoldItemEventDefinition(self._item_selector.get(), consumed=self._consume_held_item.is_checked())
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
        self._location_value = custom_components.SimpleEntry(self, callback=self._trigger_delayed_save, width=20)
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
        self._location_value = custom_components.SimpleEntry(self, callback=self._trigger_delayed_save, width=20)
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
        self._location_value = custom_components.SimpleEntry(self, callback=self._trigger_delayed_save, width=20)
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

    def get_editor(self, editor_params:EditorParams, save_callback=None, delayed_save_callback=None, is_enabled=True) -> EventEditorBase:
        if editor_params.event_type in self._lookup:
            result:EventEditorBase = self._lookup[editor_params.event_type]
            result.configure(editor_params, save_callback=save_callback, delayed_save_callback=delayed_save_callback)
            if is_enabled:
                result.enable()
            else:
                result.disable()

            return result

        editor_type = self.TYPE_MAP.get(editor_params.event_type)
        if editor_type is None:
            raise ValueError(f"Could not find visual editor for event type: {editor_params.event_type}")

        result = editor_type(self._tk_container, editor_params)
        result.configure(editor_params, save_callback=save_callback, delayed_save_callback=delayed_save_callback)
        self._lookup[editor_params.event_type] = result

        # dumb hack, but wtv. Use the same editor for all item events
        if editor_params.event_type in const.ITEM_ROUTE_EVENT_TYPES:
            for other_event_type in const.ITEM_ROUTE_EVENT_TYPES:
                self._lookup[other_event_type] = result
        
        return result

