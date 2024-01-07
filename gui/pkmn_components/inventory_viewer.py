import tkinter as tk
from tkinter import ttk
import logging
from typing import List

from routing import state_objects

logger = logging.getLogger(__name__)


class InventoryViewer(ttk.Frame):
    def __init__(self, *args, style_prefix="Inventory", **kwargs):
        kwargs["style"] = f"{style_prefix}.TFrame"
        super().__init__(*args, **kwargs)
        self.config(height=150, width=250)

        self._money_label = ttk.Label(self, text="Current Money: ", style=f"Header.TLabel", padding=(0, 2, 0, 2))
        self._money_label.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        self._all_items:List[ttk.Label] = []

        # HARDCODED for now: only support showing 20 items...
        self.max_render_size = 20
        split_point = self.max_render_size // 2
        for i in range(self.max_render_size):
            cur_item_label = ttk.Label(self, text=f"# {i:0>2}: ", anchor=tk.W, width=20, style=f"{style_prefix}.TLabel")
            cur_item_label.grid(row=(i % split_point) + 1, column=i // split_point, sticky=tk.W)
            self._all_items.append(cur_item_label)
    
    def set_inventory(self, inventory:state_objects.Inventory):
        self._money_label.config(text=f"Current Money: {inventory.cur_money}")

        idx = -1
        too_many_items = len(inventory.cur_items) > self.max_render_size

        for idx in range(min(len(inventory.cur_items), self.max_render_size)):
            cur_item = inventory.cur_items[idx]
            if too_many_items and idx == (self.max_render_size - 1):
                self._all_items[idx].config(text=f"# {idx:0>2}+: More items...")
            else:
                self._all_items[idx].config(text=f"# {idx:0>2}: {cur_item.num}x {cur_item.base_item.name}")
        
        for missing_idx in range(idx + 1, self.max_render_size):
            self._all_items[missing_idx].config(text=f"# {missing_idx:0>2}:")