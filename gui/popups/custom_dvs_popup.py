import tkinter as tk
import customtkinter as ctk

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui import custom_components
from pkmn.universal_data_objects import StatBlock
from pkmn.gen_factory import current_gen_info


class CustomDvsWindow(Popup):
    def __init__(self, main_window, controller:MainController, init_dvs:StatBlock, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs, width=400)
        self._controller = controller

        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        self.custom_dvs_hp_label = ctk.CTkLabel(self.controls_frame, text="HP DV:")
        self.custom_dvs_hp_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hp = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.hp, callback=self._recalc_hidden_power)
        self.custom_dvs_hp.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_atk_label = ctk.CTkLabel(self.controls_frame, text="Attack DV:")
        self.custom_dvs_atk_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_atk = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.attack, callback=self._recalc_hidden_power)
        self.custom_dvs_atk.grid(row=1, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_def_label = ctk.CTkLabel(self.controls_frame, text="Defense DV:")
        self.custom_dvs_def_label.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_def = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.defense, callback=self._recalc_hidden_power)
        self.custom_dvs_def.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spd_label = ctk.CTkLabel(self.controls_frame, text="Speed DV:")
        self.custom_dvs_spd_label.grid(row=3, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spd = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.speed, callback=self._recalc_hidden_power)
        self.custom_dvs_spd.grid(row=3, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_spc_label = ctk.CTkLabel(self.controls_frame, text="Special DV:")
        self.custom_dvs_spc_label.grid(row=4, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spc = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=init_dvs.special_attack, callback=self._recalc_hidden_power)
        self.custom_dvs_spc.grid(row=4, column=1, padx=self.padx, pady=self.pady)

        self.custom_dvs_hidden_power_label = ctk.CTkLabel(self.controls_frame, text="Hidden Power:")
        self.custom_dvs_hidden_power_label.grid(row=5, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hidden_power = ctk.CTkLabel(self.controls_frame)
        self.custom_dvs_hidden_power.grid(row=5, column=1, padx=self.padx, pady=self.pady)


        self.create_button = custom_components.SimpleButton(self.controls_frame, text="Set New DVs", command=self.set_dvs)
        self.create_button.grid(row=30, column=0, padx=self.padx, pady=self.pady)
        self.cancel_button = custom_components.SimpleButton(self.controls_frame, text="Cancel", command=self.close)
        self.cancel_button.grid(row=30, column=1, padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.set_dvs)
        self.bind('<Escape>', self.close)
        self._recalc_hidden_power()
    
    def _recalc_hidden_power(self, *args, **kwargs):
        try:
            hp_type, hp_power = current_gen_info().get_hidden_power(
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

    def _get_custom_dvs(self, *args, **kwargs):
        return StatBlock(
            int(self.custom_dvs_hp.get()),
            int(self.custom_dvs_atk.get()),
            int(self.custom_dvs_def.get()),
            int(self.custom_dvs_spc.get()),
            int(self.custom_dvs_spc.get()),
            int(self.custom_dvs_spd.get())
        )
    
    def set_dvs(self, *args, **kwargs):
        self._controller.customize_dvs(
            StatBlock(
                int(self.custom_dvs_hp.get()),
                int(self.custom_dvs_atk.get()),
                int(self.custom_dvs_def.get()),
                int(self.custom_dvs_spc.get()),
                int(self.custom_dvs_spc.get()),
                int(self.custom_dvs_spd.get())
            )
        )
        self.close()
