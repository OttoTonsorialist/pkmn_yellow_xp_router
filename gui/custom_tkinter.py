from cgitb import text
from mimetypes import init
from posixpath import split
from secrets import choice
from subprocess import call
import tkinter as tk
from tkinter import ttk

import pkmn.data_objects as data_objects
from pkmn import route_state_objects
from pkmn import route_events
import pkmn.router as router
from utils.constants import const

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


class CustomGridview(tk.ttk.Treeview):
    class CustomColumn(object):
        def __init__(self, name, attr, width=None):
            self.id = None
            self.name = name
            self.width = width
            self.attr = attr

    def __init__(self, *args, custom_col_data=None, text_field_attr=None, **kwargs):
        self._custom_col_data = custom_col_data
        self._text_field_attr = text_field_attr

        kwargs['columns'] = len(self._custom_col_data)
        kwargs['show'] = ['headings']
        super().__init__(*args, **kwargs, selectmode="browse")

        self._cfg_custom_columns()
    
    def _cfg_custom_columns(self):
        # set everyone's id
        for idx, cur_col in enumerate(self._custom_col_data):
            if not isinstance(cur_col, CustomGridview.CustomColumn):
                raise TypeError('Must be a CustomColumn')
            cur_col.id = '#' + str(idx + 1)

        # configure treeview columns attr
        self['columns'] = tuple(x.id for x in self._custom_col_data)

        # configure actual thingy thing
        for idx, cur_col in enumerate(self._custom_col_data):
            if cur_col.width:
                self.column(cur_col.id, width=cur_col.width, stretch=tk.NO)
            else:
                self.column(cur_col.id, stretch=tk.YES)
            self.heading(cur_col.id, text=cur_col.name)
    
    def custom_insert(self, obj, selection_id=None, tags=None):
        if not isinstance(obj, route_events.EventGroup):
            raise TypeError('Can only support rendering EventGroups')

        if not(len(self._custom_col_data)):
            raise ValueError('CustomColumns not set, cannot custom insert')
        
        text = ''
        if self._text_field_attr:
            text = self._get_attr_helper(obj, self._text_field_attr)

        self.insert(
            '',
            tk.END,
            text=text,
            values=tuple(self._get_attr_helper(obj, x.attr) for x in self._custom_col_data),
            tags=tags
        )

        if selection_id is not None and text == selection_id:
            self.selection_set(self.get_children()[-1])
    
    def refresh(self, ordered_objects):
        raw_selection = self.selection()
        if len(raw_selection) == 1:
            cur_selection = self.item(raw_selection[0])['text']
        else:
            cur_selection = None

        for x in self.get_children():
            self.delete(x)
        
        for x in ordered_objects:
            self.custom_insert(x, selection_id=cur_selection)

    @staticmethod
    def _get_attr_helper(obj, attr):
        if hasattr(obj, attr):
            cur_attr = getattr(obj, attr)
            if callable(cur_attr):
                return cur_attr()
            return cur_attr

        return None
    

class RouteList(CustomGridview):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            custom_col_data=[
                CustomGridview.CustomColumn('Event', 'name'),
                CustomGridview.CustomColumn('LevelUpsInto', 'pkmn_after_levelups', width=220),
                CustomGridview.CustomColumn('Level', 'pkmn_level', width=50),
                CustomGridview.CustomColumn('Total Exp', 'total_xp', width=80),
                CustomGridview.CustomColumn('Exp Gain', 'xp_gain', width=80),
                CustomGridview.CustomColumn('ToNextLevel', 'xp_to_next_level', width=80),
                CustomGridview.CustomColumn('% TNL', 'percent_xp_to_next_level', width=80),
            ],
            text_field_attr='group_id',
            **kwargs
        )
        self.tag_configure(const.EVENT_TAG_ERRORS, background='#d98880')
        self.tag_configure(const.EVENT_TAG_IMPORTANT, background='#b3b6b7')
    
    def custom_insert(self, obj, selection_id=None):
        super(RouteList, self).custom_insert(obj, selection_id=selection_id, tags=(obj.get_tag(),))

    def selected_event_id(self):
        return self.item(self.focus())['text']


class SimpleOptionMenu(tk.OptionMenu):
    def __init__(self, root, option_list, callback=None, default_val=None):
        self._val = tk.StringVar()

        if default_val is None:
            default_val = option_list[0]
        self._val.set(default_val)

        if callback is not None:
            self._val.trace("w", callback)

        super().__init__(root, self._val, *option_list)
        self._menu = self.children["menu"]
    
    def get(self):
        return self._val.get()

    def set(self, val):
        # TODO: should double check to make sure it's valid... what happens if it's not in the option list?
        return self._val.set(val)
    
    def new_values(self, option_list, default_val=None):
        self._menu.delete(0, "end")
        if not len(option_list):
            option_list = [""]
        for val in option_list:
            self._menu.add_command(label=val, command=lambda v=val: self._val.set(v))

        if default_val is None:
            default_val = option_list[0]
        self._val.set(default_val)

class SimpleEntry(tk.Entry):
    def __init__(self, *args, initial_value="", callback=None, **kwargs):
        self._value = tk.StringVar(value=initial_value)

        super().__init__(*args, **kwargs, textvariable=self._value)
        if callback is not None:
            self._value.trace_add("write", callback)
    
    def get(self):
        return self._value.get()
    
    def set(self, value):
        self._value.set(value)

class AmountEntry(tk.Frame):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._down_button = tk.Button(self, text="v", command=self._lower_amt)
        self._down_button.grid(row=0, column=0)
        self._amount = SimpleEntry(self, initial_value="1", callback=callback)
        self._amount.grid(row=0, column=1)
        self._up_button = tk.Button(self, text="^", command=self._raise_amt)
        self._up_button.grid(row=0, column=2)
    
    def _lower_amt(self, *args, **kwargs):
        try:
            val = int(self._amount.get().strip())
            self._amount.set(str(val - 1))
        except Exception:
            pass

    def _raise_amt(self, *args, **kwargs):
        try:
            val = int(self._amount.get().strip())
            self._amount.set(str(val + 1))
        except Exception:
            pass
    
    def get(self):
        return self._amount.get()
    
    def set(self, value):
        self._amount.set(value)


class SimpleButton(tk.Button):
    def enable(self):
        self["state"] = "normal"

    def disable(self):
        self["state"] = "disabled"


class InventoryViewer(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(bg="white", padx=10, pady=10, height=150, width=250)

        self._money_label = tk.Label(self, text="Current Money: ")
        self._money_label.grid(row=0, column=0, columnspan=2)

        self._all_items = []
        split_point = const.BAG_LIMIT // 2
        for i in range(const.BAG_LIMIT):
            cur_item_label = tk.Label(self, text=f"# {i:0>2}: ", anchor=tk.W)
            cur_item_label.config(bg="white", width=20)
            cur_item_label.grid(row=(i % split_point) + 1, column=i // split_point, sticky=tk.W)
            self._all_items.append(cur_item_label)

    
    def set_inventory(self, inventory:route_state_objects.Inventory):
        self._money_label.config(text=f"Current Money: {inventory.cur_money}")

        idx = -1
        for idx in range(len(inventory.cur_items)):
            cur_item = inventory.cur_items[idx]
            self._all_items[idx].config(text=f"# {idx:0>2}: {cur_item.num}x {cur_item.base_item.name}")
        
        for missing_idx in range(idx + 1, const.BAG_LIMIT):
            self._all_items[missing_idx].config(text=f"# {missing_idx:0>2}:")


class PkmnViewer(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(bg="white", padx=10, pady=10, height=150, width=250)

        self._name_value = tk.Label(self, anchor=tk.W)
        self._name_value.config(bg="white")
        self._name_value.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        self._level_label = tk.Label(self, text="Lv:", anchor=tk.W)
        self._level_label.config(bg="white")
        self._level_label.grid(row=0, column=2, sticky=tk.W)
        self._level_value = tk.Label(self, anchor=tk.E)
        self._level_value.config(bg="white")
        self._level_value.grid(row=0, column=3, sticky=tk.E)

        self._hp_label = tk.Label(self, text="HP:", anchor=tk.W)
        self._hp_label.config(bg="white")
        self._hp_label.grid(row=1, column=0, sticky=tk.W)
        self._hp_value = tk.Label(self, anchor=tk.E)
        self._hp_value.config(bg="white")
        self._hp_value.grid(row=1, column=1, sticky=tk.E)

        self._xp_label = tk.Label(self, text="Exp:", anchor=tk.W)
        self._xp_label.config(bg="white")
        self._xp_label.grid(row=1, column=2, sticky=tk.W)
        self._xp_value = tk.Label(self, anchor=tk.E)
        self._xp_value.config(bg="white")
        self._xp_value.grid(row=1, column=3, sticky=tk.E)

        self._attack_label = tk.Label(self, text="Attack:", anchor=tk.W)
        self._attack_label.config(bg="white")
        self._attack_label.grid(row=2, column=0, sticky=tk.W)
        self._attack_value = tk.Label(self, anchor=tk.E)
        self._attack_value.config(bg="white")
        self._attack_value.grid(row=2, column=1, sticky=tk.E)

        self._move_one_label = tk.Label(self, text="Move 1:", anchor=tk.W)
        self._move_one_label.config(bg="white")
        self._move_one_label.grid(row=2, column=2, sticky=tk.W)
        self._move_one_value = tk.Label(self)
        self._move_one_value.config(bg="white")
        self._move_one_value.grid(row=2, column=3)

        self._defense_label = tk.Label(self, text="Defense:", anchor=tk.W)
        self._defense_label.config(bg="white")
        self._defense_label.grid(row=3, column=0, sticky=tk.W)
        self._defense_value = tk.Label(self, anchor=tk.E)
        self._defense_value.config(bg="white")
        self._defense_value.grid(row=3, column=1, sticky=tk.E)

        self._move_two_label = tk.Label(self, text="Move 2:", anchor=tk.W)
        self._move_two_label.config(bg="white")
        self._move_two_label.grid(row=3, column=2, sticky=tk.W)
        self._move_two_value = tk.Label(self)
        self._move_two_value.config(bg="white")
        self._move_two_value.grid(row=3, column=3)

        self._special_label = tk.Label(self, text="Special:", anchor=tk.W)
        self._special_label.config(bg="white")
        self._special_label.grid(row=4, column=0, sticky=tk.W)
        self._special_value = tk.Label(self, anchor=tk.E)
        self._special_value.config(bg="white")
        self._special_value.grid(row=4, column=1, sticky=tk.E)

        self._move_three_label = tk.Label(self, text="Move 3:", anchor=tk.W)
        self._move_three_label.config(bg="white")
        self._move_three_label.grid(row=4, column=2, sticky=tk.W)
        self._move_three_value = tk.Label(self)
        self._move_three_value.config(bg="white")
        self._move_three_value.grid(row=4, column=3)

        self._speed_label = tk.Label(self, text="Speed:", anchor=tk.W)
        self._speed_label.config(bg="white")
        self._speed_label.grid(row=5, column=0, sticky=tk.W)
        self._speed_value = tk.Label(self, anchor=tk.E)
        self._speed_value.config(bg="white")
        self._speed_value.grid(row=5, column=1, sticky=tk.E)

        self._move_four_label = tk.Label(self, text="Move 3:", anchor=tk.W)
        self._move_four_label.config(bg="white")
        self._move_four_label.grid(row=5, column=2, sticky=tk.W)
        self._move_four_value = tk.Label(self)
        self._move_four_value.config(bg="white")
        self._move_four_value.grid(row=5, column=3)

    def set_pkmn(self, pkmn:data_objects.EnemyPkmn, badges:route_state_objects.BadgeList=None):
        self._name_value.config(text=pkmn.name)
        self._level_value.config(text=str(pkmn.level))
        self._xp_value.config(text=str(pkmn.xp))
        self._hp_value.config(text=str(pkmn.hp))

        speed_val = str(pkmn.speed)
        if badges is not None and badges.soul:
            speed_val = "*" + speed_val
        self._speed_value.config(text=speed_val)

        attack_val = str(pkmn.attack)
        if badges is not None and badges.boulder:
            attack_val = "*" + attack_val
        self._attack_value.config(text=attack_val)

        defense_val = str(pkmn.defense)
        if badges is not None and badges.thunder:
            defense_val = "*" + defense_val
        self._defense_value.config(text=defense_val)

        special_val = str(pkmn.special)
        if badges is not None and badges.volcano:
            special_val = "*" + special_val
        self._special_value.config(text=special_val)

        self._move_one_value.config(text=pkmn.move_list[0])

        if len(pkmn.move_list) > 1:
            self._move_two_value.config(text=pkmn.move_list[1])
        else:
            self._move_two_value.config(text="")

        if len(pkmn.move_list) > 2:
            self._move_three_value.config(text=pkmn.move_list[2])
        else:
            self._move_three_value.config(text="")

        if len(pkmn.move_list) > 3:
            self._move_four_value.config(text=pkmn.move_list[3])
        else:
            self._move_four_value.config(text="")


class StateViewer(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inventory = InventoryViewer(self)
        self.inventory.pack(padx=10, pady=10)
        self.pkmn = PkmnViewer(self)
        self.pkmn.pack(padx=10, pady=10)
    
    def set_state(self, cur_state:route_state_objects.RouteState):
        self.inventory.set_inventory(cur_state.inventory)
        self.pkmn.set_pkmn(cur_state.solo_pkmn.get_renderable_pkmn(), cur_state.badges)


class EnemyPkmnTeam(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._all_pkmn = []

        self._all_pkmn.append(PkmnViewer(self))
        self._all_pkmn.append(PkmnViewer(self))
        self._all_pkmn.append(PkmnViewer(self))
        self._all_pkmn.append(PkmnViewer(self))
        self._all_pkmn.append(PkmnViewer(self))
        self._all_pkmn.append(PkmnViewer(self))

    def set_team(self, enemy_pkmn):
        if enemy_pkmn is None:
            enemy_pkmn = []

        idx = -1
        for idx, cur_pkmn in enumerate(enemy_pkmn):
            self._all_pkmn[idx].set_pkmn(cur_pkmn)
            self._all_pkmn[idx].grid(row=idx//3,column=idx%3, padx=15, pady=15)
        
        for missing_idx in range(idx+1, 6):
            self._all_pkmn[missing_idx].grid_forget()