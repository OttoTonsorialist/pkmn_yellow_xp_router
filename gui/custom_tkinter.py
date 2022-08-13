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
        def __init__(self, name, attr, width=None, hidden=False):
            self.id = None
            self.name = name
            self.width = width
            self.attr = attr
            self.hidden = hidden

    def __init__(self, *args, custom_col_data=None, text_field_attr=None, **kwargs):
        self._custom_col_data = custom_col_data
        self._text_field_attr = text_field_attr

        kwargs['columns'] = len(self._custom_col_data)
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
        self["displaycolumns"] = tuple(x.id for x in self._custom_col_data if not x.hidden)

        # configure actual thingy thing
        for idx, cur_col in enumerate(self._custom_col_data):
            if cur_col.hidden:
                continue
            if cur_col.width:
                self.column(cur_col.id, width=cur_col.width, stretch=tk.NO)
            else:
                self.column(cur_col.id, stretch=tk.YES)
            self.heading(cur_col.id, text=cur_col.name)

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
                #CustomGridview.CustomColumn('Event', 'name'),
                CustomGridview.CustomColumn('LevelUpsInto', 'get_pkmn_after_levelups', width=220),
                CustomGridview.CustomColumn('Level', 'pkmn_level', width=50),
                CustomGridview.CustomColumn('Total Exp', 'total_xp', width=80),
                CustomGridview.CustomColumn('Exp Gain', 'xp_gain', width=80),
                CustomGridview.CustomColumn('ToNextLevel', 'xp_to_next_level', width=80),
                CustomGridview.CustomColumn('% TNL', 'percent_xp_to_next_level', width=80),
                CustomGridview.CustomColumn('event_id', 'group_id', hidden=True),
            ],
            text_field_attr='name',
            **kwargs
        )
        self._semantic_id_field_attr = 'group_id'
        self.tag_configure(const.EVENT_TAG_ERRORS, background=const.ERROR_COLOR)
        self.tag_configure(const.EVENT_TAG_IMPORTANT, background=const.IMPORTANT_COLOR)
        # maps group id values to tkinter list ids
        self._treeview_id_lookup = {}
        self._event_description_lookup = {}
    
    def custom_upsert(self, obj, parent="", force_open=False):
        if not(len(self._custom_col_data)):
            raise ValueError('CustomColumns not set, cannot custom insert')
        
        semantic_id = self._get_attr_helper(obj, self._semantic_id_field_attr)
        text_val = self._get_attr_helper(obj, self._text_field_attr)

        if semantic_id in self._treeview_id_lookup:
            item_id = self._treeview_id_lookup[semantic_id]
            self.item(
                item_id,
                text=str(text_val),
                values=tuple(self._get_attr_helper(obj, x.attr) for x in self._custom_col_data),
                tags=(obj.get_tag(),),
            )

        else:
            item_id = self.insert(
                parent,
                tk.END,
                text=str(text_val),
                values=tuple(self._get_attr_helper(obj, x.attr) for x in self._custom_col_data),
                tags=(obj.get_tag(), ),
                open=force_open
            )

            self._treeview_id_lookup[semantic_id] = item_id
            self._event_description_lookup[semantic_id] = obj.name

        return item_id

    def get_selected_event_id(self):
        try:
            # super ugly. extract the value of the 'group_id' column. right now this is the last column, so just hard coding the index
            return int(self.item(self.focus())['values'][-1])
        except (ValueError, IndexError):
            return -1

    def refresh(self, all_events):
        # begin keeping track of the stuff we already know we're displaying
        # so we can eventually delete stuff that has been removed
        to_delete_ids = set(self._treeview_id_lookup.keys())
        self._refresh_recursively("", all_events, to_delete_ids)

        # we have now updated all relevant records, created missing ones, and ordered everything correctly
        # just need to remove any potentially deleted records
        for cur_del_id in to_delete_ids:
            try:
                self.delete(self._treeview_id_lookup[cur_del_id])
            except Exception:
                # note: this occurs because deleting an entry with children automatically removes all children too
                # so it will fail to remove the children aftewards
                # No actual problem though, just remove from the lookup and continue
                pass
            del self._treeview_id_lookup[cur_del_id]
    
    def _refresh_recursively(self, parent_id, event_list, to_delete_ids:set):
        for event_idx, event_obj in enumerate(event_list):
            semantic_id = self._get_attr_helper(event_obj, self._semantic_id_field_attr)

            default_expand = isinstance(event_obj, route_events.EventFolder)

            if semantic_id in to_delete_ids:
                to_delete_ids.remove(semantic_id)
                cur_event_id = self._treeview_id_lookup[semantic_id]
                self.custom_upsert(event_obj, parent=parent_id, force_open=default_expand)
            else:
                cur_event_id = self.custom_upsert(event_obj, parent=parent_id, force_open=default_expand)

            self.move(cur_event_id, parent_id, event_idx)

            if isinstance(event_obj, route_events.EventFolder):
                self._refresh_recursively(cur_event_id, event_obj.children, to_delete_ids)

            elif isinstance(event_obj, route_events.EventGroup):
                if len(event_obj.event_items) > 1:
                    for item_idx, item_obj in enumerate(event_obj.event_items):
                        item_semantic_id = self._get_attr_helper(item_obj, self._semantic_id_field_attr)
                        if item_semantic_id in to_delete_ids:
                            item_id = self._treeview_id_lookup[item_semantic_id]
                            to_delete_ids.remove(item_semantic_id)
                            self.custom_upsert(item_obj, parent=cur_event_id)
                        else:
                            item_id = self.custom_upsert(item_obj, parent=cur_event_id)

                        self.move(item_id, cur_event_id, item_idx)


class SimpleOptionMenu(tk.OptionMenu):
    def __init__(self, root, option_list, callback=None, default_val=None):
        self._val = tk.StringVar()
        self.cur_options = option_list

        if default_val is None:
            default_val = option_list[0]
        self._val.set(default_val)

        if callback is not None:
            self._val.trace("w", callback)

        super().__init__(root, self._val, *option_list)
        self._menu = self.children["menu"]
    
    def enable(self):
        self.configure(state="active")
    
    def disable(self):
        self.configure(state="disabled")
    
    def get(self):
        return self._val.get()

    def set(self, val):
        # TODO: should double check to make sure it's valid... what happens if it's not in the option list?
        return self._val.set(val)
    
    def new_values(self, option_list, default_val=None):
        self.cur_options = option_list
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
        self.config(bg="white", padx=5, pady=5, height=150, width=250)
        self._labels = []

        self._name_value = tk.Label(self, anchor=tk.W, background="white")
        self._name_value.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        self._level_label = tk.Label(self, text="Lv:", anchor=tk.W, background="white")
        self._level_label.grid(row=0, column=2, sticky=tk.W)
        self._labels.append(self._level_label)
        self._level_value = tk.Label(self, anchor=tk.E, background="white")
        self._level_value.grid(row=0, column=3, sticky=tk.E)

        self._hp_label = tk.Label(self, text="HP:", anchor=tk.W, background="white")
        self._hp_label.grid(row=1, column=0, sticky=tk.W)
        self._labels.append(self._hp_label)
        self._hp_value = tk.Label(self, anchor=tk.E, background="white")
        self._hp_value.grid(row=1, column=1, sticky=tk.E)

        self._xp_label = tk.Label(self, text="Exp:", anchor=tk.W, background="white")
        self._xp_label.grid(row=1, column=2, sticky=tk.W)
        self._labels.append(self._xp_label)
        self._xp_value = tk.Label(self, anchor=tk.E, background="white")
        self._xp_value.grid(row=1, column=3, sticky=tk.E)

        self._attack_label = tk.Label(self, text="Attack:", anchor=tk.W, background="white")
        self._attack_label.grid(row=2, column=0, sticky=tk.W)
        self._labels.append(self._attack_label)
        self._attack_value = tk.Label(self, anchor=tk.E, background="white")
        self._attack_value.grid(row=2, column=1, sticky=tk.E)

        self._move_one_label = tk.Label(self, text="Move 1:", anchor=tk.W, background="white")
        self._move_one_label.grid(row=2, column=2, sticky=tk.W)
        self._labels.append(self._move_one_label)
        self._move_one_value = tk.Label(self, background="white")
        self._move_one_value.grid(row=2, column=3)

        self._defense_label = tk.Label(self, text="Defense:", anchor=tk.W, background="white")
        self._defense_label.grid(row=3, column=0, sticky=tk.W)
        self._labels.append(self._defense_label)
        self._defense_value = tk.Label(self, anchor=tk.E, background="white")
        self._defense_value.grid(row=3, column=1, sticky=tk.E)

        self._move_two_label = tk.Label(self, text="Move 2:", anchor=tk.W, background="white")
        self._move_two_label.grid(row=3, column=2, sticky=tk.W)
        self._labels.append(self._move_two_label)
        self._move_two_value = tk.Label(self, background="white")
        self._move_two_value.grid(row=3, column=3)

        self._special_label = tk.Label(self, text="Special:", anchor=tk.W, background="white")
        self._special_label.grid(row=4, column=0, sticky=tk.W)
        self._labels.append(self._special_label)
        self._special_value = tk.Label(self, anchor=tk.E, background="white")
        self._special_value.grid(row=4, column=1, sticky=tk.E)

        self._move_three_label = tk.Label(self, text="Move 3:", anchor=tk.W, background="white")
        self._move_three_label.grid(row=4, column=2, sticky=tk.W)
        self._labels.append(self._move_three_label)
        self._move_three_value = tk.Label(self, background="white")
        self._move_three_value.grid(row=4, column=3)

        self._speed_frame = tk.Frame(self, background="white")
        self._speed_frame.grid(row=5, column=0, sticky=tk.EW, columnspan=2)
        self._speed_label = tk.Label(self._speed_frame, text="Speed:", anchor=tk.W, background="white")
        self._speed_label.grid(row=0, column=0, sticky=tk.EW)
        self._labels.append(self._speed_label)
        self._speed_value = tk.Label(self._speed_frame, anchor=tk.E, background="white")
        self._speed_value.grid(row=0, column=1, sticky=tk.EW)
        self._speed_frame.columnconfigure(1, weight=1)

        self._move_four_label = tk.Label(self, text="Move 4:", anchor=tk.W, background="white")
        self._move_four_label.grid(row=5, column=2, sticky=tk.W)
        self._labels.append(self._move_four_label)
        self._move_four_value = tk.Label(self, background="white")
        self._move_four_value.grid(row=5, column=3)

    def set_pkmn(self, pkmn:data_objects.EnemyPkmn, badges:data_objects.BadgeList=None, speed_bg_color=None):
        if speed_bg_color is None:
            speed_bg_color = "white"
        
        self._name_value.config(text=pkmn.name)
        self._level_value.config(text=str(pkmn.level))
        self._xp_value.config(text=str(pkmn.xp))
        self._hp_value.config(text=str(pkmn.hp))

        speed_val = str(pkmn.speed)
        if badges is not None and badges.soul:
            speed_val = "*" + speed_val
        self._speed_value.config(text=speed_val, background=speed_bg_color)
        self._speed_label.config(background=speed_bg_color)

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
        self.pkmn = PkmnViewer(self)
        self.pkmn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.S)
        self.stat_xp = StatExpViewer(self)
        self.stat_xp.grid(row=0, column=1, padx=5, pady=5, sticky=tk.S)
        self.inventory = InventoryViewer(self)
        self.inventory.grid(row=0, column=2, padx=5, pady=5, sticky=tk.S)
    
    def set_state(self, cur_state:route_state_objects.RouteState):
        self.inventory.set_inventory(cur_state.inventory)
        self.pkmn.set_pkmn(cur_state.solo_pkmn.get_renderable_pkmn(), cur_state.badges)
        self.stat_xp.set_state(cur_state)


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

    def set_team(self, enemy_pkmn, cur_state:route_state_objects.RouteState=None):
        if enemy_pkmn is None:
            enemy_pkmn = []

        idx = -1
        for idx, cur_pkmn in enumerate(enemy_pkmn):
            if cur_state is not None:
                if cur_state.solo_pkmn.cur_stats.speed > cur_pkmn.speed:
                    bg_color = const.SPEED_WIN_COLOR
                elif cur_state.solo_pkmn.cur_stats.speed == cur_pkmn.speed:
                    bg_color = const.SPEED_TIE_COLOR
                else:
                    bg_color = const.SPEED_LOSS_COLOR
                cur_state = cur_state.defeat_pkmn(cur_pkmn)[0]
            else:
                bg_color = "white"

            self._all_pkmn[idx].set_pkmn(cur_pkmn, speed_bg_color=bg_color)
            self._all_pkmn[idx].grid(row=idx//3,column=idx%3, padx=5, pady=5)
        
        for missing_idx in range(idx+1, 6):
            self._all_pkmn[missing_idx].grid_forget()


class BadgeBoostViewer(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._info_frame = tk.Frame(self)
        self._info_frame.grid(row=0, column=0)

        self._move_selector_label = tk.Label(self._info_frame, text="Setup Move: ")
        stat_modifier_moves = list(const.STAT_INCREASE_MOVES.keys())
        stat_modifier_moves += list(const.STAT_DECREASE_MOVES.keys())
        self._move_selector = SimpleOptionMenu(self._info_frame, stat_modifier_moves, callback=self._move_selected_callback)
        self._move_selector_label.pack()
        self._move_selector.pack()

        self._badge_summary = tk.Label(self._info_frame)
        self._badge_summary.pack(pady=10)

        self._state:route_state_objects.RouteState = None

        # 6 possible badge boosts from a single setup move, plus unmodified summary
        NUM_SUMMARIES = 7
        NUM_COLS = 4
        self._frames = []
        self._labels = []
        self._viewers = []

        for idx in range(NUM_SUMMARIES):
            cur_frame = tk.Frame(self)
            # add 1 because the 0th frame is the info frame
            cur_frame.grid(row=((idx + 1) // NUM_COLS), column=((idx + 1) % NUM_COLS), padx=3, pady=3)

            self._frames.append(cur_frame)
            self._labels.append(tk.Label(cur_frame))
            self._viewers.append(PkmnViewer(cur_frame))
    
    def _clear_all_summaries(self):
        # intentionally skip base stat frame
        for idx in range(1, len(self._frames)):
            self._labels[idx].pack_forget()
            self._viewers[idx].pack_forget()
    
    def _update_base_summary(self):
        if self._state is None:
            self._labels[0].pack_forget()
            self._viewers[0].pack_forget()
            return

        self._labels[0].configure(text=f"Base: {self._state.solo_pkmn.name}")
        self._labels[0].pack()

        self._viewers[0].set_pkmn(self._state.solo_pkmn.get_renderable_pkmn(), badges=self._state.badges)
        self._viewers[0].pack(padx=3, pady=3)
    
    def _move_selected_callback(self, *args, **kwargs):
        self._update_base_summary()

        move = self._move_selector.get()
        if not move:
            self._clear_all_summaries()
            return
        
        prev_mod = data_objects.StageModifiers()
        stage_mod = None
        for idx in range(1, len(self._frames)):
            stage_mod = prev_mod.after_move(move)
            if stage_mod == prev_mod:
                self._labels[idx].pack_forget()
                self._viewers[idx].pack_forget()
                continue

            prev_mod = stage_mod

            self._labels[idx].configure(text=f"{idx}x {move}")
            self._labels[idx].pack()

            self._viewers[idx].set_pkmn(self._state.solo_pkmn.get_battle_stats(self._state.badges, stage_mod), badges=self._state.badges)
            self._viewers[idx].pack()

    
    def set_state(self, state:route_state_objects.RouteState):
        self._state = state

        # when state changes, update the badge list label
        raw_badge_text = self._state.badges.to_string(verbose=False)
        final_badge_text = raw_badge_text.split(":")[0]
        badges = raw_badge_text.split(":")[1]

        if not badges.strip():
            final_badge_text += "\nNone"
        else:
            earned_badges = badges.split(',')
            badges = ""
            while len(earned_badges) > 0:
                if len(earned_badges) == 1:
                    badges += f"{earned_badges[0]}\n"
                    del earned_badges[0]
                else:
                    badges += f"{earned_badges[0]}, {earned_badges[1]}\n"
                    del earned_badges[0]
                    del earned_badges[0]

            final_badge_text += '\n' + badges.strip()

        self._badge_summary.config(text=final_badge_text)
        self._move_selected_callback()


class StatColumn(tk.Frame):
    def __init__(self, *args, num_rows=4, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(bg="white")

        self._header_frame = tk.Frame(self, background="white")
        self._header_frame.pack()
        self._header = tk.Label(self._header_frame, background="white")

        self._frames = []
        self._labels = []
        self._values = []

        for idx in range(num_rows):
            cur_frame = tk.Frame(self, background="white")
            cur_frame.pack(fill=tk.X)
            self._frames.append(cur_frame)

            cur_label = tk.Label(cur_frame, anchor=tk.W, background="white")
            cur_label.grid(row=0, column=0, sticky=tk.EW)
            self._labels.append(cur_label)

            cur_value = tk.Label(cur_frame, anchor=tk.E, background="white")
            cur_value.grid(row=0, column=1, sticky=tk.EW)
            self._values.append(cur_value)

            cur_frame.columnconfigure(1, weight=1)
    
    def set_header(self, header):
        if header is None or header == "":
            self._header.pack_forget()
            return
        
        self._header.pack()
        self._header.config(text=header)
    
    def set_labels(self, label_text_iterable):
        for idx, cur_label_text in enumerate(label_text_iterable):
            if idx >= len(self._labels):
                break
            self._labels[idx].configure(text=cur_label_text)
        
        if len(label_text_iterable) < len(self._labels):
            for idx in range(len(label_text_iterable), len(self._labels)):
                self._labels[idx].configure(text="")
    
    def set_values(self, value_text_iterable):
        for idx, cur_value_text in enumerate(value_text_iterable):
            if idx >= len(self._values):
                break
            self._values[idx].configure(text=cur_value_text)
        
        if len(value_text_iterable) < len(self._values):
            for idx in range(len(value_text_iterable), len(self._values)):
                self._values[idx].configure(text="")


class StatExpViewer(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(bg="white", padx=5, pady=5, height=150, width=250)
        stat_labels =[
            "HP:",
            "Attack:",
            "Defense:",
            "Special:",
            "Speed:",
        ] 

        self._state = None
        self._net_gain_column = StatColumn(self, num_rows=len(stat_labels))
        self._net_gain_column.set_labels(stat_labels)
        self._net_gain_column.set_header("Net Stats\nFrom StatExp")
        self._net_gain_column.grid(row=0, column=0)

        self._realized_stat_xp_column = StatColumn(self, num_rows=len(stat_labels))
        self._realized_stat_xp_column.set_labels(stat_labels)
        self._realized_stat_xp_column.set_header("Realized\nStatExp")
        self._realized_stat_xp_column.grid(row=0, column=1)

        self._total_stat_xp_column = StatColumn(self, num_rows=len(stat_labels))
        self._total_stat_xp_column.set_labels(stat_labels)
        self._total_stat_xp_column.set_header("Total\nStatExp")
        self._total_stat_xp_column.grid(row=0, column=2)
    
    def _vals_from_stat_block(self, stat_block:data_objects.StatBlock):
        # NOTE: re-ordering stats over special
        return [stat_block.hp, stat_block.attack, stat_block.defense, stat_block.special, stat_block.speed]

    def set_state(self, state:route_state_objects.RouteState):
        self._state = state

        self._net_gain_column.set_values(
            self._vals_from_stat_block(
                self._state.solo_pkmn.get_net_gain_from_stat_xp(self._state.badges)
            )
        )
        self._realized_stat_xp_column.set_values(
            self._vals_from_stat_block(
                self._state.solo_pkmn.realized_stat_xp
            )
        )
        self._total_stat_xp_column.set_values(
            self._vals_from_stat_block(
                self._state.solo_pkmn.realized_stat_xp.add(self._state.solo_pkmn.unrealized_stat_xp)
            )
        )
