import tkinter as tk
from tkinter import ttk
import tkinter.font
import logging
from gui.pkmn_components.stat_column import StatColumn

from pkmn.gen_factory import current_gen_info
from pkmn import universal_data_objects

logger = logging.getLogger(__name__)



class PkmnViewer(ttk.Frame):
    def __init__(self, *args, stats_only=False, font_size=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.stats_only = stats_only
        self.config(height=150)

        font_to_use = tkinter.font.nametofont("TkDefaultFont")
        if font_size is not None:
            font_to_use = (font_to_use.name, font_size)

        self.stat_width = 4
        self.move_width = 11

        self._name_value = ttk.Label(self, style="Header.TLabel", font=font_to_use, padding=(0, 2, 0, 2))
        self._name_value.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        self._held_item = ttk.Label(self, style="Header.TLabel", font=font_to_use)
        self._ability = ttk.Label(self, style="Header.TLabel", font=font_to_use)

        self.stat_column = StatColumn(self, val_width=self.stat_width, num_rows=6, style_prefix="Secondary", font=font_to_use)
        self.stat_column.set_labels(["HP:", "Attack:", "Defense:", "Spc Atk:", "Spc Def:", "Speed:"])
        self.stat_column.set_header("")
        self.stat_column.grid(row=5, column=0, sticky=tk.W)

        self.move_column = StatColumn(self, val_width=self.move_width, num_rows=6, font=font_to_use)
        self.move_column.set_labels(["Lv:", "Exp:", "Move 1:", "Move 2:", "Move 3:", "Move 4:"])
        self.move_column.set_header("")

        if not self.stats_only:
            self.move_column.grid(row=5, column=1, sticky=tk.E)


    def set_pkmn(self, pkmn:universal_data_objects.EnemyPkmn, badges:universal_data_objects.BadgeList=None, speed_style=None):
        if speed_style is None:
            speed_style = "Secondary"
        
        self._name_value.config(text=pkmn.name)

        self._ability.config(text=f"{pkmn.ability} ({pkmn.nature})")
        if current_gen_info().get_generation() >= 3:
            self._ability.grid(row=2, column=0, columnspan=2, sticky=tk.EW)
        else:
            self._ability.grid_forget()

        self._held_item.config(text=f"Held Item: {pkmn.held_item}")

        if current_gen_info().get_generation() >= 2:
            self._held_item.grid(row=3, column=0, columnspan=2, sticky=tk.EW)
        else:
            self._held_item.grid_forget()

        attack_val = str(pkmn.cur_stats.attack)
        if badges is not None and badges.is_attack_boosted():
            attack_val = "*" + attack_val

        defense_val = str(pkmn.cur_stats.defense)
        if badges is not None and badges.is_defense_boosted():
            defense_val = "*" + defense_val

        spa_val = str(pkmn.cur_stats.special_attack)
        if badges is not None and badges.is_special_attack_boosted():
            spa_val = "*" + spa_val

        spd_val = str(pkmn.cur_stats.special_defense)
        if badges is not None and badges.is_special_defense_boosted():
            if current_gen_info().get_generation() == 2:
                unboosted_spa = pkmn.base_stats.calc_level_stats(
                    pkmn.level,
                    pkmn.dvs,
                    pkmn.stat_xp,
                    current_gen_info().make_badge_list(),
                    pkmn.nature,
                    ""
                ).special_attack
                if not pkmn.cur_stats.should_ignore_spd_badge_boost(unboosted_spa):
                    spd_val = "*" + spd_val
            else:
                spd_val = "*" + spd_val

        speed_val = str(pkmn.cur_stats.speed)
        if badges is not None and badges.is_speed_boosted():
            speed_val = "*" + speed_val
        
        self.stat_column.set_values(
            [str(pkmn.cur_stats.hp), attack_val, defense_val, spa_val, spd_val, speed_val],
            style_iterable=[None, None, None, None, None, speed_style]
        )

        move_list = [x for x in pkmn.move_list]
        for move_idx in range(len(move_list)):
            if move_list[move_idx] is None:
                move_list[move_idx] = ""
        self.move_column.set_values([str(pkmn.level), str(pkmn.xp)] + move_list)