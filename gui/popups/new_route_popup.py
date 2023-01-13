import os
import json

import tkinter as tk

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui import custom_components
from pkmn.universal_data_objects import StatBlock
from utils.constants import const
from utils import io_utils
from pkmn.gen_factory import current_gen_info


class NewRouteWindow(Popup):
    def __init__(self, main_window, controller:MainController, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs, width=400)
        self._controller = controller

        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        self.pkmn_version_label = tk.Label(self.controls_frame, text="Pokemon Version:")
        self.pkmn_version_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.pkmn_version = custom_components.SimpleOptionMenu(self.controls_frame, const.VERSION_LIST, callback=self._pkmn_version_callback)
        self.pkmn_version.config(width=20)
        self.pkmn_version.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.solo_selector_label = tk.Label(self.controls_frame, text="Solo Pokemon:")
        self.solo_selector_label.grid(row=1, column=0, padx=self.padx, pady=(4 * self.pady, self.pady))
        self.solo_selector = custom_components.SimpleOptionMenu(self.controls_frame, [const.NO_POKEMON])
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

        self.max_dvs_flag = tk.BooleanVar()
        self.max_dvs_flag.set(True)
        self.max_dvs_flag.trace("w", self._custom_dvs_callback)
        self.custom_dvs_label = tk.Label(self.controls_frame, text="Max DVs?")
        self.custom_dvs_checkbox = tk.Checkbutton(self.controls_frame, variable=self.max_dvs_flag, onvalue=True, offvalue=False)
        self.custom_dvs_label.grid(row=5, column=0, padx=self.padx, pady=(4 * self.pady, self.pady))
        self.custom_dvs_checkbox.grid(row=5, column=1, padx=self.padx, pady=(4 * self.pady, self.pady))

        self.custom_dvs_frame = tk.Frame(self.controls_frame)

        self.custom_dvs_hp_label = tk.Label(self.custom_dvs_frame, text="HP DV:")
        self.custom_dvs_hp_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hp = custom_components.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_hp.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_atk_label = tk.Label(self.custom_dvs_frame, text="Attack DV:")
        self.custom_dvs_atk_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_atk = custom_components.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_atk.grid(row=1, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_def_label = tk.Label(self.custom_dvs_frame, text="Defense DV:")
        self.custom_dvs_def_label.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_def = custom_components.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_def.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spd_label = tk.Label(self.custom_dvs_frame, text="Speed DV:")
        self.custom_dvs_spd_label.grid(row=3, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spd = custom_components.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_spd.grid(row=3, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spc_label = tk.Label(self.custom_dvs_frame, text="Special DV:")
        self.custom_dvs_spc_label.grid(row=4, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spc = custom_components.AmountEntry(self.custom_dvs_frame, min_val=0, max_val=15, init_val=15, callback=self._recalc_hidden_power)
        self.custom_dvs_spc.grid(row=4, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_hidden_power_label = tk.Label(self.custom_dvs_frame, text="Hidden Power:")
        self.custom_dvs_hidden_power_label.grid(row=5, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hidden_power = tk.Label(self.custom_dvs_frame)
        self.custom_dvs_hidden_power.grid(row=5, column=1, padx=self.padx, pady=self.pady)


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
    
    def _recalc_hidden_power(self, *args, **kwargs):
        try:
            hp_type, hp_power = pkmn.specific_gen_info(self.pkmn_version.get()).get_hidden_power(
                StatBlock(
                    int(self.custom_dvs_hp.get()),
                    int(self.custom_dvs_atk.get()),
                    int(self.custom_dvs_def.get()),
                    int(self.custom_dvs_spc.get()),
                    int(self.custom_dvs_spc.get()),
                    int(self.custom_dvs_spd.get())
                )
            )

            if not hp_type:
                self.custom_dvs_hidden_power.configure(text=f"Not supported in gen 1")
            else:
                self.custom_dvs_hidden_power.configure(text=f"{hp_type}: {hp_power}")
        except Exception as e:
            self.custom_dvs_hidden_power.configure(text=f"Failed to calculate, invalid DVs")

    def _pkmn_version_callback(self, *args, **kwargs):
        # now that we've loaded the right version, repopulate the pkmn selector just in case
        temp_gen = pkmn.specific_gen_info(self.pkmn_version.get())
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

    def _pkmn_filter_callback(self, *args, **kwargs):
        self.solo_selector.new_values(pkmn.specific_gen_info(self.pkmn_version.get()).pkmn_db().get_filtered_names(filter_val=self.pkmn_filter.get().strip()))

    def _base_route_filter_callback(self, *args, **kwargs):
        # NOTE: assume the _min_battles_cache is always accurate, and just filter it down as needed
        filter_val = self.min_battles_filter.get().strip().lower()
        new_vals = [x for x in self._min_battles_cache if filter_val in x.lower()]

        if not new_vals:
            new_vals = [const.EMPTY_ROUTE_NAME]

        self.min_battles_selector.new_values(new_vals)
    
    def _custom_dvs_callback(self, *args, **kwargs):
        if not self.max_dvs_flag.get():
            self.custom_dvs_frame.grid(row=5, column=0, columnspan=2)
            self._recalc_hidden_power()
        else:
            self.custom_dvs_frame.grid_forget()
    
    def _get_custom_dvs(self, *args, **kwargs):
        if self.max_dvs_flag.get():
            return None
        
        return {
            const.HP: int(self.custom_dvs_hp.get()),
            const.ATK: int(self.custom_dvs_atk.get()),
            const.DEF: int(self.custom_dvs_def.get()),
            const.SPD: int(self.custom_dvs_spd.get()),
            const.SPC: int(self.custom_dvs_spc.get()),
        }
    
    def create(self, *args, **kwargs):
        selected_base_route = self.min_battles_selector.get()
        if selected_base_route == const.EMPTY_ROUTE_NAME:
            selected_base_route = None
        elif selected_base_route.startswith(const.PRESET_ROUTE_PREFIX):
            temp_gen = pkmn.specific_gen_info(self.pkmn_version.get())
            selected_base_route = os.path.join(temp_gen.min_battles_db().get_dir(), selected_base_route[len(const.PRESET_ROUTE_PREFIX):] + ".json")
        else:
            selected_base_route = io_utils.get_existing_route_path(selected_base_route)
            
        self.close()
        self._controller.create_new_route(
            self.solo_selector.get(),
            selected_base_route,
            self.pkmn_version.get(),
            self._get_custom_dvs()
        )
