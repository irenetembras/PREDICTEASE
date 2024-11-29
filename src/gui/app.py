import os
import threading
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, messagebox, simpledialog, ttk
import pandas as pd
import sqlite3

from src.data import file_importer, data_handler
from src.models import regression, model_io
from src.visualization import data_display, plotting
from src.gui.loading_indicator import LoadingIndicator

class DataLoaderApp:
    """
    Application to load and visualize data, manage NaNs, and create a
    linear regression model with error metrics.
    """
    def __init__(self, root):
        self.root = root
        self.font_style = tkFont.Font(family="Helvetica", size=12)
        self.build_menu()
        # Initialize the root window and GUI components
        self.root.state('zoomed')
        self.root.title("Data Loader")
        self.root.configure(bg="#f0f0f0")

        # Initialize variables
        self.df = None
        self.selected_input = None
        self.selected_output = None
        self.model_description = ""
        self.model = None

        # Build GUI components
        self.build_labels()
        self.build_frames()
        self.build_controls()
        self.build_results_table()

        # Welcome message
        messagebox.showinfo(
            "Welcome to Data Loader",
            "Welcome to the Data Loader application!\n\n"
            "This tool allows you to:\n"
            "1. Load and Visualize Data\n"
            "2. Manage Missing Values\n"
            "3. Create Linear Regression Models\n"
            "4. Save and Load Models\n\n"
            "To get started:\n"
            "- Navigate to the 'File' menu to load a dataset or an existing model.\n"
            "- Use the 'Data' menu to preprocess your data.\n"
            "- In the 'Regression Controls' section, select your desired columns and create a regression model.\n"
            "- Save your model using the 'Save Model' button for future reference."
        )

    # Methods to build GUI components
    def build_menu(self):
        """Build the menu bar with File, Data, and Prediction menus"""
        # Create the toolbar
        self.toolbar = tk.Frame(self.root, bg="#3e3e3e", height=40)
        self.toolbar.pack(side="top", fill="x")

        # File menu button
        self.file_menu_button = tk.Menubutton(
            self.toolbar,
            text="File",
            font=self.font_style,
            bg="#3e3e3e",
            fg="white",
            bd=0,
            padx=20,
            pady=5,
            activebackground="#5e5e5e",
            activeforeground="white"
        )
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0, bg="#5e5e5e", fg="white")
        self.file_menu.add_command(
            label="Load Dataset", command=self.load_file
        )
        self.file_menu.add_command(
            label="Load Model", command=self.load_model
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.file_menu_button.config(menu=self.file_menu)
        self.file_menu_button.pack(side="left", padx=10)

        # Data menu button
        self.data_menu_button = tk.Menubutton(
            self.toolbar,
            text="Data",
            font=self.font_style,
            bg="#3e3e3e",
            fg="white",
            bd=0,
            padx=20,
            pady=5,
            activebackground="#5e5e5e",
            activeforeground="white"
        )
        self.data_menu = tk.Menu(self.data_menu_button, tearoff=0, bg="#5e5e5e", fg="white")
        self.data_menu.add_command(
            label="Remove rows with NaN",  # Option 1
            command=lambda: self.handle_nan(option="1")
        )
        self.data_menu.add_command(
            label="Fill with Mean",  # Option 2
            command=lambda: self.handle_nan(option="2")
        )
        self.data_menu.add_command(
            label="Fill with Median",  # Option 3
            command=lambda: self.handle_nan(option="3")
        )
        self.data_menu.add_command(
            label="Fill with Constant",  # Option 4
            command=lambda: self.handle_nan(option="4")
        )
        self.data_menu_button.config(menu=self.data_menu)
        self.data_menu_button.pack(side="left", padx=2)

        # Prediction menu button (initially disabled)
        self.prediction_menu_button = tk.Menubutton(
            self.toolbar,
            text="Prediction",
            font=self.font_style,
            bg="#3e3e3e",
            fg="white",
            bd=0,
            padx=20,
            pady=5,
            state='disabled',  # Initially disabled
            activebackground="#5e5e5e",
            activeforeground="white"
        )
        self.prediction_menu = tk.Menu(self.prediction_menu_button, tearoff=0, bg="#5e5e5e", fg="white")
        self.prediction_menu.add_command(
            label="Make Prediction",
            command=self.make_prediction_dialog
        )
        self.prediction_menu_button.config(menu=self.prediction_menu)
        self.prediction_menu_button.pack(side="left", padx=2)

    def build_labels(self):
        # Label to display the selected file path
        self.file_path_label = tk.Label(
            self.root,
            text="No file selected",
            font=self.font_style,
            bg="#f0f0f0",
            fg="black"
        )
        self.file_path_label.pack(pady=10)

    def build_frames(self):
        # Frame for the data table
        self.table_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.table_frame_border.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.table_frame = tk.Frame(
            self.table_frame_border, bg="white"
        )
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for regression controls
        self.controls_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.controls_frame_border.pack(
            side="left", fill="y", padx=10, pady=5
        )
        self.controls_frame = tk.Frame(
            self.controls_frame_border, bg="white"
        )
        self.controls_frame.pack(fill="both", padx=5, pady=5)

        # Frame for the graph
        self.graph_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.graph_frame_border.pack(
            side="right",
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )
        self.graph_frame = tk.Frame(self.graph_frame_border, bg="white")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def build_controls(self):
        # Contents of regression control section
        input_label = tk.Label(
            self.controls_frame,
            text="Select input column:",
            font=self.font_style,
            bg="white"
        )
        input_label.pack(anchor="w", padx=10, pady=5)
        self.input_selector = ttk.Combobox(
            self.controls_frame, state="readonly"
        )
        self.input_selector.pack(fill=tk.X, padx=10, pady=5)

        output_label = tk.Label(
            self.controls_frame,
            text="Select output column:",
            font=self.font_style,
            bg="white"
        )
        output_label.pack(anchor="w", padx=10, pady=5)
        self.output_selector = ttk.Combobox(
            self.controls_frame, state="readonly"
        )
        self.output_selector.pack(fill=tk.X, padx=10, pady=5)

        description_label = tk.Label(
            self.controls_frame,
            text="Enter model description (optional):",
            font=self.font_style,
            bg="white"
        )
        description_label.pack(anchor="w", padx=10, pady=5)
        self.dtext = tk.Text(
            self.controls_frame, height=2, width=30
        )
        self.dtext.pack(padx=10, pady=5)

        create_button = tk.Button(
            self.controls_frame,
            text="Create Model",
            command=self.create_regression_model,
            font=self.font_style,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049"
        )
        create_button.pack(pady=10, padx=10, fill=tk.X)

        save_button = tk.Button(
            self.controls_frame,
            text="Save Model",
            command=self.save_model,
            font=self.font_style,
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda"
        )
        save_button.pack(pady=5, padx=10, fill=tk.X)

    def build_results_table(self):
        # Create a results table
        self.results_table = ttk.Treeview(
            self.controls_frame,
            columns=("Name", "Value"),
            show='headings',
            height=5
        )
        self.results_table.heading("Name", text="Name")
        self.results_table.heading("Value", text="Value")
        self.results_table.column("Name", anchor="center", width=150)
        self.results_table.column("Value", anchor="center", width=200)
        self.results_table.pack(pady=10, padx=10, fill=tk.BOTH)

        # Initialize the table with placeholders
        self.results_names = ["Formula", "R²", "MSE", "Description", "Prediction Result"]
        self.results_items = []
        for name in self.results_names:
            item_id = self.results_table.insert("", "end", values=(name, "-"))
            self.results_items.append(item_id)

    # Other methods from interfaz_grafica.py
    # Ensure that all methods are appropriately updated to use the new modules

    def load_file(self):
        """Loads a data file and processes it."""
        file_types = [
            ("CSV Files", "*.csv"),
            ("Excel Files", "*.xlsx *.xls"),
            ("SQLite Files", "*.sqlite *.db")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            threading.Thread(target=self.process_import, args=(file_path,)).start()

    def process_import(self, file_path):
        """Processes the import of the selected file."""
        try:
            self.show_loading_indicator("Loading dataset, please wait...")
            
            def import_task():
                try:
                    # Check file size
                    if os.path.getsize(file_path) == 0:
                        raise ValueError("The selected file is empty.")

                    # Import the file
                    df = file_importer.import_file(file_path)
                    if df is None:
                        raise ValueError("Failed to import the file. It may be corrupted or in an unsupported format.")

                    # Update DataFrame in main thread
                    self.root.after(0, lambda: self._complete_import(df, file_path))

                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                finally:
                    self.root.after(0, self.hide_loading_indicator)

            # Start import in separate thread
            thread = threading.Thread(target=import_task)
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.hide_loading_indicator()
            messagebox.showerror("Error", f"Failed to start import: {str(e)}")

    def _complete_import(self, df, file_path):
        """Complete the import process in the main thread."""
        try:
            self.df = df
            self.file_path_label.config(text=f"Loaded: {os.path.basename(file_path)}")
            self.display_data()
            self.populate_selectors()
            messagebox.showinfo("Success", "File loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error completing import: {str(e)}")

    def display_data(self):
        """Displays the data in a table."""
        if self.df is None:
            return

        data_display.display_data_table(self.table_frame, self.df)

    def populate_selectors(self):
        """Populates the column selectors with DataFrame columns."""
        if self.df is not None:
            columns = list(self.df.columns)
            self.input_selector['values'] = columns
            self.output_selector['values'] = columns

    def handle_nan(self, option):
        """Handles NaN values in the DataFrame."""
        if self.df is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        threading.Thread(target=self._handle_nan_thread, args=(option,)).start()

    def _handle_nan_thread(self, option):
        """Thread function for handling NaN values."""
        try:
            self.show_loading_indicator("Handling NaN values...")
            if option == "1":
                self.df = data_handler.remove_rows_with_nan(self.df)
            elif option == "2":
                self.df = data_handler.fill_nan_with_mean(self.df)
            elif option == "3":
                self.df = data_handler.fill_nan_with_median(self.df)
            elif option == "4":
                value = simpledialog.askfloat("Input", "Enter constant value:")
                if value is not None:
                    self.df = data_handler.fill_nan_with_constant(self.df, value)
                else:
                    return

            self.root.after(0, self.display_data)
            self.root.after(0, lambda: messagebox.showinfo("Success", "NaN values handled successfully."))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            self.root.after(0, self.hide_loading_indicator)

    def create_regression_model(self):
        """Creates a linear regression model."""
        if self.df is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        self.selected_input = self.input_selector.get()
        self.selected_output = self.output_selector.get()

        if not self.selected_input or not self.selected_output:
            messagebox.showwarning("Warning", "Please select input and output columns.")
            return

        self.model_description = self.dtext.get("1.0", "end-1c").strip()
        if not self.model_description:
            self.model_description = "No description provided"

        threading.Thread(target=self._create_model_thread).start()

    def _create_model_thread(self):
        """Thread function for creating the regression model."""
        try:
            self.show_loading_indicator("Creating regression model...")
            X = self.df[[self.selected_input]].values
            y = self.df[self.selected_output].values

            model, predictions, mse, r2, formula = regression.create_linear_regression_model(X, y)
            self.model = model

            # Store data for plotting
            self.X_plot = X
            self.y_plot = y
            self.predictions_plot = predictions

            # Update UI in main thread
            self.root.after(0, lambda: self.update_model_results(formula, r2, mse))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            self.root.after(0, self.hide_loading_indicator)

    def update_model_results(self, formula, r2, mse):
        """Updates the UI with model results."""
        # Update results table
        self.update_results_table({
            "Formula": formula,
            "R²": f"{r2:.4f}",
            "MSE": f"{mse:.4f}",
            "Description": self.model_description
        })

        # Plot regression graph
        plotting.plot_regression_graph(
            self.graph_frame,
            self.X_plot,
            self.y_plot,
            self.predictions_plot,
            self.selected_input,
            self.selected_output
        )

        # Enable prediction menu
        self.prediction_menu_button.config(state='normal')

        messagebox.showinfo("Success", "Regression model created successfully!")

    def make_prediction_dialog(self):
        """Opens a dialog for making predictions."""
        if self.model is None:
            messagebox.showwarning("Warning", "No model available.")
            return

        value = simpledialog.askfloat(
            "Input",
            f"Enter a value for {self.selected_input}:"
        )
        
        if value is not None:
            try:
                prediction = self.model.predict([[value]])[0]
                result = f"{prediction:.4f}"
                self.update_results_table({"Prediction Result": result})
                messagebox.showinfo(
                    "Prediction Result",
                    f"Predicted {self.selected_output}: {result}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Prediction failed: {str(e)}")

    def save_model(self):
        """Saves the current model."""
        if self.model is None:
            messagebox.showwarning("Warning", "No model to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".joblib",
            filetypes=[("Joblib files", "*.joblib")]
        )
        
        if file_path:
            model_data = {
                'model': self.model,
                'input_column': self.selected_input,
                'output_column': self.selected_output,
                'description': self.model_description
            }
            
            success, message = model_io.save_model(file_path, model_data)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def load_model(self):
        """Loads a saved model."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Joblib files", "*.joblib")]
        )
        
        if file_path:
            model_data, error = model_io.load_model(file_path)
            if error:
                messagebox.showerror("Error", error)
                return

            self.model = model_data['model']
            self.selected_input = model_data['input_column']
            self.selected_output = model_data['output_column']
            self.model_description = model_data.get('description', 'No description provided')

            self.prediction_menu_button.config(state='normal')
            messagebox.showinfo("Success", "Model loaded successfully!")

    def update_results_table(self, updates):
        """Updates the results table with new values."""
        for idx, name in enumerate(self.results_names):
            if name in updates:
                self.results_table.item(
                    self.results_items[idx],
                    values=(name, updates[name])
                )

    def reset_controls(self):
        """Resets all controls to their default state."""
        self.input_selector.set('')
        self.output_selector.set('')
        self.dtext.delete('1.0', tk.END)
        for idx, name in enumerate(self.results_names):
            self.results_table.item(
                self.results_items[idx],
                values=(name, "-")
            )
        self.prediction_menu_button.config(state='disabled')

    def show_loading_indicator(self, message):
        """Shows a loading indicator with the given message."""
        self.loading_indicator = LoadingIndicator(self.root, message)

    def hide_loading_indicator(self):
        """Hides the loading indicator."""
        if hasattr(self, 'loading_indicator'):
            self.loading_indicator.close()