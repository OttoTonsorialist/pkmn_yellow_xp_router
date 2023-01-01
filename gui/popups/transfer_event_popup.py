import tkinter as tk

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui import custom_components
from utils.constants import const


class TransferEventWindow(Popup):
    def __init__(self, main_window, controller:MainController, all_existing_folders, valid_dest_folders, event_ids, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._controller = controller
        self._all_existing_folders = all_existing_folders
        self._valid_dest_folders = valid_dest_folders
        self._event_ids = event_ids

        self._transfer_type_label = tk.Label(self, text=f"Transfer to:")
        self._transfer_type = custom_components.SimpleOptionMenu(self, option_list=[const.TRANSFER_EXISTING_FOLDER, const.TRANSFER_NEW_FOLDER], callback=self._transfer_type_callback)
        self._transfer_type_label.grid(row=0, column=0, padx=10, pady=10)
        self._transfer_type.grid(row=0, column=1, padx=10, pady=10)

        self._new_folder_label = tk.Label(self, text=f"New folder:")
        self._new_folder_name = custom_components.SimpleEntry(self, callback=self._new_folder_callback)

        self._dest_folder_label = tk.Label(self, text=f"New folder:")
        self._dest_folder_name = custom_components.SimpleOptionMenu(self, option_list=self.get_possible_folders())

        self.filter_label = tk.Label(self, text="Filter:")
        self.filter = custom_components.SimpleEntry(self, callback=self._filter_callback)

        self._add_button = custom_components.SimpleButton(self, command=self.transfer, text="Transfer to Folder")
        self._cancel_button = custom_components.SimpleButton(self, text="Cancel", command=self.close)
        self._add_button.grid(row=3, column=0, padx=10, pady=10)
        self._cancel_button.grid(row=3, column=1, padx=10, pady=10)

        self.bind('<Return>', self.transfer)
        self.bind('<Escape>', self.close)
        self._transfer_type_callback()
        self.filter.focus()
    
    def get_possible_folders(self, filter_text=""):
        filter_text = filter_text.lower()
        result = [x for x in self._valid_dest_folders if filter_text in x.lower()]

        if not result:
            result = [const.NO_FOLDERS]

        return result
    
    def _transfer_type_callback(self, *args, **kwargs):
        if self._transfer_type.get() == const.TRANSFER_EXISTING_FOLDER:
            self._dest_folder_label.grid(row=1, column=0, padx=10, pady=10)
            self._dest_folder_name.grid(row=1, column=1, padx=10, pady=10)
            self.filter_label.grid(row=2, column=0, padx=10, pady=10)
            self.filter.grid(row=2, column=1, padx=10, pady=10)
            self._new_folder_label.grid_forget()
            self._new_folder_name.grid_forget()
            self._filter_callback()
        else:
            self._dest_folder_label.grid_forget()
            self._dest_folder_name.grid_forget()
            self.filter_label.grid_forget()
            self.filter.grid_forget()
            self._new_folder_label.grid(row=1, column=0, padx=10, pady=10)
            self._new_folder_name.grid(row=1, column=1, padx=10, pady=10)
            self._new_folder_callback()

    def _filter_callback(self, *args, **kwargs):
        dest_folder_vals = self.get_possible_folders(filter_text=self.filter.get())
        if const.NO_FOLDERS in dest_folder_vals:
            self._add_button.disable()
        else:
            self._add_button.enable()

        self._dest_folder_name.new_values(dest_folder_vals)

    def _new_folder_callback(self, *args, **kwargs):
        if self._new_folder_name.get() in self._all_existing_folders:
            self._add_button.disable()
        else:
            self._add_button.enable()
    
    def transfer(self, *args, **kwargs):
        if self._transfer_type.get() == const.TRANSFER_EXISTING_FOLDER:
            if self._dest_folder_name.get() != const.NO_FOLDERS:
                self.close()
                self._controller.transfer_to_folder(self._event_ids, self._dest_folder_name.get())
        else:
            if self._new_folder_name.get() not in self._all_existing_folders:
                self.close()
                self._controller.transfer_to_folder(self._event_ids, self._new_folder_name.get().strip())
