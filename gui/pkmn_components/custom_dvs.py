import tkinter as tk
from tkinter import ttk
import logging
from typing import Tuple

from gui import custom_components
from pkmn.pkmn_info import CurrentGen
from pkmn.universal_data_objects import Nature, PokemonSpecies, StatBlock
from pkmn.gen_factory import current_gen_info

logger = logging.getLogger(__name__)


class CustomDVsFrame(ttk.Frame):
    def __init__(self, target_mon:PokemonSpecies, *args, target_game:CurrentGen=None, init_dvs:StatBlock=None, init_ability:str=None, init_nature:Nature=None, **kwargs):
        super().__init__(*args, **kwargs)
        # will be overwritten later by config function that runs at the end of constructor
        self._target_game = None

        self.controls_frame = ttk.Frame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        self.custom_dvs_hp_label = tk.Label(self.controls_frame, text=f"HP DV:")
        self.custom_dvs_hp = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=15, callback=self.recalc_hidden_power)
        self.custom_dvs_atk_label = tk.Label(self.controls_frame, text=f"Attack DV:")
        self.custom_dvs_atk = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=15, callback=self.recalc_hidden_power)
        self.custom_dvs_def_label = tk.Label(self.controls_frame, text=f"Defense DV:")
        self.custom_dvs_def = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=15, callback=self.recalc_hidden_power)
        self.custom_dvs_spd_label = tk.Label(self.controls_frame, text=f"Speed DV:")
        self.custom_dvs_spd = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=15, callback=self.recalc_hidden_power)
        self.custom_dvs_spc_atk_label = tk.Label(self.controls_frame, text=f"Special DV:")
        self.custom_dvs_spc_atk = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=15, init_val=15, callback=self.recalc_hidden_power)
        self.custom_dvs_spc_def_label = None
        self.custom_dvs_spc_def = None
        self.nature_label = None
        self._nature_lookup = []
        self.nature_vals = None
        self.ability_label = None
        self.ability_vals = None
        self.hidden_power_label = None
        self.hidden_power = None

        if target_game is None:
            target_game = current_gen_info()

        self.config_for_target_game_and_mon(
            target_game,
            target_mon,
            init_dvs=init_dvs,
            init_ability=init_ability,
            init_nature=init_nature,
        )


    
    def config_for_target_game_and_mon(self, target_game:CurrentGen, target_mon:PokemonSpecies, init_dvs:StatBlock=None, init_ability:str=None, init_nature:Nature=None):
        logger.info(f"configuring for mon: {target_mon.name if target_mon is not None else target_mon}")
        self._target_game = target_game
        cur_gen = self._target_game.get_generation()

        if init_dvs is None:
            if cur_gen <= 2:
                max_dv = 15
            else:
                max_dv = 31

            init_dvs = self._target_game.make_stat_block(max_dv, max_dv, max_dv, max_dv, max_dv, max_dv)
        
        if init_ability is None and cur_gen >= 3:
            if target_mon is None:
                init_ability = ""
            else:
                init_ability = target_mon.abilitiies[0]
        
        if init_nature is None and cur_gen >= 3:
            init_nature = Nature.HARDY

        if cur_gen > 2:
            dv_max = 31
            dv_text = "IV"
            self._nature_lookup = [str(x) for x in Nature]

            # these may not exist, so create them if necessary
            if self.custom_dvs_spc_def_label is None:
                self.custom_dvs_spc_def_label = tk.Label(self.controls_frame)
            if self.custom_dvs_spc_def is None:
                self.custom_dvs_spc_def = custom_components.AmountEntry(self.controls_frame, min_val=0, max_val=dv_max, callback=self.recalc_hidden_power)
            if self.nature_label is None:
                self.nature_label = tk.Label(self.controls_frame, text="Nature:")
            if self.nature_vals is None:
                self.nature_vals = custom_components.SimpleOptionMenu(self.controls_frame, self._nature_lookup, default_val=str(init_nature))
            if self.ability_label is None:
                self.ability_label = tk.Label(self.controls_frame, text="Ability:")
            if self.ability_vals is None:
                ability_list = target_mon.abilitiies if target_mon is not None else []
                self.ability_vals = custom_components.SimpleOptionMenu(
                    self.controls_frame,
                    ability_list,
                    default_val=init_ability
                )
            else:
                ability_list = target_mon.abilitiies if target_mon is not None else [""]
                self.ability_vals.new_values(ability_list)
            if self.hidden_power_label is None:
                self.hidden_power_label = tk.Label(self.controls_frame, text="Hidden Power:")
            if self.hidden_power is None:
                self.hidden_power = tk.Label(self.controls_frame)


            self.custom_dvs_hp_label.configure(text=f"HP {dv_text}:")
            self.custom_dvs_hp.max_val = dv_max
            self.custom_dvs_hp.set(init_dvs.hp)
            self.custom_dvs_atk_label.configure(text=f"Attack {dv_text}:")
            self.custom_dvs_atk.max_val = dv_max
            self.custom_dvs_atk.set(init_dvs.attack)
            self.custom_dvs_def_label.configure(text=f"Defense {dv_text}:")
            self.custom_dvs_def.max_val = dv_max
            self.custom_dvs_def.set(init_dvs.defense)
            self.custom_dvs_spd_label.configure(text=f"Speed {dv_text}:")
            self.custom_dvs_spd.max_val = dv_max
            self.custom_dvs_spd.set(init_dvs.speed)
            self.custom_dvs_spc_atk_label.configure(text=f"Special Attack {dv_text}:")
            self.custom_dvs_spc_atk.max_val = dv_max
            self.custom_dvs_spc_atk.set(init_dvs.special_attack)
            self.custom_dvs_spc_def_label.configure(text=f"Special Defense {dv_text}:")
            self.custom_dvs_spc_def.max_val = dv_max
            self.custom_dvs_spc_def.set(init_dvs.special_defense)
        else:
            dv_text = "DV"
            dv_max = 15
            self._nature_lookup = []

            if self.custom_dvs_spc_def_label is not None:
                self.custom_dvs_spc_def_label.grid_forget()
                self.custom_dvs_spc_def_label = None
            if self.custom_dvs_spc_def is not None:
                self.custom_dvs_spc_def.grid_forget()
                self.custom_dvs_spc_def = None
            if self.nature_label is not None:
                self.nature_label.grid_forget()
                self.nature_label = None
            if self.nature_vals is not None:
                self.nature_vals.grid_forget()
                self.nature_vals = None
            if self.ability_label is not None:
                self.ability_label.grid_forget()
                self.ability_label = None
            if self.ability_vals is not None:
                self.ability_vals.grid_forget()
                self.ability_vals = None
            if cur_gen == 1:
                if self.hidden_power_label is not None:
                    self.hidden_power_label.grid_forget()
                    self.hidden_power_label = None
                if self.hidden_power is not None:
                    self.hidden_power.grid_forget()
                    self.hidden_power = None
            elif cur_gen == 2:
                if self.hidden_power_label is None:
                    self.hidden_power_label = tk.Label(self.controls_frame, text="Hidden Power:")
                if self.hidden_power is None:
                    self.hidden_power = tk.Label(self.controls_frame)

            self.custom_dvs_hp_label.configure(text=f"HP {dv_text}:")
            self.custom_dvs_hp.max_val = dv_max
            self.custom_dvs_hp.set(init_dvs.hp)
            self.custom_dvs_atk_label.configure(text=f"Attack {dv_text}:")
            self.custom_dvs_atk.max_val = dv_max
            self.custom_dvs_atk.set(init_dvs.attack)
            self.custom_dvs_def_label.configure(text=f"Defense {dv_text}:")
            self.custom_dvs_def.max_val = dv_max
            self.custom_dvs_def.set(init_dvs.defense)
            self.custom_dvs_spd_label.configure(text=f"Speed {dv_text}:")
            self.custom_dvs_spd.max_val = dv_max
            self.custom_dvs_spd.set(init_dvs.speed)
            self.custom_dvs_spc_atk_label.configure(text=f"Special {dv_text}:")
            self.custom_dvs_spc_atk.max_val = dv_max
            self.custom_dvs_spc_atk.set(init_dvs.special_attack)

        self.custom_dvs_hp_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_hp.grid(row=0, column=1, padx=self.padx, pady=self.pady)
        self.custom_dvs_atk_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_atk.grid(row=1, column=1, padx=self.padx, pady=self.pady)
        self.custom_dvs_def_label.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_def.grid(row=2, column=1, padx=self.padx, pady=self.pady)
        self.custom_dvs_spd_label.grid(row=3, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spd.grid(row=3, column=1, padx=self.padx, pady=self.pady)
        self.custom_dvs_spc_atk_label.grid(row=4, column=0, padx=self.padx, pady=self.pady)
        self.custom_dvs_spc_atk.grid(row=4, column=1, padx=self.padx, pady=self.pady)
        if self.custom_dvs_spc_def_label is not None:
            self.custom_dvs_spc_def_label.grid(row=5, column=0, padx=self.padx, pady=self.pady)
        if self.custom_dvs_spc_def is not None:
            self.custom_dvs_spc_def.grid(row=5, column=1, padx=self.padx, pady=self.pady)

        if self.hidden_power_label is not None:
            self.hidden_power_label.grid(row=6, column=0, padx=self.padx, pady=self.pady)
        if self.hidden_power is not None:
            self.hidden_power.grid(row=6, column=1, padx=self.padx, pady=self.pady)

        if self.nature_label is not None:
            self.nature_label.grid(row=10, column=0, padx=self.padx, pady=self.pady)
        if self.nature_vals is not None:
            self.nature_vals.grid(row=10, column=1, padx=self.padx, pady=self.pady)
        if self.ability_label is not None:
            self.ability_label.grid(row=12, column=0, padx=self.padx, pady=self.pady)
        if self.ability_vals is not None:
            self.ability_vals.grid(row=12, column=1, padx=self.padx, pady=self.pady)


    def recalc_hidden_power(self, *args, **kwargs):
        if self.hidden_power is None:
            return
        try:
            if self.custom_dvs_spc_def is not None:
                spc_def_stat = self.custom_dvs_spc_def.get()
            else:
                spc_def_stat = self.custom_dvs_spc_atk.get()
            hp_type, hp_power = self._target_game.get_hidden_power(
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
                self.hidden_power.configure(text=f"Not supported in gen 1")
            else:
                self.hidden_power.configure(text=f"{hp_type}: {hp_power}")
        except Exception as e:
            self.hidden_power.configure(text=f"Failed to calculate, invalid DVs")
            logger.exception("Failed to calculated hidden power")

    def get_dvs(self, *args, **kwargs) -> Tuple[StatBlock, str, Nature]:
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

        return(
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