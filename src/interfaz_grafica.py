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

import modulo_importacion


class DataLoaderApp:
    """
    Application to load and visualize data, manage NaNs, and create a
    linear regression model with error metrics.
    """
    def __init__(self, root):
        root.state('zoomed')
        self.root = root
        self.root.title("Data Loader")
        self.root.configure(bg="white")
        self.font_style = ("Helvetica", 10)

        # Create the toolbar
        self.toolbar = tk.Frame(root, bg="#e0e0e0", height=40)
        self.toolbar.pack(side="top", fill="x")

        # File menu button
        self.file_menu_button = tk.Menubutton(
            self.toolbar,
            text="File",
            font=self.font_style,
            bg="#e0e0e0",
            fg="black",
            bd=0,
            padx=20,
            pady=5
        )
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0)
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
            bg="#e0e0e0",
            fg="black",
            bd=0,
            padx=20,
            pady=5
        )
        self.data_menu = tk.Menu(self.data_menu_button, tearoff=0)
        self.data_menu.add_command(
            label="Remove rows with NaN",
            command=lambda: self.handle_nan(option="1")
        )
        self.data_menu.add_command(
            label="Fill with Mean",
            command=lambda: self.handle_nan(option="2")
        )
        self.data_menu.add_command(
            label="Fill with Median",
            command=lambda: self.handle_nan(option="3")
        )
        self.data_menu.add_command(
            label="Fill with Constant",
            command=lambda: self.handle_nan(option="4")
        )
        self.data_menu_button.config(menu=self.data_menu)
        self.data_menu_button.pack(side="left", padx=2)

        # Label to display the selected file path
        self.file_path_label = tk.Label(
            root,
            text="No file selected",
            font=self.font_style,
            bg="white",
            fg="black"
        )
        self.file_path_label.pack(pady=10)

        # Frame for the data table
        self.table_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.table_frame_border.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.table_frame = tk.Frame(
            self.table_frame_border, bg="#f9f9f9"
                                    )
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for regression controls
        self.controls_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.controls_frame_border.pack(
            side="left", fill="y", padx=10, pady=5
            )
        self.controls_frame = tk.Frame(
            self.controls_frame_border, bg="#f9f9f9"
            )
        self.controls_frame.pack(fill="both", padx=5, pady=5)

        # Content of the regression control section
        input_label = tk.Label(
            self.controls_frame,
            text="Select input column:",
            font=self.font_style,
            bg="#f9f9f9"
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
            bg="#f9f9f9"
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
            bg="#f9f9f9"
        )
        description_label.pack(anchor="w", padx=10, pady=5)
        self.dtext = tk.Text(
            self.controls_frame, height=4, width=30
            )
        self.dtext.pack(padx=10, pady=5)

        create_button = tk.Button(
            self.controls_frame,
            text="Create Model",
            command=self.create_regression_model,
            font=self.font_style
        )
        create_button.pack(pady=10)

        save_button = tk.Button(
            self.controls_frame,
            text="Save Model",
            command=self.save_model,
            font=self.font_style
        )
        save_button.pack(pady=5)

        # Section to display results
        self.result_label = tk.Label(
            self.controls_frame,
            text="",
            font=self.font_style,
            fg="blue",
            justify="left",
            bg="#f9f9f9"
        )
        self.result_label.pack(pady=10)

        # Frame for the graph
        self.graph_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.graph_frame_border.pack(
            side="right",
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )
        self.graph_frame = tk.Frame(self.graph_frame_border, bg="#f9f9f9")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Initialization of variables
        self.df = None
        self.selected_input = None
        self.selected_output = None
        self.model_description = ""
        self.model = None

    def load_file(self):
        """Loads a data file and processes it."""
        file_types = [
            ("CSV Files", ".csv"),
            ("Excel Files", ".xlsx .xls"),
            ("SQLite Files", ".sqlite *.db")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.file_path_label.config(text=file_path)

            # If model details frame exists, destroy it
            if hasattr(self, 'model_details') and self.model_details:
                self.model_details.destroy()

            # Ensure data components are visible
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
            threading.Thread(
                target=self.process_import,
                args=(file_path,)
            ).start()

            # Reset the selectors and description
            self.reset_controls()

            # Clear the graph
            self.clear_graph()

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

    def process_import(self, file_path):
        """Processes the import of the selected file."""
        try:
            # Check file size before importing
            if os.path.getsize(file_path) == 0:
                raise ValueError(
                    "The selected file is empty (size is zero bytes)."
                    )

            # Import the file
            self.df = modulo_importacion.import_file(file_path)

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

        # Détruire tout widget existant dans le cadre de la table
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Créer les barres de défilement verticales et horizontales
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        # Créer la vue en arbre pour afficher les données
        self.table = ttk.Treeview(
            self.table_frame,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            style="Treeview"
        )
        self.table.pack(fill=tk.BOTH, expand=True)

        # Configurer les barres de défilement
        vsb.config(command=self.table.yview)
        hsb.config(command=self.table.xview)

        # Configurer les colonnes de la table
        self.table["columns"] = list(self.df.columns)
        self.table["show"] = "headings"

        for col in self.df.columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=100)

        # Insérer les données dans la table
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
            numeric_columns = self.data_frame.select_dtypes(
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
                    self.data_frame[col] = self.data_frame[col].fillna(
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


    def get_decimal_places(self, series):
        """Returns the maximum number of decimal places in the series."""
        decimals = series.dropna().astype(str).str.split('.').str[1]  # Get the decimal part
        return decimals.str.len().max() if not decimals.empty else 0

    def create_regression_model(self):
        """Creates a linear regression model using the selected columns."""
        if self.df is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        self.selected_input = self.input_selector.get()
        self.selected_output = self.output_selector.get()

        if not self.selected_input or not self.selected_output:
            messagebox.showwarning(
                "Warning", "No columns selected for regression."
                )
            return

        self.model_description = self.dtext.get("1.0", "end-1c").strip()
        if not self.model_description:
            proceed = messagebox.askyesno(
                "Missing Description",
                "No model description provided. Do you want to continue?"
            )
            if not proceed:
                return

        try:
            X = self.df[[self.selected_input]].values
            y = self.df[self.selected_output].values

            self.model = LinearRegression()
            self.model.fit(X, y)
            predictions = self.model.predict(X)
            mse = mean_squared_error(y, predictions)
            r2 = r2_score(y, predictions)

            intercept = self.model.intercept_
            coef = self.model.coef_[0]
            formula = (
                f"{self.selected_output} = {coef:.2f} * {self.selected_input}"
                f"+ {intercept:.2f}"
            )
            self.result_label.config(
                text=f"Formula: {formula}\nR²: {r2:.2f}\nMSE: {mse:.2f}"
            )

            # Clear previous graph
            self.clear_graph()

            # Create and display the graph
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(X, y, color="blue", label="Data Points")
            ax.plot(X, predictions, color="red", label="Regression Line")
            ax.set_xlabel(self.selected_input)
            ax.set_ylabel(self.selected_output)
            ax.legend()
            ax.set_title("Regression Line")

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred while creating the model: {e}"
            )

    def save_model(self):
        """Saves the linear regression model data to a file."""
        if self.model is None:
            messagebox.showwarning(
                "Warning",
                "No model has been created to save."
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pkl",
            filetypes=[
                ("Pickle files", "*.pkl"),
                ("Joblib files", "*.joblib")
            ]
        )
        if not file_path:
            return  # Exit if no file is selected

        try:
            # Prepare the data to save
            model_data = {
                'input_column': self.selected_input,
                'output_column': self.selected_output,
                'model_description': self.model_description,
                'formula': (
                    f"{self.selected_output} = {self.model.coef_[0]:.2f}"
                    f"* {self.selected_input} + {self.model.intercept_:.2f}"
                ),
                'metrics': {
                    'R²': round(
                        r2_score(
                            self.df[self.selected_output],
                            self.model.predict(self.df[[self.selected_input]])
                        ),
                        2
                    ),
                    'MSE': round(
                        mean_squared_error(
                            self.df[self.selected_output],
                            self.model.predict(self.df[[self.selected_input]])
                        ),
                        2
                    )
                }
            }

            # Save the model data
            joblib.dump(model_data, file_path)
            messagebox.showinfo(
                "Success",
                f"Model data saved successfully at {file_path}."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred while saving the model: {e}"
            )

    def load_model(self):
        """Load a saved model and update the interface accordingly."""
        while True:
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Pickle files", "*.pkl"),
                    ("Joblib files", "*.joblib")
                ]
            )
            if not file_path:
                break  # Exit if no file is selected

            try:
                # Load the model
                model_data = joblib.load(file_path)

                # Extract model information
                self.selected_input = model_data['input_column']
                self.selected_output = model_data['output_column']
                self.model_description = model_data.get(
                    'model_description',
                    'No description provided'
                )
                formula = model_data['formula']
                r2 = model_data['metrics']['R²']
                mse = model_data['metrics']['MSE']

                # Update the interface to display the model information
                self.update_interface_for_model(formula, r2, mse)

                # Reset controls
                self.reset_controls()

                # Confirmation message
                messagebox.showinfo("Success", "Model loaded successfully.")
                break  # Exit the loop after successful load

            except Exception as e:
                error_message = f"Error while loading the model: {str(e)}"
                retry = messagebox.askretrycancel(
                    "Error",
                    f"{error_message}\n\nMaybe try loading another file?"
                )
                if not retry:
                    break  

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


if __name__ == "__main__":
    root = tk.Tk()
    app = DataLoaderApp(root)
    root.mainloop()
