import tkinter as tk
from tkinter import ttk
import logging
from typing import List

logger = logging.getLogger(__name__)



class StatColumn(ttk.Frame):
    def __init__(self, *args, num_rows=4, label_width=None, val_width=None, font=None, style_prefix="Primary", **kwargs):
        kwargs['style'] = f"{style_prefix}.TFrame"
        super().__init__(*args, **kwargs)

        self._style_prefix = style_prefix
        self._header_frame = ttk.Frame(self)
        self._header_frame.pack()
        self._header = ttk.Label(self._header_frame, style=f"{style_prefix}.TLabel")

        self._frames:List[ttk.Frame] = []
        self._labels:List[ttk.Label] = []
        self._values:List[ttk.Label] = []

        for idx in range(num_rows):
            cur_frame = ttk.Frame(self)
            cur_frame.pack(fill=tk.X, pady=(2, 0))
            self._frames.append(cur_frame)

            cur_label = ttk.Label(cur_frame, anchor=tk.W, style=f"{style_prefix}.TLabel", width=label_width, font=font)
            cur_label.grid(row=0, column=0, sticky=tk.EW)
            self._labels.append(cur_label)

            cur_value = ttk.Label(cur_frame, anchor=tk.E, style=f"{style_prefix}.TLabel", width=val_width, font=font)
            cur_value.grid(row=0, column=1, sticky=tk.EW)
            self._values.append(cur_value)

            cur_frame.columnconfigure(1, weight=1)
    
    def set_header(self, header):
        if header is None or header == "":
            self._header.pack_forget()
            return
        
        self._header.pack()
        self._header.configure(text=header)
    
    def set_labels(self, label_text_iterable):
        for idx, cur_label_text in enumerate(label_text_iterable):
            if idx >= len(self._labels):
                break
            self._labels[idx].configure(text=cur_label_text)
        
        if len(label_text_iterable) < len(self._labels):
            for idx in range(len(label_text_iterable), len(self._labels)):
                self._labels[idx].configure(text="")
    
    def set_values(self, value_text_iterable, style_iterable=None):
        if style_iterable is None:
            style_iterable = [self._style_prefix for _ in value_text_iterable]
        else:
            for idx in range(len(style_iterable)):
                if style_iterable[idx] is None:
                    style_iterable[idx] = self._style_prefix

        for idx, cur_value_text in enumerate(value_text_iterable):
            if idx >= len(self._values):
                break
            self._values[idx].configure(text=cur_value_text, style=f"{style_iterable[idx]}.TLabel")
            self._labels[idx].configure(style=f"{style_iterable[idx]}.TLabel")
        
        if len(value_text_iterable) < len(self._values):
            for idx in range(len(value_text_iterable), len(self._values)):
                self._values[idx].configure(text="")