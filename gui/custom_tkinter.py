import os

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from utils.constants import const

# These three checkbox icons were isolated from Checkbox States.svg (https://commons.wikimedia.org/wiki/File:Checkbox_States.svg?uselang=en)
IM_CHECKED = os.path.join(const.ASSETS_PATH, "checked.png")
IM_UNCHECKED = os.path.join(const.ASSETS_PATH, "unchecked.png")
IM_TRISTATE = os.path.join(const.ASSETS_PATH, "tristate.png")


class CheckboxTreeview(ttk.Treeview):
    CHECKED_TAG = "checked"
    UNCHECKED_TAG =" unchecked"
    TRISTATE_TAG = "tristate"

    ALL_STATES = (CHECKED_TAG, UNCHECKED_TAG, TRISTATE_TAG)

    def __init__(self, root=None, checkbox_callback=None, checkbox_item_callback=None, **kwargs):
        super().__init__(root, **kwargs)

        # checkboxes are implemented with pictures
        self.im_checked = ImageTk.PhotoImage(Image.open(IM_CHECKED), master=self)
        self.im_unchecked = ImageTk.PhotoImage(Image.open(IM_UNCHECKED), master=self)
        self.im_tristate = ImageTk.PhotoImage(Image.open(IM_TRISTATE), master=self)
        self.tag_configure(self.UNCHECKED_TAG, image=self.im_unchecked, background="#E6E6E6", foreground="gray40")
        self.tag_configure(self.TRISTATE_TAG, image=self.im_tristate)
        self.tag_configure(self.CHECKED_TAG, image=self.im_checked)

        # This is the general callback, which happens on click
        self.checkbox_callback = checkbox_callback
        # This is the item specific callback, which happens on the state change of any item
        self.checkbox_item_callback = checkbox_item_callback
        self.bind("<Button-1>", self._box_click, True)
    
    def get_checkbox_state(self, item):
        tags = self.item(item, "tags")
        prev_state = [t for t in tags if t in self.ALL_STATES]
        if len(prev_state) != 0:
            return prev_state[0]
        return None

    def set_checkbox_state(self, item, state, force=False, bubble_up=False, bubble_down=False):
        tags = self.item(item, "tags")

        prev_state = [t for t in tags if t in self.ALL_STATES]
        if len(prev_state) != 0:
            prev_state = prev_state[0]
            # NOTE: if the state is not actually changing, then skip the rest of the function
            # primarily, this skips the state change callback, since the state is not actually changing
            # also cuts off the bubble_up chain once we don't have a functional change from it
            if prev_state == state:
                return
        else:
            prev_state = None

        new_tags = [t for t in tags if t not in self.ALL_STATES]
        # if an element wasn't previously set to a particular set, don't force it unless directed
        if prev_state is not None or force:
            new_tags.append(state)
            if self.checkbox_item_callback is not None:
                self.checkbox_item_callback(item, state)

        self.item(item, tags=tuple(new_tags))

        if bubble_up:
            self.update_parent(item, bubble_up=bubble_up)
        if bubble_down:
            self.update_descendants(item, state)
    
    def is_checked(self, item):
        return self.tag_has(self.CHECKED_TAG, item)

    def is_unchecked(self, item):
        return self.tag_has(self.UNCHECKED_TAG, item)

    def is_tristate(self, item):
        return self.tag_has(self.TRISTATE_TAG, item)

    def update_descendants(self, item, state):
        # can't force tristate downwards, so just ignore if this happens
        if state == self.TRISTATE_TAG:
            return

        for iid in self.get_children(item):
            self.set_checkbox_state(iid, state)
            self.update_descendants(iid, state)

    def update_parent(self, item, bubble_up=False):
        # we don't force states upwards, just need to recalculate what the parent will be
        # with the new state just set on one its children
        parent = self.parent(item)
        if parent:
            children_checked = [self.is_checked(c) for c in self.get_children(parent)]
            if all(children_checked):
                self.set_checkbox_state(parent, self.CHECKED_TAG, bubble_up=bubble_up)
            elif any(children_checked):
                self.set_checkbox_state(parent, self.TRISTATE_TAG, bubble_up=bubble_up)
            else:
                self.set_checkbox_state(parent, self.UNCHECKED_TAG, bubble_up=bubble_up)

    def _box_click(self, event):
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify("element", x, y)
        if "image" in elem:
            # a box was clicked
            item = self.identify_row(y)
            if self.tag_has(self.UNCHECKED_TAG, item) or self.tag_has(self.TRISTATE_TAG, item):
                result_state = self.CHECKED_TAG
            else:
                result_state = self.UNCHECKED_TAG

            self.set_checkbox_state(item, result_state, bubble_up=True)
            self.update_descendants(item, result_state)

            if self.checkbox_callback is not None:
                self.checkbox_callback()


class CustomGridview(CheckboxTreeview):
    class CustomColumn(object):
        def __init__(self, name, attr, width=None, hidden=False):
            self.id = None
            self.name = name
            self.width = width
            self.attr = attr
            self.hidden = hidden

    def __init__(self, *args, custom_col_data=None, text_field_attr=None, checkbox_attr=None, semantic_id_attr=None, tags_attr=None, **kwargs):
        self._custom_col_data = custom_col_data

        self._text_field_attr = text_field_attr
        self._checkbox_attr = checkbox_attr
        self._semantic_id_attr = semantic_id_attr
        self._tags_attr = tags_attr

        kwargs["columns"] = len(self._custom_col_data)
        super().__init__(*args, **kwargs, selectmode="browse")

        self._treeview_id_lookup = {}
        self._cfg_custom_columns()
    
    def _cfg_custom_columns(self):
        # set everyone's id
        for idx, cur_col in enumerate(self._custom_col_data):
            if not isinstance(cur_col, CustomGridview.CustomColumn):
                raise TypeError("Must be a CustomColumn")
            cur_col.id = "#" + str(idx + 1)

        # configure treeview columns attr
        self["columns"] = tuple(x.id for x in self._custom_col_data)
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
    
    def custom_upsert(self, obj, parent="", force_open=False, update_checkbox=False):
        if not(len(self._custom_col_data)):
            raise ValueError('CustomColumns not set, cannot custom insert')
        
        semantic_id = self._get_attr_helper(obj, self._semantic_id_attr)
        text_val = self._get_attr_helper(obj, self._text_field_attr)

        tags = self._get_attr_helper(obj, self._tags_attr)
        if update_checkbox:
            checkbox_val = self._get_attr_helper(obj, self._checkbox_attr)
            if checkbox_val is not None:
                tags.append(self.CHECKED_TAG if checkbox_val else self.UNCHECKED_TAG)
        
        tags = tuple(tags)

        if semantic_id in self._treeview_id_lookup:
            item_id = self._treeview_id_lookup[semantic_id]

            # if we aren't updating checkbox state, attempt to preserve previous state
            if not update_checkbox:
                prev_checkbox_state = self.get_checkbox_state(item_id)
                if prev_checkbox_state is not None:
                    tags = tuple(list(tags) + [prev_checkbox_state])

            self.item(
                item_id,
                text=str(text_val),
                values=tuple(self._get_attr_helper(obj, x.attr) for x in self._custom_col_data),
                tags=tags,
            )

        else:
            item_id = self.insert(
                parent,
                tk.END,
                text=str(text_val),
                values=tuple(self._get_attr_helper(obj, x.attr) for x in self._custom_col_data),
                tags=tags,
                open=force_open
            )

            self._treeview_id_lookup[semantic_id] = item_id

        return item_id


class CheckboxLabel(tk.Frame):
    CHECKED_STATE = "checked"
    UNCHECKED_STATE =" unchecked"

    def __init__(self, *args, text="", init_check_state=None, toggle_command=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._checkbox = tk.Label(self)
        self._text_label = tk.Label(self, text=text)

        self._checkbox.grid(row=0, column=0)
        self._text_label.grid(row=0, column=1)

        self.im_checked = ImageTk.PhotoImage(Image.open(IM_CHECKED), master=self)
        self.im_unchecked = ImageTk.PhotoImage(Image.open(IM_UNCHECKED), master=self)

        self.toggle_command = toggle_command
        if init_check_state is None:
            init_check_state = self.UNCHECKED_STATE
        self.set_checked(init_check_state == self.CHECKED_STATE)

        self.bind("<Button-1>", self.toggle_checked)
        self._checkbox.bind("<Button-1>", self.toggle_checked)
        self._text_label.bind("<Button-1>", self.toggle_checked)

    def set_checked(self, is_checked):
        if is_checked:
            self._check_state = self.CHECKED_STATE
            self._checkbox.config(image=self.im_checked)
        else:
            self._check_state = self.UNCHECKED_STATE
            self._checkbox.config(image=self.im_unchecked)

    def is_checked(self):
        return self._check_state == self.CHECKED_STATE
    
    def toggle_checked(self, *args, **kwargs):
        self.set_checked(not self.is_checked())
        if self.toggle_command is not None:
            self.toggle_command(self.is_checked())

class SimpleOptionMenu(ttk.Combobox):
    def __init__(self, root, option_list, callback=None, default_val=None, **kwargs):
        self._val = tk.StringVar()
        self.cur_options = option_list

        if default_val is None:
            default_val = option_list[0]
        self._val.set(default_val)

        if callback is not None:
            self._val.trace("w", callback)

        super().__init__(root, textvariable=self._val, values=option_list, state="readonly", **kwargs)
    
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
        self.config(values=self.cur_options)

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


class AutoClearingLabel(tk.Label):
    def __init__(self, *args, clear_timeout=3000, **kwargs):
        super().__init__(*args, **kwargs)
        self.clear_timeout = clear_timeout
        self.latest_clear_id = 0
    
    def set_message(self, value):
        self.config(text=value)
        self.latest_clear_id += 1
        self.after(self.clear_timeout, self._clear_id_curry(self.latest_clear_id))
    
    def _clear_id_curry(self, id_to_clear):
        def inner(*args, **kwargs):
            self._clear(id_to_clear)
        return inner

    def _clear(self, id_to_clear):
        if id_to_clear != self.latest_clear_id:
            return

        self.config(text="")


class Popup(tk.Toplevel):
    def __init__(self, main_window, *args, **kwargs):
        tk.Toplevel.__init__(self, main_window, *args, **kwargs)
        self._main_window = main_window
        # TODO: if we want the little flash thingy, try this instead of disabling: https://stackoverflow.com/a/28541762
        self._main_window.attributes('-disabled', True)

        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self, event=None):
        self._main_window.attributes('-disabled', False)
        self.destroy()
