import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import joblib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from modules.modulo_importacion import import_file  


def process_import(self, file_path):
            """Processes the import of the selected file."""
            try:
                # Check file size before importing
                if os.path.getsize(file_path) == 0:
                    raise ValueError(
                        "The selected file is empty (size is zero bytes)."
                        )

                # Import the file
                self.df = import_file(file_path)

                # Check if the DataFrame is empty after import
                if self.df is None or self.df.empty:
                    raise ValueError(
                        "The imported file is empty (no rows or columns found)."
                        )

                # Check if the file contains only empty columns
                if not self.df.columns.any() or self.df.dropna(how='all').empty:
                    raise ValueError(
                        "The imported file has only empty columns or rows."
                        )

                # If everything is correct, display the data
                self.root.after(0, self.display_data)
                self.root.after(0, self.populate_selectors)
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Success", "File loaded successfully."
                        )
                )

            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                self.root.after(
                    0,
                    lambda: messagebox.showerror("Error", error_message)
                )

def populate_selectors(self):
            """Fills the column selectors with the columns from the DataFrame."""
            if self.df is not None:
                columns = list(self.df.columns)
                self.input_selector['values'] = columns
                self.output_selector['values'] = columns

def display_data(self):
            """Displays the data in a table."""
            # Ensure data frames are visible
            self.file_path_label.pack(pady=10)
            self.table_frame_border.pack(
                fill=tk.BOTH, expand=True, padx=10, pady=5
                )
            self.controls_frame_border.pack(
                side="left", fill="y", padx=10, pady=5
                )
            self.graph_frame_border.pack(
                side="right",
                fill=tk.BOTH,
                expand=True,
                padx=10,
                pady=5
            )

            # Reset controls and clear graph
            self.reset_controls()
            self.clear_graph()

            # Destroy any existing widgets in the table frame
            for widget in self.table_frame.winfo_children():
                widget.destroy()

            # Create vertical and horizontal scrollbars
            vsb = ttk.Scrollbar(self.table_frame, orient="vertical")
            vsb.pack(side='right', fill='y')
            hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")
            hsb.pack(side='bottom', fill='x')

            # Create the treeview to display the data
            self.table = ttk.Treeview(
                self.table_frame,
                yscrollcommand=vsb.set,
                xscrollcommand=hsb.set,
                style="Treeview"
            )
            self.table.pack(fill=tk.BOTH, expand=True)

            # Configure the scrollbars
            vsb.config(command=self.table.yview)
            hsb.config(command=self.table.xview)

            # Configure the table columns
            self.table["columns"] = list(self.df.columns)
            self.table["show"] = "headings"

            for col in self.df.columns:
                self.table.heading(col, text=col)
                self.table.column(col, anchor="center", width=100)

            # Insert the data into the table
            for _, row in self.df.iterrows():
                self.table.insert("", "end", values=list(row))

def handle_nan(self, option):
            """Handles NaN values in the DataFrame."""
            if self.df is None:
                messagebox.showwarning("Warning", "No dataset loaded.")
                return

            if option == "1":
                self.df = self.df.dropna()
                messagebox.showinfo("Success", "Rows with NaN values removed.")
            else:
                if option == "4":  # Fill with constant
                    constant_value_input = simpledialog.askstring(
                        "Input",
                        "Enter a constant value:"
                    )
                    if constant_value_input is None:
                        messagebox.showinfo("Cancelled", "Operation cancelled by user.")
                        return  # Exit the method if user cancels
                    try:
                        constant_value = float(constant_value_input)
                    except ValueError:
                        messagebox.showerror("Error", "Invalid constant value entered.")
                        return  # Exit the method if invalid input
                numeric_columns = self.df.select_dtypes(
                    include=['float64', 'int64']
                ).columns
                for col in numeric_columns:
                    if option == "2":  # Fill with mean
                        mean_value = self.df[col].mean()
                        rounded_mean_value = round(mean_value, 3)
                        self.df[col] = self.df[col].fillna(
                            rounded_mean_value
                        )
                    elif option == "3":  # Fill with median
                        median_value = self.df[col].median()
                        rounded_median_value = round(median_value, 3)
                        self.df[col] = self.df[col].fillna(
                            rounded_median_value
                        )
                    elif option == "4":  # Fill with constant
                        self.df[col] = self.df[col].fillna(
                            constant_value
                        )
                # Display success message after processing
                if option == "2":
                    messagebox.showinfo(
                        "Success", "NaN values filled with column mean."
                        )
                elif option == "3":
                    messagebox.showinfo("Success", "NaN values filled with column median.")
                elif option == "4":
                    messagebox.showinfo(
                        "Success",
                        f"NaN values filled with constant value: {constant_value}"
                    )
            self.display_data()
