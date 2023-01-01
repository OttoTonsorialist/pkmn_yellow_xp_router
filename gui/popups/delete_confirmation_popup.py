import tkinter as tk
import customtkinter as ctk

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui import custom_components


class DeleteConfirmation(Popup):
    def __init__(self, main_window, controller:MainController, event_ids, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._controller = controller
        self._event_ids = event_ids
        
        if len(self._event_ids) == 1:
            text = "You are trying to delete a non-empty folder.\nAre you sure you want to delete the folder and all child events?"
        else:
            text = "You are trying to delete multiple items at once.\nAre you sure you want to delete all selected items?"
        
        self._label = ctk.CTkLabel(self, text=text)
        self._label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self._confirm_button = custom_components.SimpleButton(self, text="Delete", command=self.delete)
        self._cancel_button = custom_components.SimpleButton(self, text="Cancel", command=self.close)
        self._confirm_button.grid(row=1, column=0, padx=10, pady=10)
        self._cancel_button.grid(row=1, column=1, padx=10, pady=10)

        self.bind('<Return>', self.delete)
        self.bind('<Escape>', self.close)

    def delete(self, *args, **kwargs):
        self.close()
        self._controller.delete_events(self._event_ids)
