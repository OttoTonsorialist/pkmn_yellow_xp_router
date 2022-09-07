import tkinter as tk
import tkinter.font

from gui import custom_tkinter
import pkmn.data_objects as data_objects
from pkmn import route_state_objects
from pkmn import route_events
from pkmn.router import Router
from utils.constants import const

class RouteList(custom_tkinter.CustomGridview):
    def __init__(self, route_list:Router, *args, **kwargs):
        self._route_list = route_list
        super().__init__(
            *args,
            custom_col_data=[
                custom_tkinter.CustomGridview.CustomColumn('LevelUpsInto', 'get_pkmn_after_levelups', width=220),
                custom_tkinter.CustomGridview.CustomColumn('Level', 'pkmn_level', width=50),
                custom_tkinter.CustomGridview.CustomColumn('Total Exp', 'total_xp', width=80),
                custom_tkinter.CustomGridview.CustomColumn('Exp Gain', 'xp_gain', width=80),
                custom_tkinter.CustomGridview.CustomColumn('ToNextLevel', 'xp_to_next_level', width=80),
                custom_tkinter.CustomGridview.CustomColumn('% TNL', 'percent_xp_to_next_level', width=80),
                custom_tkinter.CustomGridview.CustomColumn('event_id', 'group_id', hidden=True),
            ],
            text_field_attr='name',
            semantic_id_attr='group_id',
            tags_attr='get_tags',
            checkbox_attr='is_enabled',
            req_column_width=325,
            checkbox_callback=self.general_checkbox_callback_fn,
            checkbox_item_callback=self.checkbox_item_callback_fn,
            **kwargs
        )

        self.tag_configure(const.EVENT_TAG_ERRORS, background=const.ERROR_COLOR)
        self.tag_configure(const.EVENT_TAG_IMPORTANT, background=const.IMPORTANT_COLOR)

        self.bind("<<TreeviewOpen>>", self._treeview_opened_callback)
        self.bind("<<TreeviewClose>>", self._treeview_closed_callback)

    def general_checkbox_callback_fn(self):
        self._route_list._recalc()
        self.refresh()

    def _treeview_opened_callback(self, *args, **kwargs):
        selected = self.get_all_selected_event_ids()
        # no easy way to figure out unless only one is sleected. Just give up otherwise
        if len(selected) == 1:
            cur_obj = self._route_list.get_event_obj(selected[0])
            if isinstance(cur_obj, route_events.EventFolder):
                cur_obj.expanded = True

    def _treeview_closed_callback(self, event):
        selected = self.get_all_selected_event_ids()
        # no easy way to figure out unless only one is sleected. Just give up otherwise
        if len(selected) == 1:
            cur_obj = self._route_list.get_event_obj(selected[0])
            if isinstance(cur_obj, route_events.EventFolder):
                cur_obj.expanded = False
    
    def checkbox_item_callback_fn(self, item_id, new_state):
        if new_state == self.TRISTATE_TAG:
            return

        raw_obj = self._route_list.get_event_obj(self._get_route_id_from_item_id(item_id))
        raw_obj.set_enabled_status(new_state == self.CHECKED_TAG)
    
    def _get_route_id_from_item_id(self, iid):
        try:
            # super ugly. extract the value of the 'group_id' column. right now this is the last column, so just hard coding the index
            return int(self.item(iid)['values'][-1])
        except (ValueError, IndexError):
            return -1
    
    def get_all_selected_event_ids(self, allow_event_items=True):
        temp = set(self.selection())
        result = []
        for cur_iid in self.selection():
            # event items can't be manipulated at all
            cur_route_id = self._get_route_id_from_item_id(cur_iid)
            if not allow_event_items and isinstance(self._route_list.get_event_obj(cur_route_id), route_events.EventItem):
                continue

            # if any folders are selected, ignore all events that are children of that folder
            # we basically say that you have selected the container, and thus do not need to select any of the child objects
            if self.parent(cur_iid) in temp:
                continue
            
            result.append(cur_route_id)

        return result

    def refresh(self, *args, **kwargs):
        # begin keeping track of the stuff we already know we're displaying
        # so we can eventually delete stuff that has been removed
        to_delete_ids = set(self._treeview_id_lookup.keys())
        self._refresh_recursively("", self._route_list.root_folder.children, to_delete_ids)

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

        self.event_generate(const.ROUTE_LIST_REFRESH_EVENT)
    
    def _refresh_recursively(self, parent_id, event_list, to_delete_ids:set):
        last_event_item_id = None
        for event_idx, event_obj in enumerate(event_list):
            semantic_id = self._get_attr_helper(event_obj, self._semantic_id_attr)

            if isinstance(event_obj, route_events.EventFolder):
                is_folder = True
                force_open = event_obj.expanded
            else:
                is_folder = False
                force_open = False

            if semantic_id in to_delete_ids:
                to_delete_ids.remove(semantic_id)
                cur_event_id = self._treeview_id_lookup[semantic_id]
                self.custom_upsert(event_obj, parent=parent_id, force_open=force_open, update_checkbox=(not is_folder))
            else:
                # when first creating the event, make sure it is defined with a checkbox
                cur_event_id = self.custom_upsert(event_obj, parent=parent_id, force_open=force_open, update_checkbox=True)

            self.move(cur_event_id, parent_id, event_idx)

            if is_folder:
                self._refresh_recursively(cur_event_id, event_obj.children, to_delete_ids)

            elif isinstance(event_obj, route_events.EventGroup):
                last_event_item_id = cur_event_id
                if len(event_obj.event_items) > 1:
                    for item_idx, item_obj in enumerate(event_obj.event_items):
                        item_semantic_id = self._get_attr_helper(item_obj, self._semantic_id_attr)
                        if item_semantic_id in to_delete_ids:
                            item_id = self._treeview_id_lookup[item_semantic_id]
                            to_delete_ids.remove(item_semantic_id)
                            self.custom_upsert(item_obj, parent=cur_event_id)
                        else:
                            item_id = self.custom_upsert(item_obj, parent=cur_event_id)

                        self.move(item_id, cur_event_id, item_idx)
        
        if last_event_item_id:
            # Folders can be in the tristate checkbox state, based on the states of its children
            # So whenever we're done populating a folder's children, recalculate its checkbox state
            # (only if it has any children)
            # TODO: this has some potential weirdness if you have a folder that contains only folders... fix later
            self.update_parent(last_event_item_id)


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
    def __init__(self, *args, stats_only=False, font_size=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.stats_only = stats_only
        self.config(bg="white", padx=5, pady=5, height=150)
        self._labels = []

        font_to_use = tkinter.font.nametofont("TkDefaultFont")
        if font_size is not None:
            font_to_use = (font_to_use.name, font_size)

        self.stat_width = 4
        self.move_width = 11

        self._name_value = tk.Label(self, background=const.HEADER_BG_COLOR, font=font_to_use)
        self._name_value.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        self._level_frame = tk.Frame(self, background=const.HEADER_BG_COLOR)
        self._level_frame.grid(row=1, column=0, sticky=tk.EW)

        self._level_label = tk.Label(self._level_frame, text="Lv:", anchor=tk.W, background=const.HEADER_BG_COLOR, font=font_to_use)
        self._level_label.grid(row=1, column=0, sticky=tk.W)
        self._labels.append(self._level_label)
        self._level_value = tk.Label(self._level_frame, anchor=tk.E, background=const.HEADER_BG_COLOR, font=font_to_use)
        self._level_value.grid(row=1, column=1, sticky=tk.E)
        self._level_frame.columnconfigure(1, weight=1)

        self.stat_column = StatColumn(self, bg_color=const.STAT_BG_COLOR, val_width=self.stat_width, num_rows=5, font=font_to_use)
        self.stat_column.set_labels(["HP:", "Attack:", "Defense:", "Special:", "Speed:"])
        self.stat_column.set_header("")
        self.stat_column.grid(row=2, column=0, sticky=tk.W)

        self._xp_frame = tk.Frame(self, background=const.HEADER_BG_COLOR)
        self._xp_label = tk.Label(self._xp_frame, text="Exp:", anchor=tk.W, background=const.HEADER_BG_COLOR, font=font_to_use)
        self._xp_label.grid(row=1, column=0, sticky=tk.W)
        self._labels.append(self._xp_label)
        self._xp_value = tk.Label(self._xp_frame, anchor=tk.E, background=const.HEADER_BG_COLOR, font=font_to_use)
        self._xp_value.grid(row=1, column=1, sticky=tk.E)
        self._xp_frame.columnconfigure(1, weight=1)

        self.move_column = StatColumn(self, bg_color=const.MOVE_BG_COLOR, val_width=self.move_width, num_rows=5, font=font_to_use)
        self.move_column.set_labels(["Move 1:", "Move 2:", "Move 3:", "Move 4:", ""])
        self.move_column.set_header("")

        if not self.stats_only:
            self._xp_frame.grid(row=1, column=1, sticky=tk.EW)
            self.move_column.grid(row=2, column=1, sticky=tk.E)


    def set_pkmn(self, pkmn:data_objects.EnemyPkmn, badges:data_objects.BadgeList=None, speed_bg_color=None):
        if speed_bg_color is None:
            speed_bg_color = const.STAT_BG_COLOR
        
        self._name_value.config(text=pkmn.name)
        self._level_value.config(text=str(pkmn.level))
        self._xp_value.config(text=str(pkmn.xp))

        attack_val = str(pkmn.attack)
        if badges is not None and badges.boulder:
            attack_val = "*" + attack_val

        defense_val = str(pkmn.defense)
        if badges is not None and badges.thunder:
            defense_val = "*" + defense_val

        special_val = str(pkmn.special)
        if badges is not None and badges.volcano:
            special_val = "*" + special_val

        speed_val = str(pkmn.speed)
        if badges is not None and badges.soul:
            speed_val = "*" + speed_val
        
        self.stat_column.set_values(
            [str(pkmn.hp), attack_val, defense_val, special_val, speed_val],
            bg_color_iterable=[None, None, None, None, speed_bg_color]
        )

        self.move_column.set_values(pkmn.move_list)


class StateViewer(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pkmn = PkmnViewer(self, font_size=10)
        self.pkmn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.S)
        self.stat_xp = StatExpViewer(self)
        self.stat_xp.grid(row=0, column=1, padx=5, pady=5, sticky=tk.S)
        self.inventory = InventoryViewer(self)
        self.inventory.grid(row=0, column=2, padx=5, pady=5, sticky=tk.S)
    
    def set_state(self, cur_state:route_state_objects.RouteState):
        self.inventory.set_inventory(cur_state.inventory)
        self.pkmn.set_pkmn(cur_state.solo_pkmn.get_pkmn_obj(cur_state.badges), cur_state.badges)
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
        self._move_selector = custom_tkinter.SimpleOptionMenu(self._info_frame, stat_modifier_moves, callback=self._move_selected_callback)
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
            self._viewers.append(PkmnViewer(cur_frame, stats_only=True))
    
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

        self._viewers[0].set_pkmn(self._state.solo_pkmn.get_pkmn_obj(self._state.badges), badges=self._state.badges)
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

            self._viewers[idx].set_pkmn(self._state.solo_pkmn.get_pkmn_obj(self._state.badges, stage_mod), badges=self._state.badges)
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
    def __init__(self, *args, num_rows=4, bg_color="white", label_width=None, val_width=None, font=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_color = bg_color
        self.config(bg=self.bg_color)

        if font is None:
            font = tkinter.font.nametofont("TkDefaultFont")
        self.font = font

        self._header_frame = tk.Frame(self, background=self.bg_color)
        self._header_frame.pack()
        self._header = tk.Label(self._header_frame, background=self.bg_color, font=font)

        self._frames = []
        self._labels = []
        self._values = []

        for idx in range(num_rows):
            cur_frame = tk.Frame(self, background=self.bg_color)
            cur_frame.pack(fill=tk.X)
            self._frames.append(cur_frame)

            cur_label = tk.Label(cur_frame, anchor=tk.W, background=self.bg_color, width=label_width, font=font)
            cur_label.grid(row=0, column=0, sticky=tk.EW)
            self._labels.append(cur_label)

            cur_value = tk.Label(cur_frame, anchor=tk.E, background=self.bg_color, width=val_width, font=font)
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
    
    def set_values(self, value_text_iterable, bg_color_iterable=None):
        if bg_color_iterable is None:
            bg_color_iterable = [self.bg_color for _ in value_text_iterable]
        
        for idx in range(len(bg_color_iterable)):
            if bg_color_iterable[idx] == None:
                bg_color_iterable[idx] = self.bg_color

        for idx, cur_value_text in enumerate(value_text_iterable):
            if idx >= len(self._values):
                break
            self._values[idx].configure(text=cur_value_text, background=bg_color_iterable[idx])
            self._labels[idx].configure(background=bg_color_iterable[idx])
        
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
        self._net_gain_column = StatColumn(self, num_rows=len(stat_labels), val_width=3, bg_color=const.HEADER_BG_COLOR)
        self._net_gain_column.set_labels(stat_labels)
        self._net_gain_column.set_header("Net Stats\nFrom StatExp")
        self._net_gain_column.grid(row=0, column=0)

        self._realized_stat_xp_column = StatColumn(self, num_rows=len(stat_labels), val_width=5, bg_color=const.STAT_BG_COLOR)
        self._realized_stat_xp_column.set_labels(stat_labels)
        self._realized_stat_xp_column.set_header("Realized\nStatExp")
        self._realized_stat_xp_column.grid(row=0, column=1)

        self._total_stat_xp_column = StatColumn(self, num_rows=len(stat_labels), val_width=5, bg_color=const.MOVE_BG_COLOR)
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