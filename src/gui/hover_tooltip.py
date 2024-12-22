# src/gui/hover_tooltip.py

import tkinter as tk

class HoverTooltip:
    """
    A simple tooltip that appears when the mouse hovers over an item.
    """
    def __init__(self, parent, text=""):
        self.parent = parent
        self.text = text
        self.tipwindow = None

    def show(self, x, y):
        """
        Create a Toplevel window to display the text.
        Position it near (x, y).
        """
        if self.tipwindow or not self.text:
            return
        self.tipwindow = tw = tk.Toplevel(self.parent)
        tw.wm_overrideredirect(True)  # remove window decorations
        tw.wm_geometry(f"+{x}+{y}")   # position it at (x,y)

        label = tk.Label(
            tw, text=self.text,
            bg="lightyellow", fg="black",
            relief="solid", borderwidth=1,
            font=("Helvetica", 9)
        )
        label.pack(ipadx=1, ipady=1)

    def hide(self):
        """Destroy the Toplevel if it exists."""
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None
