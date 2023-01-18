import tkinter as tk
from controllers.main_controller import MainController

from gui import custom_components
from gui.popups.base_popup import Popup
from utils import io_utils
from pkmn.gen_factory import _gen_factory as gen_factory

class CustomGenWindow(Popup):
    def __init__(self, main_window, controller:MainController, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._controller = controller
        self.padx = 5
        self.pady = 5
        self.new_version_frame = tk.Frame(self)
        self.new_version_frame.pack(padx=self.padx, pady=(2 * self.pady))

        self.instructions_label_1 = tk.Label(self.new_version_frame, text="Custom Gen Instructions:")
        self.instructions_label_1.grid(row=0, column=0, columnspan=2)
        instructions = """
Create a custom gen when you want to play a romhack, or a modified
version of an official game (e.g. hacking in a pokemon from a newer gen).
A custom gen will re-use all the damage calculations and mechanics
from the base official generation, but want to route with new or changed content.

Creating a custom gen will copy all the information for the official gen
into a new folder. Once created, click on the button below to open that
location, and then modify the files as necessary.

The application loads all custom gens on startup, so when you modify
the custom gen, you must restart the app before those changes will be recognized.

NOTE: All custom gens are validated on app startup. If any errors are detected,
you will get a pop-up.  The app will still work fine,
but any custom gens with errors detected will not be loaded

"""
        self.instructions_label_1 = tk.Label(self.new_version_frame, text=instructions)
        self.instructions_label_1.grid(row=1, column=0, columnspan=2)

        self.base_version_label = tk.Label(self.new_version_frame, text="Base Version:")
        self.base_version_label.grid(row=11, column=0)
        self.base_version_value = custom_components.SimpleOptionMenu(self.new_version_frame, option_list=gen_factory.get_gen_names(real_gens=True, custom_gens=False))
        self.base_version_value.grid(row=11, column=1)

        self.custom_name_label = tk.Label(self.new_version_frame, text="Custom Version Name:")
        self.custom_name_label.grid(row=12, column=0, pady=2)
        self.custom_name_value = custom_components.SimpleEntry(self.new_version_frame, callback=self.on_custom_name_change)
        self.custom_name_value.grid(row=12, column=1, pady=2)

        self.custom_create_button = custom_components.SimpleButton(self.new_version_frame, text="Create Custom Version", command=self.create_custom_gen)
        self.custom_create_button.grid(row=17, column=0, columnspan=2, pady=2)
        self.custom_create_button.disable()

        # dynamic stuff
        self.cur_custom_gens_frame = tk.Frame(self)
        self.cur_custom_gens_frame.pack(padx=self.padx, pady=(4 * self.pady, 2 * self.pady))
        self.loaded_gens_label = tk.Label(self.cur_custom_gens_frame, text="All Custom Gens")
        self.loaded_gens_label.grid(row=0, column=0, columnspan=2)
        self._dynamic_frame_contents = []
        self._populate_custom_gens()

        self.close_button = custom_components.SimpleButton(self, text="Close", command=self.close)
        self.close_button.pack(padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.create_custom_gen)
        self.bind('<Escape>', self.close)
    
    def _populate_custom_gens(self):
        for to_remove in self._dynamic_frame_contents:
            to_remove.grid_forget()
        
        self._dynamic_frame_contents = []
        for cur_idx, (cur_path, cur_base_version, cur_custom_gen_name) in enumerate(gen_factory.get_all_custom_gen_info()):
            cur_label = tk.Label(self.cur_custom_gens_frame, text=f"{cur_custom_gen_name} ({cur_base_version})")
            cur_label.grid(row=cur_idx + 1, column=0, sticky=tk.W)
            self._dynamic_frame_contents.append(cur_label)

            cur_button = tk.Button(self.cur_custom_gens_frame, text="Open Custom Gen", command=self.curry_open_dialog(cur_path))
            cur_button.grid(row=cur_idx + 1, column=1)
            self._dynamic_frame_contents.append(cur_button)
    
    def on_custom_name_change(self, *args, **kwargs):
        if self._verify_custom_gen_name(self.custom_name_value.get()):
            self.custom_create_button.enable()
        else:
            self.custom_create_button.disable()
    
    def _verify_custom_gen_name(self, name):
        if not name:
            return False
        
        return name not in gen_factory.get_gen_names(real_gens=True, custom_gens=True)
    
    def create_custom_gen(self, *args, **kwargs):
        new_name = self.custom_name_value.get()
        if not self._verify_custom_gen_name(new_name):
            return
        
        self._controller.create_custom_version(self.base_version_value.get(), new_name)
        self._populate_custom_gens()
    
    def curry_open_dialog(self, path_to_open):
        def inner(*args, **kwargs):
            io_utils.open_explorer(path_to_open)
        
        return inner
