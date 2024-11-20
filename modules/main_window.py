import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from modules import modulo_importacion
from modules.data_operations import *  # Importar las funciones que manejan los datos
from modules.model_operations import create_regression_model, load_model  # Importar la función para cargar el modelo
from modules.modulo_importacion import import_file

def reset_controls(self):
            """Resets the input/output selectors and description field."""
            self.input_selector.set('')
            self.output_selector.set('')
            self.dtext.delete('1.0', tk.END)
            self.result_label.config(text='')

def clear_graph(self):
            """Clears the graph frame."""
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
def get_decimal_places(self, series):
            """Returns the maximum number of decimal places in the series."""
            decimals = series.dropna().astype(str).str.split('.').str[1]  # Get the decimal part
            return decimals.str.len().max() if not decimals.empty else 0

def update_interface_for_model(self, formula, r2, mse):
            """Update the interface to display the loaded model."""
            # Destroy existing model details frame if it exists
            if hasattr(self, 'model_details') and self.model_details:
                self.model_details.destroy()

            # Hide unnecessary sections
            self.file_path_label.pack_forget()
            self.table_frame_border.pack_forget()
            self.controls_frame_border.pack_forget()
            self.graph_frame_border.pack_forget()

            # Create a new frame to display the model details
            self.model_details = tk.Frame(self.root, bg="white")
            self.model_details.pack(fill=tk.BOTH, expand=True)

            # Display the model details
            model_info = (
                f"Formula: {formula}\n"
                f"R²: {r2}\n"
                f"MSE: {mse}\n\n"
                f"Description: {self.model_description}"
            )
            model_info_label = tk.Label(
                self.model_details,
                text=model_info,
                font=("Helvetica", 12),
                fg="black",
                justify="center",
                bg="white"
            )
            model_info_label.pack(pady=10, expand=True)

def populate_selectors(self):
        """Fills the column selectors with the columns from the DataFrame."""
        if self.df is not None:
            columns = list(self.df.columns)
            self.input_selector['values'] = columns
            self.output_selector['values'] = columns