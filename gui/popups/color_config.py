import tkinter as tk
from tkinter import ttk
from tkinter import font

from gui.popups.base_popup import Popup
from gui import custom_components
from utils.config_manager import config


class ConfigWindow(Popup):
    def __init__(self, main_window, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        
        self._font_frame = ttk.Frame(self)
        self._font_frame.grid(row=0, column=0)
        self._font_frame.columnconfigure(1, weight=1)

        self._font_name_label = tk.Label(self._font_frame, text="Font Name:")
        self._font_name_label.grid(row=3, column=0, padx=3, pady=3, sticky=tk.EW)

        self._font_name = custom_components.SimpleOptionMenu(self._font_frame, sorted(font.families()))
        self._font_name.grid(row=3, column=1, padx=5, pady=3, sticky=tk.EW)
        custom_font_name = config.get_custom_font_name()
        if custom_font_name not in font.families():
            custom_font_name = config.DEFAULT_FONT_NAME
        self._font_name.set(custom_font_name)

        self._font_name_button = tk.Button(self._font_frame, text="Set Font Name", command=self.set_font_name)
        self._font_name_button.grid(row=4, column=0, columnspan=2, padx=3, pady=3)

        self._font_warning = tk.Label(self._font_frame, text=f"If your custom font is not present in the list\nMake sure that it is installed on your system\nAnd then restart the program")
        self._font_warning.grid(row=5, column=0, columnspan=2, padx=5, pady=3, sticky=tk.EW)

        self._color_frame = ttk.Frame(self)
        #self._color_frame.grid(row=2, column=0, pady=20)

        self._color_header = tk.Label(self._color_frame, text="Color Config:")
        self._color_header.grid(row=0, column=0, padx=5, pady=3, sticky=tk.EW)

        self._reset_colors_button = tk.Button(self._color_frame, text="Reset all colors", command=self._reset_all_colors)
        self._reset_colors_button.grid(row=1, column=0, padx=5, pady=3, sticky=tk.EW)

        self._success_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Success Color:", setter=config.set_success_color, getter=config.get_success_color, callback=self.lift)
        self._success_color.grid(row=2, column=0, sticky=tk.EW)

        self._warning_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Warning Color:", setter=config.set_warning_color, getter=config.get_warning_color, callback=self.lift)
        self._warning_color.grid(row=3, column=0, sticky=tk.EW)

        self._failure_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Failure Color:", setter=config.set_failure_color, getter=config.get_failure_color, callback=self.lift)
        self._failure_color.grid(row=4, column=0, sticky=tk.EW)

        self._divider_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Divider Color:", setter=config.set_divider_color, getter=config.get_divider_color, callback=self.lift)
        self._divider_color.grid(row=5, column=0, sticky=tk.EW)
        
        self._header_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Header Color:", setter=config.set_header_color, getter=config.get_header_color, callback=self.lift)
        self._header_color.grid(row=6, column=0, sticky=tk.EW)
        
        self._primary_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Primary Color:", setter=config.set_primary_color, getter=config.get_primary_color, callback=self.lift)
        self._primary_color.grid(row=7, column=0, sticky=tk.EW)
        
        self._secondary_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Secondary Color:", setter=config.set_secondary_color, getter=config.get_secondary_color, callback=self.lift)
        self._secondary_color.grid(row=8, column=0, sticky=tk.EW)
        
        self._contrast_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Contrast Color:", setter=config.set_contrast_color, getter=config.get_contrast_color, callback=self.lift)
        self._contrast_color.grid(row=9, column=0, sticky=tk.EW)
        
        self._background_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Background Color:", setter=config.set_background_color, getter=config.get_background_color, callback=self.lift)
        self._background_color.grid(row=10, column=0, sticky=tk.EW)
        
        self._text_color = custom_components.ConfigColorUpdater(self._color_frame, label_text="Text Color:", setter=config.set_text_color, getter=config.get_text_color, callback=self.lift)
        self._text_color.grid(row=11, column=0, sticky=tk.EW)

        self._restart_label = tk.Label(self._color_frame, text="After changing colors, you must restart the program\nbefore color changes will take effect")
        self._restart_label.grid(row=15, column=0, padx=5, pady=5, sticky=tk.EW)

        self._close_button = custom_components.SimpleButton(self, text="Close", command=self.close)
        self._close_button.grid(row=15, column=0, padx=5, pady=2)

        self.bind('<Escape>', self.close)
    
    def _reset_all_colors(self, *args, **kwargs):
        config.reset_all_colors()
        self._success_color.refresh_color()
        self._warning_color.refresh_color()
        self._failure_color.refresh_color()
        self._divider_color.refresh_color()
        self._header_color.refresh_color()
        self._primary_color.refresh_color()
        self._secondary_color.refresh_color()
        self._contrast_color.refresh_color()
        self._background_color.refresh_color()
        self._text_color.refresh_color()

    def set_font_name(self, *args, **kwargs):
        config.set_custom_font_name(self._font_name.get())
        self._main_window.load_custom_font()
