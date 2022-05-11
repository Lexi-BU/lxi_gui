import tkinter as tk
from tkinter import font


def entry_box(root=None,
              width=10,
              justify="center",
              bg="white",
              fg="black",
              borderwidth=2,
              entry_val="",
              entry_label="",
              row=0,
              column=0,
              rowspan=1,
              columnspan=1,
              sticky="n",
              font_style=None):
    """
    Creates a text entry box in the GUI.
    """

    if root is None:
        raise ValueError("Root is not defined.")
    if font_style is None:
        font_style = font.Font(family="Helvetica", size=12)

    main_entry = tk.Entry(root, width=width, justify=justify, bg=bg, fg=fg, borderwidth=borderwidth)
    main_entry.insert(0, entry_val)
    main_entry.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan, sticky=sticky)
    main_label = tk.Label(root, text=entry_label, font=font_style)
    main_label.grid(row=row, column=column + 1, columnspan=columnspan, rowspan=rowspan, sticky=sticky)

    return main_entry, main_label
