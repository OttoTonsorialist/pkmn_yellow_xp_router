import time
import threading

import customtkinter as ctk

from gui import custom_components
from utils.constants import const
from utils import auto_update

class AutoUpgradeGUI(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._allow_close = False

        self.auto_update_frame = ctk.CTkFrame(self, width=250, height=150)
        self.auto_update_frame.pack()
        self.auto_update_frame.pack_propagate(False)

        self.processing_message = ctk.CTkLabel(self.auto_update_frame)
        self.processing_message.pack(pady=10, padx=20)

        self.auto_update_message = ctk.CTkLabel(self.auto_update_frame)
        self.auto_update_message.pack(pady=10, padx=10)

        self.button = custom_components.SimpleButton(self.auto_update_frame, text="Restart App", command=self._prevent_abort)
        self.button.pack(pady=10, padx=10)
        self.button.disable()
        
        self._dum_thread = threading.Thread(target=self._update_processing_text)
        self._dum_thread.daemon = True
        self._dum_thread.start()
        
        self._thread = threading.Thread(target=self._auto_update_app)
        self._thread.daemon = True
        self._thread.start()

        self.bind(const.FORCE_QUIT_EVENT, self._prevent_abort)
        self.protocol("WM_DELETE_WINDOW", self._prevent_abort)
    
    def _prevent_abort(self, *args, **kwargs):
        if self._allow_close:
            self.destroy()
    
    def _update_processing_text(self, *args, **kwargs):
        messages = [
            "Updating .",
            "Updating ..",
            "Updating ...",
        ]
        cur_idx = 0
        while not self._allow_close:
            self.processing_message.configure(text=messages[cur_idx])
            cur_idx = (cur_idx + 1) % len(messages)
            time.sleep(0.1)
    
    def _display_update_message(self, new_text):
        self.auto_update_message.configure(text=new_text)

    def _auto_update_app(self, *args, **kwargs):
        try:
            success = auto_update.update(display_fn=self._display_update_message)
        except Exception as e:
            success = False

        self._allow_close = True
        time.sleep(0.15)
        if not success:
            self.processing_message.configure(text="Error")
            self.auto_update_message.configure(text="Failed automatic update\nTry manually installing the new version")
        else:
            self.processing_message.configure(text="Success!")
            self.auto_update_message.configure(text="Automatic update successful!\nClick OK to restart app")
        
        self.button.enable()
