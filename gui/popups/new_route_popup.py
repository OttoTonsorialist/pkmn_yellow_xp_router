import os
import json

import tkinter as tk
from tkinter import ttk

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui.popups.custom_dvs_popup import CustomDVsFrame
from gui import custom_components
from utils.constants import const
from utils import io_utils
from pkmn.gen_factory import _gen_factory as gen_factory, current_gen_info


class NewRouteWindow(Popup):
    def __init__(self, main_window, controller:MainController, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs, width=400)
        self._controller = controller

        self.controls_frame = ttk.Frame(self)
        self.controls_frame.grid()
        self.padx = 5
        self.pady = 5

        self.pkmn_version_label = tk.Label(self.controls_frame, text="Pokemon Version:")
        self.pkmn_version_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.pkmn_version = custom_components.SimpleOptionMenu(self.controls_frame, gen_factory.get_gen_names(), callback=self._pkmn_version_callback)
        self.pkmn_version.config(width=20)
        self.pkmn_version.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.solo_selector_label = tk.Label(self.controls_frame, text="Solo Pokemon:")
        self.solo_selector_label.grid(row=1, column=0, padx=self.padx, pady=(4 * self.pady, self.pady))
        self.solo_selector = custom_components.SimpleOptionMenu(self.controls_frame, [const.NO_POKEMON], callback=self._pkmn_selector_callback)
        self.solo_selector.config(width=20)
        self.solo_selector.grid(row=1, column=1, padx=self.padx, pady=(4 * self.pady, self.pady))

        self.pkmn_filter_label = tk.Label(self.controls_frame, text="Solo Pokemon Filter:")
        self.pkmn_filter_label.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.pkmn_filter = custom_components.SimpleEntry(self.controls_frame, callback=self._pkmn_filter_callback)
        self.pkmn_filter.config(width=30)
        self.pkmn_filter.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        # need to create a local cache of all min battles due to all the version switching we're going to do
        self._min_battles_cache = [const.EMPTY_ROUTE_NAME]
        self.min_battles_selector_label = tk.Label(self.controls_frame, text="Base Route:")
        self.min_battles_selector_label.grid(row=3, column=0, padx=self.padx, pady=(4 * self.pady, self.pady))
        self.min_battles_selector = custom_components.SimpleOptionMenu(self.controls_frame, self._min_battles_cache)
        self.min_battles_selector.grid(row=3, column=1, padx=self.padx, pady=(4 * self.pady, self.pady))

        self.min_battles_filter_label = tk.Label(self.controls_frame, text="Base Route Filter:")
        self.min_battles_filter_label.grid(row=4, column=0, padx=self.padx, pady=self.pady)
        self.min_battles_filter = custom_components.SimpleEntry(self.controls_frame, callback=self._base_route_filter_callback)
        self.min_battles_filter.config(width=30)
        self.min_battles_filter.grid(row=4, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_frame = CustomDVsFrame(None, self, target_game=current_gen_info())
        self.custom_dvs_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=self.padx, pady=self.pady)

        self.warning_label = tk.Label(self.controls_frame, text="WARNING: Any unsaved changes in your current route\nwill be lost when creating a new route!", justify=tk.CENTER, anchor=tk.CENTER)
        self.warning_label.grid(row=29, column=0, columnspan=2, sticky=tk.EW, padx=self.padx, pady=self.pady)

        self.create_button = custom_components.SimpleButton(self.controls_frame, text="Create Route", command=self.create)
        self.create_button.grid(row=30, column=0, padx=self.padx, pady=self.pady)
        self.cancel_button = custom_components.SimpleButton(self.controls_frame, text="Cancel", command=self.close)
        self.cancel_button.grid(row=30, column=1, padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.create)
        self.bind('<Escape>', self.close)
        self._pkmn_version_callback()
        self.pkmn_filter.focus()
    
    def _pkmn_version_callback(self, *args, **kwargs):
        # now that we've loaded the right version, repopulate the pkmn selector just in case
        temp_gen = gen_factory.get_specific_version(self.pkmn_version.get())
        self.solo_selector.new_values(temp_gen.pkmn_db().get_filtered_names(filter_val=self.pkmn_filter.get().strip()))

        all_routes = [const.EMPTY_ROUTE_NAME]
        for preset_route_name in temp_gen.min_battles_db().data:
            all_routes.append(const.PRESET_ROUTE_PREFIX + preset_route_name)

        for test_route in io_utils.get_existing_route_names():
            try:
                with open(io_utils.get_existing_route_path(test_route), 'r') as f:
                    raw = json.load(f)
                    if raw[const.PKMN_VERSION_KEY] == self.pkmn_version.get():
                        all_routes.append(test_route)
            except Exception as e:
                pass

        self._min_battles_cache = all_routes
        self._base_route_filter_callback()
        self.custom_dvs_frame.config_for_target_game_and_mon(temp_gen, temp_gen.pkmn_db().get_pkmn(self.solo_selector.get()))

    def _pkmn_filter_callback(self, *args, **kwargs):
        self.solo_selector.new_values(gen_factory.get_specific_version(self.pkmn_version.get()).pkmn_db().get_filtered_names(filter_val=self.pkmn_filter.get().strip()))

    def _pkmn_selector_callback(self, *args, **kwargs):
        print(f"ollo!")
        temp_gen = gen_factory.get_specific_version(self.pkmn_version.get())
        self.custom_dvs_frame.config_for_target_game_and_mon(temp_gen, temp_gen.pkmn_db().get_pkmn(self.solo_selector.get()))

    def _base_route_filter_callback(self, *args, **kwargs):
        # NOTE: assume the _min_battles_cache is always accurate, and just filter it down as needed
        filter_val = self.min_battles_filter.get().strip().lower()
        new_vals = [x for x in self._min_battles_cache if filter_val in x.lower()]

        if not new_vals:
            new_vals = [const.EMPTY_ROUTE_NAME]

        self.min_battles_selector.new_values(new_vals)
    
    def create(self, *args, **kwargs):
        selected_base_route = self.min_battles_selector.get()
        if selected_base_route == const.EMPTY_ROUTE_NAME:
            selected_base_route = None
        elif selected_base_route.startswith(const.PRESET_ROUTE_PREFIX):
            temp_gen = gen_factory.get_specific_version(self.pkmn_version.get())
            selected_base_route = os.path.join(temp_gen.min_battles_db().get_dir(), selected_base_route[len(const.PRESET_ROUTE_PREFIX):] + ".json")
        else:
            selected_base_route = io_utils.get_existing_route_path(selected_base_route)
            
        custom_dvs, custom_ability_idx, custom_nature = self.custom_dvs_frame.get_dvs()
        self.close()
        self._controller.create_new_route(
            self.solo_selector.get(),
            selected_base_route,
            self.pkmn_version.get(),
            custom_dvs=custom_dvs,
            custom_ability_idx=custom_ability_idx,
            custom_nature=custom_nature
        )
