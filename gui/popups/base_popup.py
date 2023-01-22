import customtkinter as ctk


class Popup(ctk.CTkToplevel):
    def __init__(self, main_window:ctk.CTk, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self._main_window = main_window
        # TODO: if we want the little flash thingy, try this instead of disabling: https://stackoverflow.com/a/28541762
        self._main_window.attributes('-disabled', True)

        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self, event=None):
        self._main_window.attributes('-disabled', False)
        # TODO: just remove this call??
        self._main_window.clear_popup()
        self.destroy()
