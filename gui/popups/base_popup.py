import tkinter as tk
import sys


class Popup(tk.Toplevel):
    def __init__(self, main_window:tk.Tk, *args, **kwargs):
        tk.Toplevel.__init__(self, main_window, *args, **kwargs)
        self._main_window = main_window
        # TODO: if we want the little flash thingy, try this instead of disabling: https://stackoverflow.com/a/28541762
        if sys.platform == "win32":
            self._main_window.attributes('-disabled', True)

        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self, event=None):
        if sys.platform == "win32":
            self._main_window.attributes('-disabled', False)
        self.destroy()
