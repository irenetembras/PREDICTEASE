# src/visualization/data_display.py

import tkinter as tk
from tkinter import ttk


def display_dataframe_in_treeview(df, parent_frame):
    """
    Displays a pandas DataFrame in a Tkinter Treeview widget.

    Parameters:
    - df (pd.DataFrame): The DataFrame to display.
    - parent_frame (tk.Frame): The parent frame to place the Treeview in.
    """
    # Destroy all existing widgets in the parent frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Create vertical and horizontal scrollbars
    vsb = ttk.Scrollbar(parent_frame, orient="vertical")
    vsb.pack(side='right', fill='y')
    hsb = ttk.Scrollbar(parent_frame, orient="horizontal")
    hsb.pack(side='bottom', fill='x')

    # Create the Treeview to display data
    tree = ttk.Treeview(
        parent_frame,
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set,
        style="Treeview"
    )
    tree.pack(fill=tk.BOTH, expand=True)

    # Configure the scrollbars
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)

    # Configure the columns of the table
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    # Insert the data into the table
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))
