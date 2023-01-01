import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui import custom_components
from utils.config_manager import config
from utils import route_one_utils



class RouteOneWindow(Popup):
    def __init__(self, main_window, controller:MainController, cur_route_name, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._controller = controller
        self._cur_route_name = cur_route_name

        raw_route = self._controller.get_raw_route()
        if raw_route.init_route_state is None:
            self._final_config_path = self._final_route_path = self._final_output_path = "Not Generated"
            route_one_results_init = "Cannot export when no route is loaded"
        else:
            self._final_config_path, self._final_route_path, self._final_output_path = \
                route_one_utils.export_to_route_one(raw_route, self._cur_route_name)
            route_one_results_init = ""

        self._config_file_label = tk.Label(self, text=f"Config path: {self._final_config_path}")
        self._config_file_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self._route_file_label = tk.Label(self, text=f"Route path: {self._final_route_path}")
        self._route_file_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self._route_jar_label = tk.Label(self, text=f"RouteOne jar Path: {config.get_route_one_path()}")
        self._route_jar_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self._set_jar_button = custom_components.SimpleButton(self, text=f"Set R1 jar path", command=self.set_jar_path)
        self._set_jar_button.grid(row=3, column=0, padx=10, pady=10)
        self._run_route_one_button = custom_components.SimpleButton(self, text=f"Run RouteOne", command=self.run_route_one)
        self._run_route_one_button.grid(row=3, column=1, padx=10, pady=10)

        # TODO: gross, ugly, wtv
        if raw_route.init_route_state is None:
            self._run_route_one_button.disable()

        self._route_one_results_label = tk.Label(self, text=route_one_results_init, justify=tk.CENTER)
        self._route_one_results_label.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

        self._close_button = custom_components.SimpleButton(self, text="Close", command=self.close)
        self._close_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.bind('<Escape>', self.close)

    def set_jar_path(self, *args, **kwargs):
        file_result = filedialog.askopenfile()
        if file_result is None:
            self.lift()
            return
        jar_path = file_result.name
        self._route_jar_label.configure(text=f"RouteOne jar Path: {jar_path}")
        config.set_route_one_path(jar_path)
        self.lift()

    def run_route_one(self, *args, **kwargs):
        if not config.get_route_one_path():
            self._route_one_results_label.configure(text="No RouteOne jar path set, cannot run...")
            return
        
        result = route_one_utils.run_route_one(config.get_route_one_path(), self._final_config_path)
        if not result:
            self._route_one_results_label.configure(text=f"RouteOne finished: {self._final_output_path}\nDouble check top of output file for errors")
        else:
            self._route_one_results_label.configure(text=f"Error encountered running RouteOne: {result}")

        self.lift()
