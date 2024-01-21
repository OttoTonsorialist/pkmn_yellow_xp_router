import os
import threading

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from gui import custom_components
from gui.popups.base_popup import Popup
from utils.constants import const
from utils.config_manager import config
from utils import io_utils, auto_update

class DataDirConfigWindow(Popup):
    def __init__(self, main_window, restart_callback, *args, first_time_setup=False, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._restart_callback = restart_callback

        self.first_time_setup = first_time_setup
        self._data_dir_changed = False
        self._thread = None
        self._new_app_version = None
        self._new_asset_url = None

        self.padx = 5
        self.pady = 5
        self.app_info_frame = ttk.Frame(self)
        self.app_info_frame.pack(padx=self.padx, pady=(2 * self.pady))
        self.data_location_frame = ttk.Frame(self)
        self.data_location_frame.pack(padx=self.padx, pady=(4 * self.pady, 2 * self.pady))

        self.app_version_label = tk.Label(self.app_info_frame, text="App Version:")
        self.app_version_label.grid(row=0, column=0)
        self.app_version_value = tk.Label(self.app_info_frame, text=const.APP_VERSION)
        self.app_version_value.grid(row=0, column=1)

        self.app_release_date_label = tk.Label(self.app_info_frame, text="Release Date:")
        self.app_release_date_label.grid(row=1, column=0)
        self.app_release_date_value = tk.Label(self.app_info_frame, text=const.APP_RELEASE_DATE)
        self.app_release_date_value.grid(row=1, column=1)

        self.debug_mode_label = tk.Label(self.app_info_frame, text="Debug Mode:")
        self.debug_mode_label.grid(row=2, column=0)
        self.debug_mode_value = tk.BooleanVar()
        self.debug_mode_value.set(config.is_debug_mode())
        self.debug_mode_value.trace("w", self.toggle_debug_mode)
        self.debug_mode_button = ttk.Checkbutton(self.app_info_frame, variable=self.debug_mode_value)
        self.debug_mode_button.grid(row=2, column=1)

        self._windows_label = tk.Label(self.app_info_frame, text="Automatic updates only supported on windows machines")
        self._windows_label.grid(row=5, column=0, columnspan=2, padx=self.padx, pady=(2 * self.pady, self.pady))
        self._latest_version_label = tk.Label(self.app_info_frame, text="Fetching newest version...")
        self._latest_version_label.grid(row=6, column=0, columnspan=2)
        self._check_for_updates_button = custom_components.SimpleButton(self.app_info_frame, text="No Upgrade Needed", command=self._kick_off_auto_update)
        self._check_for_updates_button.grid(row=7, column=0, columnspan=2)
        self._check_for_updates_button.disable()

        self.data_location_value = tk.Label(self.data_location_frame, text=f"Data Location: {config.get_user_data_dir()}")
        self.data_location_value.grid(row=15, column=0, columnspan=2)
        self.data_location_label = custom_components.SimpleButton(self.data_location_frame, text="Open Data Folder", command=self.open_data_location)
        self.data_location_label.grid(row=16, column=0)
        self.data_location_change_button = custom_components.SimpleButton(self.data_location_frame, text="Move Data Location", command=self.change_data_location)
        self.data_location_change_button.grid(row=16, column=1)

        self.app_location_button = custom_components.SimpleButton(self.data_location_frame, text="Open Config/Logs Folder", command=self.open_global_config_location)
        self.app_location_button.grid(row=17, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.close_button = custom_components.SimpleButton(self, text="Close", command=self._final_cleanup)
        self.close_button.pack(padx=self.padx, pady=self.pady)

        self.bind('<Return>', self._final_cleanup)
        self.bind('<Escape>', self._final_cleanup)
        self._thread = threading.Thread(target=self._get_new_updates_info)
        self._thread.start()
    
    def _final_cleanup(self, *args, **kwargs):
        if self.first_time_setup and not self._data_dir_changed:
            io_utils.change_user_data_location(None, config.get_user_data_dir())
        self._thread.join()
        self.close()
    
    def _get_new_updates_info(self, *args, **kwargs):
        self._new_app_version, self._new_asset_url = auto_update.get_new_version_info()
        self._latest_version_label.configure(text=f"Newest Version: {self._new_app_version}")
        if auto_update.is_upgrade_needed(self._new_app_version, const.APP_VERSION):
            self._check_for_updates_button.configure(text="Upgrade")
            self._check_for_updates_button.enable()
    
    def _kick_off_auto_update(self, *args, **kwargs):
        # TODO: fix this to actually work
        global flag_to_auto_update
        flag_to_auto_update = True
        self._thread.join()
        self._restart_callback()

    def open_global_config_location(self, *args, **kwargs):
        io_utils.open_explorer(const.GLOBAL_CONFIG_DIR)

    def open_data_location(self, *args, **kwargs):
        io_utils.open_explorer(config.get_user_data_dir())
    
    def toggle_debug_mode(self, *args, **kwargs):
        config.set_debug_mode(not config.is_debug_mode())

    def change_data_location(self, *args, **kwargs):
        valid_path_found = False
        while not valid_path_found:
            file_result = filedialog.askdirectory(initialdir=config.get_user_data_dir(), mustexist=False)
            if not file_result:
                self.lift()
                return

            new_path = os.path.realpath(file_result)
            if os.path.realpath(const.SOURCE_ROOT_PATH) in new_path:
                messagebox.showerror("Error", "Cannot place the data dir inside the app, as it will be removed during automatic updates")
            else:
                valid_path_found = True

        if io_utils.change_user_data_location(config.get_user_data_dir(), new_path):
            config.set_user_data_dir(new_path)
            self.data_location_value.config(text=new_path)
        else:
            messagebox.showerror("Error", "Failed to change user data location...")

        self.lift()
