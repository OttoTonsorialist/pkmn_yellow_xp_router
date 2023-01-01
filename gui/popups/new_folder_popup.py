import tkinter as tk

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui import custom_components


class NewFolderWindow(Popup):
    def __init__(self, main_window, controller:MainController, cur_folder_names, prev_folder_name, *args, insert_after=None, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._controller = controller
        self._cur_folder_names = cur_folder_names
        self._prev_folder_name = prev_folder_name
        self._insert_after = insert_after

        self._label = tk.Label(self)
        self._folder_name = custom_components.SimpleEntry(self, callback=self.folder_name_update)
        self._label.grid(row=0, column=0, padx=10, pady=10)
        self._folder_name.grid(row=0, column=1, padx=10, pady=10)
        self._add_button = custom_components.SimpleButton(self, command=self.create)
        self._cancel_button = custom_components.SimpleButton(self, text="Cancel", command=self.close)
        self._add_button.grid(row=1, column=0, padx=10, pady=10)
        self._cancel_button.grid(row=1, column=1, padx=10, pady=10)

        self.bind('<Return>', self.create)
        self.bind('<Escape>', self.close)
        self._folder_name.focus()

        if prev_folder_name is None:
            self.title("Create New Folder")
            self._label.configure(text="New Folder Name")
            self._add_button.configure(text="New Folder")
        else:
            self.title("Update Folder Name")
            self._label.configure(text="Update Folder Name")
            self._folder_name.set(prev_folder_name)
            self._add_button.configure(text="Update Folder")

    def folder_name_update(self, *args, **kwargs):
        cur_name = self._folder_name.get()
        if cur_name in self._cur_folder_names:
            self._add_button.disable()
        else:
            self._add_button.enable()
    
    def create(self, *args, **kwargs):
        cur_name = self._folder_name.get()
        if not cur_name:
            return
        elif cur_name in self._cur_folder_names:
            return

        self.close()
        self._controller.finalize_new_folder(
            cur_name,
            prev_folder_name=self._prev_folder_name,
            insert_after=self._insert_after
        )
