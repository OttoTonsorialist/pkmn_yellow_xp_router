import tkinter.ttk as ttk


def get_bounding_box(tk_frame:ttk.Frame):
    leftmost = tk_frame.winfo_rootx()
    topmost = tk_frame.winfo_rooty()
    rightmost = leftmost + tk_frame.winfo_width()
    bottommost = topmost + tk_frame.winfo_height()

    return (leftmost, topmost, rightmost, bottommost)
