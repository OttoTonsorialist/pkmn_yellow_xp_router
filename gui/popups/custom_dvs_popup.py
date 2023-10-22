import tkinter as tk
from tkinter import ttk
import logging

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui import custom_components
from pkmn.universal_data_objects import Nature, StatBlock
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


class CustomDvsWindow(Popup):
    def __init__(self, main_window, controller:MainController, init_dvs:StatBlock, init_ability:str, init_nature:Nature, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs, width=400)
        self._controller = controller

        self.controls_frame = ttk.Frame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        cur_gen = current_gen_info().get_generation()
        if cur_gen > 2:
            dv_max = 31
            dv_text = "IV"
            self.custom_dvs_spc_atk_label = tk.Label(self.controls_frame, text=f"Spc Atk {dv_text}:")
            self.custom_dvs_spc_atk = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=dv_max, init_val=init_dvs.special_attack, callback=self._recalc_hidden_power)
            self.custom_dvs_spc_def_label = tk.Label(self.controls_frame, text=f"Spc Def {dv_text}:")
            self.custom_dvs_spc_def = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=dv_max, init_val=init_dvs.special_attack, callback=self._recalc_hidden_power)
            self.nature_label = tk.Label(self.controls_frame, text="Nature:")
            self._nature_lookup = [str(x) for x in Nature]
            self.nature_vals = custom_components.SimpleOptionMenu(self.controls_frame, self._nature_lookup, default_val=str(init_nature))
            self.ability_label = tk.Label(self.controls_frame, text="Ability:")
            self.ability_vals = custom_components.SimpleOptionMenu(
                self.controls_frame,
                self._controller.get_init_state().solo_pkmn.species_def.abilitiies,
                default_val=init_ability
            )
            self.custom_dvs_hidden_power_label = tk.Label(self.controls_frame, text="Hidden Power:")
            self.custom_dvs_hidden_power = tk.Label(self.controls_frame)
        else:
            dv_text = "DV"
            dv_max = 15
            self.custom_dvs_spc_atk_label = tk.Label(self.controls_frame, text=f"Special {dv_text}:")
            self.custom_dvs_spc_atk = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=dv_max, init_val=init_dvs.special_attack, callback=self._recalc_hidden_power)
            self.custom_dvs_spc_def_label = None
            self.custom_dvs_spc_def = None
            self.nature_label = None
            self._nature_lookup = []
            self.nature_vals = None
            self.ability_label = None
            self.ability_vals = None
            if cur_gen == 2:
                self.custom_dvs_hidden_power_label = tk.Label(self.controls_frame, text="Hidden Power:")
                self.custom_dvs_hidden_power = tk.Label(self.controls_frame)
            else:
                self.custom_dvs_hidden_power_label = None
                self.custom_dvs_hidden_power = None

        self.custom_dvs_hp_label = tk.Label(self.controls_frame, text=f"HP {dv_text}:")
        self.custom_dvs_hp_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hp = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=dv_max, init_val=init_dvs.hp, callback=self._recalc_hidden_power)
        self.custom_dvs_hp.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_atk_label = tk.Label(self.controls_frame, text=f"Attack {dv_text}:")
        self.custom_dvs_atk_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_atk = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=dv_max, init_val=init_dvs.attack, callback=self._recalc_hidden_power)
        self.custom_dvs_atk.grid(row=1, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_def_label = tk.Label(self.controls_frame, text=f"Defense {dv_text}:")
        self.custom_dvs_def_label.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_def = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=dv_max, init_val=init_dvs.defense, callback=self._recalc_hidden_power)
        self.custom_dvs_def.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spd_label = tk.Label(self.controls_frame, text=f"Speed {dv_text}:")
        self.custom_dvs_spd_label.grid(row=3, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spd = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=dv_max, init_val=init_dvs.speed, callback=self._recalc_hidden_power)
        self.custom_dvs_spd.grid(row=3, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spc_atk_label.grid(row=4, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spc_atk.grid(row=4, column=1, padx=self.padx, pady=self.pady)

        if self.custom_dvs_spc_def_label is not None:
            self.custom_dvs_spc_def_label.grid(row=5, column=0, padx=self.padx, pady=self.pady)
        if self.custom_dvs_spc_def is not None:
            self.custom_dvs_spc_def.grid(row=5, column=1, padx=self.padx, pady=self.pady)

        if self.custom_dvs_hidden_power_label is not None:
            self.custom_dvs_hidden_power_label.grid(row=6, column=0, padx=self.padx, pady=self.pady)
        if self.custom_dvs_hidden_power is not None:
            self.custom_dvs_hidden_power.grid(row=6, column=1, padx=self.padx, pady=self.pady)

        if self.nature_label is not None:
            self.nature_label.grid(row=10, column=0, padx=self.padx, pady=self.pady)
        if self.nature_vals is not None:
            self.nature_vals.grid(row=10, column=1, padx=self.padx, pady=self.pady)
        if self.ability_label is not None:
            self.ability_label.grid(row=12, column=0, padx=self.padx, pady=self.pady)
        if self.ability_vals is not None:
            self.ability_vals.grid(row=12, column=1, padx=self.padx, pady=self.pady)

        self.create_button = custom_components.SimpleButton(self.controls_frame, text="Set New DVs", command=self.set_dvs)
        self.create_button.grid(row=30, column=0, padx=self.padx, pady=self.pady)
        self.cancel_button = custom_components.SimpleButton(self.controls_frame, text="Cancel", command=self.close)
        self.cancel_button.grid(row=30, column=1, padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.set_dvs)
        self.bind('<Escape>', self.close)
        self._recalc_hidden_power()
    
    def _recalc_hidden_power(self, *args, **kwargs):
        if self.custom_dvs_hidden_power is None:
            return
        try:
            if self.custom_dvs_spc_def is not None:
                spc_def_stat = self.custom_dvs_spc_def.get()
            else:
                spc_def_stat = self.custom_dvs_spc_atk.get()
            hp_type, hp_power = current_gen_info().get_hidden_power(
                StatBlock(
                    int(self.custom_dvs_hp.get()),
                    int(self.custom_dvs_atk.get()),
                    int(self.custom_dvs_def.get()),
                    int(self.custom_dvs_spc_atk.get()),
                    int(spc_def_stat),
                    int(self.custom_dvs_spd.get())
                )
            )

            if not hp_type:
                self.custom_dvs_hidden_power.configure(text=f"Not supported in gen 1")
            else:
                self.custom_dvs_hidden_power.configure(text=f"{hp_type}: {hp_power}")
        except Exception as e:
            self.custom_dvs_hidden_power.configure(text=f"Failed to calculate, invalid DVs")
            logger.exception("Failed to calculated hidden power")

    def set_dvs(self, *args, **kwargs):
        if self.nature_vals is None:
            new_nature = Nature.HARDY
        else:
            new_nature = Nature(self._nature_lookup.index(self.nature_vals.get()))
        
        if self.ability_vals is None:
            new_ability = ""
        else:
            new_ability = self.ability_vals.get()
        
        if self.custom_dvs_spc_def is not None:
            spc_def_stat = self.custom_dvs_spc_def.get()
        else:
            spc_def_stat = self.custom_dvs_spc_atk.get()

        self._controller.customize_innate_stats(
            StatBlock(
                int(self.custom_dvs_hp.get()),
                int(self.custom_dvs_atk.get()),
                int(self.custom_dvs_def.get()),
                int(self.custom_dvs_spc_atk.get()),
                int(spc_def_stat),
                int(self.custom_dvs_spd.get())
            ),
            new_ability,
            new_nature
        )
        self.close()
