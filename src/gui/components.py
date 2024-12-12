import tkinter as tk
from tkinter import ttk


def create_menu_button(parent, text, menu_items, font_style,
                       bg, fg, activebackground, activeforeground):
    """Creates a Menubutton with the given menu items."""
    menu_button = tk.Menubutton(
        parent,
        text=text,
        font=font_style,
        bg=bg,
        fg=fg,
        bd=0,
        padx=20,
        pady=5,
        activebackground=activebackground,
        activeforeground=activeforeground
    )
    menu = tk.Menu(menu_button, tearoff=0, bg=activebackground, fg=fg)
    for item in menu_items:
        if item == "separator":
            menu.add_separator()
        else:
            label = item.get('label')
            command = item.get('command')
            menu.add_command(label=label, command=command)
    menu_button.config(menu=menu)
    return menu_button


def create_label(parent, text, font_style, bg, fg):
    """Creates a Label."""
    label = tk.Label(
        parent,
        text=text,
        font=font_style,
        bg=bg,
        fg=fg
    )
    return label


def create_frame(parent, bg, side=None, fill=None,
                 expand=False, padx=0, pady=0):
    """Creates a Frame."""
    frame = tk.Frame(parent, bg=bg)
    if side:
        frame.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)
    else:
        frame.pack(fill=fill, expand=expand, padx=padx, pady=pady)
    return frame


def create_button(parent, text, command, font_style, bg, fg, activebackground):
    """Creates a Button."""
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=font_style,
        bg=bg,
        fg=fg,
        activebackground=activebackground
    )
    return button


def create_combobox(parent, state="readonly"):
    """Creates a Combobox."""
    combobox = ttk.Combobox(parent, state=state)
    return combobox


def create_text(parent, height, width):
    """Creates a Text widget."""
    text_widget = tk.Text(parent, height=height, width=width)
    return text_widget


def create_treeview(parent, columns, headings, column_widths, height):
    """Creates a Treeview."""
    treeview = ttk.Treeview(
        parent,
        columns=columns,
        show='headings',
        height=height
    )
    for col, heading, width in zip(columns, headings, column_widths):
        treeview.heading(col, text=heading)
        treeview.column(col, anchor="center", width=width)
    return treeview
