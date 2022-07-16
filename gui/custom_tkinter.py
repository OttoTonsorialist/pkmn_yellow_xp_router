from secrets import choice
import tkinter as tk
from tkinter import ttk

import pkmn.data_objects as data_objects
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
    
    def custom_insert(self, obj):
        if not isinstance(obj, router.EventGroup):
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
            values=tuple(self._get_attr_helper(obj, x.attr) for x in self._custom_col_data)
        )
    
    def refresh(self, ordered_objects):
        for x in self.get_children():
            self.delete(x)
        
        for x in ordered_objects:
            self.custom_insert(x)

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
                CustomGridview.CustomColumn('LevelUpsInto', 'pkmn_after_levelups', width=300),
                CustomGridview.CustomColumn('Level', 'pkmn_level', width=50),
                CustomGridview.CustomColumn('Total XP', 'total_xp', width=80),
                CustomGridview.CustomColumn('XP Gain', 'xp_gain', width=80),
                CustomGridview.CustomColumn('NextLevel', 'xp_to_next_level', width=80),
            ],
            text_field_attr='group_id',
            **kwargs
        )

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
    
    def new_values(self, option_list, default_val=None):
        self._menu.delete(0, "end")
        if not len(option_list):
            option_list = [""]
        for val in option_list:
            self._menu.add_command(label=val, command=lambda v=val: self._val.set(v))

        if default_val is None:
            default_val = option_list[0]
        self._val.set(default_val)

class SimpleButton(tk.Button):
    def enable(self):
        self["state"] = "normal"

    def disable(self):
        self["state"] = "disabled"


class PkmnViewer(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(bg="white", padx=10, pady=10, height=150, width=250)

        self._name_label = tk.Label(self, text="Pkmn:")
        self._name_label.config(bg="white")
        self._name_label.grid(row=0, column=0)
        self._name_value = tk.Label(self)
        self._name_value.config(bg="white")
        self._name_value.grid(row=0, column=1)

        self._level_label = tk.Label(self, text="XL:")
        self._level_label.config(bg="white")
        self._level_label.grid(row=0, column=2)
        self._level_value = tk.Label(self)
        self._level_value.config(bg="white")
        self._level_value.grid(row=0, column=3)

        self._xp_label = tk.Label(self, text="XP:")
        self._xp_label.config(bg="white")
        self._xp_label.grid(row=1, column=0)
        self._xp_value = tk.Label(self)
        self._xp_value.config(bg="white")
        self._xp_value.grid(row=1, column=1)

        self._speed_label = tk.Label(self, text="Spd:")
        self._speed_label.config(bg="white")
        self._speed_label.grid(row=1, column=2)
        self._speed_value = tk.Label(self)
        self._speed_value.config(bg="white")
        self._speed_value.grid(row=1, column=3)

        self._hp_label = tk.Label(self, text="HP:")
        self._hp_label.config(bg="white")
        self._hp_label.grid(row=2, column=0)
        self._hp_value = tk.Label(self)
        self._hp_value.config(bg="white")
        self._hp_value.grid(row=2, column=1)

        self._move_one_label = tk.Label(self, text="Move 1:")
        self._move_one_label.config(bg="white")
        self._move_one_label.grid(row=2, column=2)
        self._move_one_value = tk.Label(self)
        self._move_one_value.config(bg="white")
        self._move_one_value.grid(row=2, column=3)

        self._attack_label = tk.Label(self, text="Atk:")
        self._attack_label.config(bg="white")
        self._attack_label.grid(row=3, column=0)
        self._attack_value = tk.Label(self)
        self._attack_value.config(bg="white")
        self._attack_value.grid(row=3, column=1)

        self._move_two_label = tk.Label(self, text="Move 2:")
        self._move_two_label.config(bg="white")
        self._move_two_label.grid(row=3, column=2)
        self._move_two_value = tk.Label(self)
        self._move_two_value.config(bg="white")
        self._move_two_value.grid(row=3, column=3)

        self._defense_label = tk.Label(self, text="Defense:")
        self._defense_label.config(bg="white")
        self._defense_label.grid(row=4, column=0)
        self._defense_value = tk.Label(self)
        self._defense_value.config(bg="white")
        self._defense_value.grid(row=4, column=1)

        self._move_three_label = tk.Label(self, text="Move 3:")
        self._move_three_label.config(bg="white")
        self._move_three_label.grid(row=4, column=2)
        self._move_three_value = tk.Label(self)
        self._move_three_value.config(bg="white")
        self._move_three_value.grid(row=4, column=3)

        self._special_label = tk.Label(self, text="Special:")
        self._special_label.config(bg="white")
        self._special_label.grid(row=5, column=0)
        self._special_value = tk.Label(self)
        self._special_value.config(bg="white")
        self._special_value.grid(row=5, column=1)

        self._move_four_label = tk.Label(self, text="Move 3:")
        self._move_four_label.config(bg="white")
        self._move_four_label.grid(row=5, column=2)
        self._move_four_value = tk.Label(self)
        self._move_four_value.config(bg="white")
        self._move_four_value.grid(row=5, column=3)
    
    def set_pkmn(self, pkmn:data_objects.EnemyPkmn):
        self._name_value.config(text=pkmn.name)
        self._level_value.config(text=str(pkmn.level))
        self._xp_value.config(text=str(pkmn.xp))
        self._speed_value.config(text=str(pkmn.speed))
        self._hp_value.config(text=str(pkmn.hp))
        self._attack_value.config(text=str(pkmn.attack))
        self._defense_value.config(text=str(pkmn.defense))
        self._special_value.config(text=str(pkmn.special))

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

    def set_team(self, enemy_team:data_objects.Trainer):
        if enemy_team is None:
            pkmn = []
        else:
            pkmn = enemy_team.pkmn

        idx = -1
        for idx, cur_pkmn in enumerate(pkmn):
            self._all_pkmn[idx].set_pkmn(cur_pkmn)
            self._all_pkmn[idx].grid(row=idx//3,column=idx%3, padx=15, pady=15)
        
        for missing_idx in range(idx+1, 6):
            self._all_pkmn[missing_idx].grid_forget()