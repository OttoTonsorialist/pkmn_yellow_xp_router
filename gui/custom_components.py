import os

import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk

from utils.constants import const
from utils.config_manager import config

# These three checkbox icons were isolated from Checkbox States.svg (https://commons.wikimedia.org/wiki/File:Checkbox_States.svg?uselang=en)
IM_UNCHECKED = os.path.join(const.ASSETS_PATH, "theme", "dark", "circle-hover.gif")
IM_CHECKED = os.path.join(const.ASSETS_PATH, "theme", "dark", "check-basic.gif")
IM_TRISTATE = os.path.join(const.ASSETS_PATH, "theme", "dark", "check-tri-basic.gif")


class CheckboxTreeview(ttk.Treeview):
    CHECKED_TAG = "checked"
    UNCHECKED_TAG =" unchecked"
    TRISTATE_TAG = "tristate"

    ALL_STATES = (CHECKED_TAG, UNCHECKED_TAG, TRISTATE_TAG)

    def __init__(self, root=None, checkbox_callback=None, checkbox_item_callback=None, **kwargs):
        super().__init__(root, **kwargs)

        # checkboxes are implemented with pictures
        img_resize = 14
        self.im_checked = ImageTk.PhotoImage(Image.open(IM_CHECKED).resize((img_resize, img_resize)), master=self)
        self.im_unchecked = ImageTk.PhotoImage(Image.open(IM_UNCHECKED).resize((img_resize, img_resize)), master=self)
        self.im_tristate = ImageTk.PhotoImage(Image.open(IM_TRISTATE).resize((img_resize, img_resize)), master=self)
        # TODO: figure out how to connect this to the actual styles...
        self.tag_configure(self.UNCHECKED_TAG, image=self.im_unchecked, background="#cbcbcb", foreground="gray40")
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

    def _set_checkbox_state(self, item, state, force=False):
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

        self.force_active_parent(item)
    
    def is_checked(self, item):
        return self.tag_has(self.CHECKED_TAG, item)

    def is_unchecked(self, item):
        return self.tag_has(self.UNCHECKED_TAG, item)

    def is_tristate(self, item):
        return self.tag_has(self.TRISTATE_TAG, item)

    def force_active_parent(self, item):
        # need to recalculate what the parent will be with the new state just set on one its children
        parent = self.parent(item)
        if parent:
            self._set_checkbox_state(parent, self.CHECKED_TAG)

    def _box_click(self, event):
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify("element", x, y)
        if "image" in elem:
            # a box was clicked
            self.trigger_checkbox(single_item=self.identify_row(y))
    
    def trigger_checkbox(self, single_item=None):
        if single_item is None:
            all_items = self.selection()
            if len(all_items) == 0:
                return
        else:
            all_items = [single_item]
        
        for cur_item in all_items:
            if self.tag_has(self.UNCHECKED_TAG, cur_item):
                result_state = self.CHECKED_TAG
            else:
                result_state = self.UNCHECKED_TAG
            self._set_checkbox_state(cur_item, result_state)

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

    def __init__(self, *args, custom_col_data=None, text_field_attr=None, checkbox_attr=None, semantic_id_attr=None, tags_attr=None, req_column_width=None, **kwargs):
        self._custom_col_data = custom_col_data

        self._text_field_attr = text_field_attr
        self._checkbox_attr = checkbox_attr
        self._semantic_id_attr = semantic_id_attr
        self._tags_attr = tags_attr
        self._req_column_width = req_column_width

        kwargs["columns"] = len(self._custom_col_data)
        super().__init__(*args, **kwargs, selectmode="extended")

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

        # special case for required column
        if self._req_column_width is not None:
            self.column("#0", width=self._req_column_width, stretch=tk.NO)

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


class CheckboxLabel(ttk.Frame):
    def __init__(self, *args, text="", toggle_command=None, flip=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._var = tk.BooleanVar()
        self._var.trace("w", self._did_toggle)
        self._checkbox = ttk.Checkbutton(self, variable=self._var)
        self._text_label = ttk.Label(self, text=text)

        if flip:
            self.columnconfigure(0, weight=1)
            self._checkbox.grid(row=0, column=1)
            self._text_label.grid(row=0, column=0, sticky=tk.W)
        else:
            self.columnconfigure(1, weight=1)
            self._checkbox.grid(row=0, column=0)
            self._text_label.grid(row=0, column=1)

        self.toggle_command = toggle_command
        self.bind("<Button-1>", self.toggle_checked)
        self._text_label.bind("<Button-1>", self.toggle_checked)

    def is_checked(self):
        return self._var.get()
    
    def set_checked(self, val):
        self._var.set(val)
    
    def toggle_checked(self, *args, **kwargs):
        self._var.set(not self._var.get())
    
    def _did_toggle(self, *args, **kwargs):
        if self.toggle_command is not None:
            self.toggle_command()
    
    def enable(self):
        self._checkbox.configure(state="normal")
    
    def disable(self):
        self._checkbox.configure(state="disabled")

class SimpleOptionMenu(ttk.Combobox):
    def __init__(self, root, option_list, callback=None, default_val=None, var_name=None, **kwargs):
        self._val = tk.StringVar(name=var_name)
        self.cur_options = option_list

        if default_val is None:
            default_val = option_list[0]
        self._val.set(default_val)

        if callback is not None:
            self._val.trace("w", callback)

        kwargs['state'] = "readonly"
        kwargs['exportselection'] = False
        super().__init__(root, textvariable=self._val, values=option_list, **kwargs)
    
    def enable(self):
        self.configure(state="readonly")
    
    def disable(self):
        self.configure(state="disabled")
    
    def get(self):
        return self._val.get()

    def set(self, val):
        # TODO: should double check to make sure it's valid... what happens if it's not in the option list?
        return self._val.set(val)
    
    def new_values(self, option_list, default_val=None):
        if option_list == self.cur_options:
            if default_val is not None:
                self._val.set(default_val)
            return

        self.cur_options = option_list
        self.config(values=self.cur_options)

        if default_val is None:
            default_val = option_list[0]
        self._val.set(default_val)


class SimpleEntry(ttk.Entry):
    def __init__(self, *args, initial_value="", callback=None, **kwargs):
        self._value = tk.StringVar(value=initial_value)

        super().__init__(*args, **kwargs, textvariable=self._value)
        if callback is not None:
            self._value.trace_add("write", callback)
    
    def get(self):
        return self._value.get()
    
    def set(self, value):
        self._value.set(value)
    
    def enable(self):
        self.configure(state="normal")
    
    def disable(self):
        self.configure(state="disabled")


class AmountEntry(ttk.Frame):
    def __init__(self, *args, callback=None, max_val=None, min_val=None, init_val=None, width=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.max_val = max_val
        self.min_val = min_val

        if init_val is None:
            if min_val is None:
                init_val = "1"
            else:
                init_val = str(min_val)
        
        self._down_button = SimpleButton(self, text="v", command=self._lower_amt, width=1)
        self._down_button.grid(row=0, column=0)
        self._amount = SimpleEntry(self, initial_value=init_val, callback=callback)
        self._amount.grid(row=0, column=1)
        if width is not None:
            self._amount.configure(width=width)
        self._up_button = SimpleButton(self, text="^", command=self._raise_amt, width=1)
        self._up_button.grid(row=0, column=2)
        self._update_buttons()
    
    def _lower_amt(self, *args, **kwargs):
        try:
            val = int(self._amount.get().strip()) - 1
            if self.min_val is not None:
                val = max(val, self.min_val)
            self.set(str(val))
        except Exception:
            pass

    def _raise_amt(self, *args, **kwargs):
        try:
            val = int(self._amount.get().strip()) + 1
            if self.max_val is not None:
                val = min(val, self.max_val)
            self.set(str(val))
        except Exception:
            pass
    
    def get(self):
        return self._amount.get()
    
    def _update_buttons(self):
        if self.get() == str(self.min_val):
            self._down_button.disable()
        else:
            self._down_button.enable()

        if self.get() == str(self.max_val):
            self._up_button.disable()
        else:
            self._up_button.enable()
    
    def set(self, value, update_buttons_only=False):
        try:
            value = int(value)
            if self.min_val is not None:
                value = max(value, self.min_val)
            if self.max_val is not None:
                value = min(value, self.max_val)
        except Exception:
            value = self._amount.get()
        
        self._amount.set(value)
        self._update_buttons()
    
    def enable(self):
        self._up_button.enable()
        self._amount.enable()
        self._down_button.enable()
    
    def disable(self):
        self._up_button.disable()
        self._amount.disable()
        self._down_button.disable()


class SimpleButton(ttk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def enable(self):
        self["state"] = "normal"

    def disable(self):
        self["state"] = "disabled"


class SimpleText(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result

    def enable(self):
        self.configure(state="normal")

    def disable(self):
        self.configure(state="disabled")


class AutoClearingLabel(ttk.Label):
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


class ScrollableFrame(ttk.Frame):
    """
    NOTE: doesn't work, but leaving it here because I don't want to give up on it yet
    might not work though, seems like tkinter doesn't like the concept very much

    Make a frame scrollable with scrollbar on the right.
    After adding or removing widgets to the scrollable frame,
    call the update() method to refresh the scrollable area.
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(parent)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner_frame = ttk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # TODO: is this tag important?
        self.canvas.create_window((4,4), window=self.inner_frame, anchor=tk.NW, tags="self.inner_frame")

        self.canvas.bind('<Configure>', self.on_frame_configure)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class ConfigColorUpdater(ttk.Frame):
    def __init__(self, *args, label_text=None, getter=None, setter=None, callback=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.getter = getter
        self.setter = setter
        self.callback = callback

        self.columnconfigure(0, weight=1, uniform="group")
        self.columnconfigure(1, weight=1, uniform="group")

        self._label = ttk.Label(self, text=label_text)
        self._label.grid(row=0, column=0, padx=10, pady=2, sticky=tk.W)

        self._inner_frame = ttk.Frame(self)
        self._inner_frame.grid(row=0, column=1, sticky=tk.EW)

        self._button = ttk.Button(self._inner_frame, text="Change Color", command=self.change_success_color)
        self._button.grid(row=0, column=1, padx=5, pady=2, sticky=tk.E)
        self._preview = tk.Frame(self._inner_frame, bg=self.getter(), width=20, height=20)
        self._preview.grid(row=0, column=2, padx=5, pady=2, sticky=tk.E)
        self._preview.grid_propagate(0)
    
    def change_success_color(self, *args, **kwargs):
        result = colorchooser.askcolor(color=self.getter())
        if result is not None and result[1] is not None:
            self.setter(result[1])
            self._preview.configure(bg=self.getter())
        
        if self.callback is not None:
            self.callback()
    
    def refresh_color(self, *args, **kwargs):
        self._preview.configure(bg=self.getter())
