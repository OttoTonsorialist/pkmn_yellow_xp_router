import tkinter as tk

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui import custom_components
from utils.constants import const
from utils import io_utils


class LoadRouteWindow(Popup):
    def __init__(self, main_window, controller:MainController, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._controller = controller

        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack()
        self.padx = 5
        self.pady = 5

        self.previous_route_label = tk.Label(self.controls_frame, text="Existing Routes:")
        self.previous_route_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.previous_route_names = custom_components.SimpleOptionMenu(self.controls_frame, [const.NO_SAVED_ROUTES], callback=self._select_callback)
        self.previous_route_names.grid(row=0, column=1, padx=self.padx, pady=self.pady)
        self.previous_route_names.config(width=25)

        self.filter_label = tk.Label(self.controls_frame, text="Filter:")
        self.filter = custom_components.SimpleEntry(self.controls_frame, callback=self._filter_callback)
        self.filter_label.grid(row=1, column=0)
        self.filter.grid(row=1, column=1)

        self.allow_oudated = tk.BooleanVar()
        self.allow_oudated.trace("w", self._filter_callback)
        self.outdated_label = tk.Label(self.controls_frame, text="Show Backup Routes?")
        self.outdated_checkbox = tk.Checkbutton(self.controls_frame, variable=self.allow_oudated, onvalue=True, offvalue=False)
        self.outdated_label.grid(row=2, column=0)
        self.outdated_checkbox.grid(row=2, column=1)

        self.outdated_info_label = tk.Label(self.controls_frame, text="Backup Routes are older versions of your route.\nEvery save makes a backup that is persisted, and can be reloaded if needed.\nThese are hidden by default because they can quickly pile up")
        self.outdated_info_label.grid(row=3, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.warning_label = tk.Label(self.controls_frame, text="WARNING: Any unsaved changes in your current route\nwill be lost when loading an existing route!")
        self.warning_label.grid(row=4, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.create_button = custom_components.SimpleButton(self.controls_frame, text="Load Route", command=self.load)
        self.create_button.grid(row=10, column=0, padx=self.padx, pady=self.pady)
        self.cancel_button = custom_components.SimpleButton(self.controls_frame, text="Cancel", command=self.close)
        self.cancel_button.grid(row=10, column=1, padx=self.padx, pady=self.pady)

        self.bind('<Return>', self.load)
        self.bind('<Escape>', self.close)
        self.filter.focus()
        self._filter_callback()
        self._select_callback()

    def _filter_callback(self, *args, **kwargs):
        all_routes = io_utils.get_existing_route_names(
            filter_text=self.filter.get(),
            load_backups=self.allow_oudated.get()
        )

        if not all_routes:
            all_routes = [const.NO_SAVED_ROUTES]

        self.previous_route_names.new_values(all_routes)

    def _select_callback(self, *args, **kwargs):
        selected_route = self.previous_route_names.get()
        if selected_route == const.NO_SAVED_ROUTES:
            self.create_button.disable()
        else:
            self.create_button.enable()
    
    def load(self, *args, **kwargs):
        selected_route = self.previous_route_names.get()
        if selected_route == const.NO_SAVED_ROUTES:
            return
        
        self.close()
        self._controller.load_route(io_utils.get_existing_route_path(self.previous_route_names.get()))
