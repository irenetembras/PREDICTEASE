#  main.py
from src.gui.app import DataLoaderApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = DataLoaderApp(root)
    root.mainloop()
