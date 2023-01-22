import logging

import tkinter as tk
import customtkinter as ctk
from controllers.main_controller import MainController

from gui import custom_components

from utils.constants import const
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


class RouteSearch(ctk.CTkFrame):
    def __init__(self, controller:MainController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._controller:MainController = controller

        self.padx = 5
        self.pady = 1

        self._filter_vals = []
        self._filter_components = []

        num_filters_per_row = 5
        for cur_idx, event_type in enumerate(const.ROUTE_EVENT_TYPES):
            cur_row = cur_idx // num_filters_per_row
            cur_col = (cur_idx % num_filters_per_row) * 2

            cur_checkbox = custom_components.CheckboxLabel(self, text=event_type, toggle_command=self.curry_filter_callback(event_type))
            cur_checkbox.grid(row=cur_row, column=cur_col, padx=self.padx, pady=self.pady, sticky=tk.W)
            self._filter_components.append(cur_checkbox)

        """
        for cur_idx in range(num_filters_per_row):
            self.columnconfigure((2 * cur_idx) + 1, weight=1)
            """
        
        row_idx = len(const.ROUTE_EVENT_TYPES) + 1
        self.reset_button = custom_components.SimpleButton(self, text="Reset All Filters", command=self.reset_all_filters)
        self.reset_button.grid(row=row_idx, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)

        self.search_label = ctk.CTkLabel(self, text="Search:")
        self.search_label.grid(row=row_idx, column=2, padx=self.padx, pady=self.pady, sticky=tk.W)

        self.search_val = custom_components.SimpleEntry(self, callback=self.search_callback)
        self.search_val.grid(row=row_idx, column=4, padx=self.padx, pady=self.pady, sticky=tk.EW, columnspan=3)
    
    def reset_all_filters(self, *args, **kwargs):
        for cur_checkbox in self._filter_components:
            cur_checkbox:custom_components.CheckboxLabel
            if cur_checkbox.is_checked():
                cur_checkbox.toggle_checked()

        self.search_val.set("")

    def search_callback(self, *args, **kwargs):
        self._controller.set_route_search(self.search_val.get())

    def curry_filter_callback(self, string_val):
        def inner(*args, **kwargs):
            if string_val in self._filter_vals:
                self._filter_vals.remove(string_val)
            else:
                self._filter_vals.append(string_val)

            self._controller.set_route_filter_types(self._filter_vals)
        
        return inner
