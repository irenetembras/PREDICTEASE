# src/gui/loading_indicator.py

import tkinter as tk
from tkinter import ttk


def show_loading_indicator(root, message):
    """
    Displays a loading indicator window with a progress bar.

    Parameters:
    - root: The root Tkinter window.
    - message (str): The message to display above the progress bar.
    """
    loading_window = tk.Toplevel(root)
    loading_window.title("Loading")
    loading_window.resizable(False, False)
    loading_window.grab_set()  # Prevent interaction with the main window

    # Define the size of the window
    width = 500  # Increased width
    height = 200  # Increased height

    # Calculate x and y coordinates to center the window
    screen_width = loading_window.winfo_screenwidth()
    screen_height = loading_window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Set the geometry of the window
    loading_window.geometry(f"{width}x{height}+{x}+{y}")

    # Create and pack the message label
    label = tk.Label(loading_window, text=message, font=("Helvetica", 12))
    label.pack(pady=30)

    # Create and pack the progress bar
    progress = ttk.Progressbar(loading_window, mode='indeterminate', length=400)
    progress.pack(pady=20)
    progress.start(10)  # Adjust the speed as needed

    # Attach the loading window to the root for easy access
    root.loading_window = loading_window


def hide_loading_indicator(root):
    """
    Closes the loading indicator window.

    Parameters:
    - root: The root Tkinter window.
    """
    if hasattr(root, 'loading_window') and root.loading_window:
        root.loading_window.destroy()
        root.loading_window = None
