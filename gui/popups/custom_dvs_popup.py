from tkinter import ttk
import logging

from controllers.main_controller import MainController
from gui.pkmn_components.custom_dvs import CustomDVsFrame
from gui.popups.base_popup import Popup
from gui import custom_components
from pkmn.gen_factory import current_gen_info
from pkmn.universal_data_objects import Nature, StatBlock

logger = logging.getLogger(__name__)


class CustomDvsWindow(Popup):
    def __init__(self, main_window, controller:MainController, init_dvs:StatBlock, init_ability_idx:int, init_nature:Nature, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs, width=400)
        self._controller = controller
        self._dvs_frame = CustomDVsFrame(
            self._controller.get_init_state().solo_pkmn.species_def,
            self,
            target_game=current_gen_info(),
            init_dvs=init_dvs,
            init_ability_idx=init_ability_idx,
            init_nature=init_nature
        )
        self._dvs_frame.pack()

        self._buttons_frame = ttk.Frame(self)
        self._buttons_frame.pack()

        self.create_button = custom_components.SimpleButton(self._buttons_frame, text="Set New DVs", command=self.set_dvs)
        self.create_button.grid(row=30, column=0, padx=5, pady=5)
        self.cancel_button = custom_components.SimpleButton(self._buttons_frame, text="Cancel", command=self.close)
        self.cancel_button.grid(row=30, column=1, padx=5, pady=5)

        self.bind('<Return>', self.set_dvs)
        self.bind('<Escape>', self.close)
        self._dvs_frame.recalc_hidden_power()
    
    def set_dvs(self, *args, **kwargs):
        dvs, ability_idx, nature = self._dvs_frame.get_dvs()
        self._controller.customize_innate_stats(dvs, ability_idx, nature)
        self.close()
