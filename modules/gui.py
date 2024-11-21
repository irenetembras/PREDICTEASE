import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
class DataLoaderApp:
    """
    Application to load and visualize data, manage NaNs, and create a
    linear regression model with error metrics.
    """
    # Import necessary functions for operations.
    
    from modules.data_operations import (
        process_import,
        display_data,
        handle_nan,
        populate_selectors
    )

    from modules.main_window import (
        reset_controls, 
        clear_graph,  
        update_interface_for_model, 
    )
    

    def __init__(self, root):
        root.state('zoomed')
        self.root = root
        self.root.title("Data Loader")
        self.root.configure(bg="white")
        self.font_style = ("Helvetica", 10)

        # Create the toolbar at the top of the window.
        self.toolbar = tk.Frame(root, bg="#e0e0e0", height=40)
        self.toolbar.pack(side="top", fill="x")

        # File menu button setup.
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

        # Data menu button setup for NaN management.
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
        # Adding commands to handle NaN values in the dataset.
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

        # Label to display the selected file path.
        self.file_path_label = tk.Label(
            root,
            text="No file selected",
            font=self.font_style,
            bg="white",
            fg="black"
        )
        self.file_path_label.pack(pady=10)

        # Frame for the data table.
        self.table_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.table_frame_border.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.table_frame = tk.Frame(self.table_frame_border, bg="#f9f9f9")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for regression controls on the left side.
        self.controls_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.controls_frame_border.pack(side="left", fill="y", padx=10, pady=5)
        self.controls_frame = tk.Frame(self.controls_frame_border, bg="#f9f9f9")
        self.controls_frame.pack(fill="both", padx=5, pady=5)

        # Input column selector.
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

        # Output column selector.
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

        # Model description input (optional).
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

        # Button to create regression model.
        create_button = tk.Button(
            self.controls_frame,
            text="Create Model",
            command=self.create_regression_model,
            font=self.font_style
        )
        create_button.pack(pady=10)

        # Button to save the model.
        save_button = tk.Button(
            self.controls_frame,
            text="Save Model",
            command=self.save_model,
            font=self.font_style
        )
        save_button.pack(pady=5)

        # Section to display results after model is created.
        self.result_label = tk.Label(
            self.controls_frame,
            text="",
            font=self.font_style,
            fg="blue",
            justify="center",
            bg="#f9f9f9",
            height=6,
            width=40,
            anchor="center",
            wraplength=380
        )
        self.result_label.pack(pady=10)

        # Frame for the graph visualization on the right side.
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

        # Initialization of variables.
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

            # If model details frame exists, destroy it.
            if hasattr(self, 'model_details') and self.model_details:
                self.model_details.destroy()

            # Make sure data components are visible.
            self.file_path_label.pack(pady=10)
            self.table_frame_border.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            self.controls_frame_border.pack(side="left", fill="y", padx=10, pady=5)
            self.graph_frame_border.pack(side="right", fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Start processing the file in a separate thread.
            threading.Thread(
                target=self.process_import,
                args=(file_path,)
            ).start()

            # Reset the selectors and description.
            self.reset_controls()

            # Clear the graph.
            self.clear_graph()

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
                f" + {intercept:.2f}"
            )
            self.result_label.config(
                text=f"Formula: {formula}\nR²: {r2:.2f}\nMSE: {mse:.2f}"
            )

            # Clear previous graph to avoid overlap with new one.
            self.clear_graph()

            # Create and display the regression line plot.
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(X, y, color="blue", label="Data Points")
            ax.plot(X, predictions, color="red", label="Regression Line")
            ax.set_xlabel(self.selected_input)
            ax.set_ylabel(self.selected_output)
            ax.legend()
            ax.set_title("Regression Line")

            # Embed the plot in the Tkinter window.
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

        # Prompt user to select a file path to save the model.
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pkl",
            filetypes=[
                ("Pickle files", "*.pkl"),
                ("Joblib files", "*.joblib")
            ]
        )
        if not file_path:
            return  # Exit if no file is selected.

        try:
            # Prepare model data for saving.
            model_data = {
                'input_column': self.selected_input,
                'output_column': self.selected_output,
                'model_description': self.model_description,
                'formula': (
                    f"{self.selected_output} = {self.model.coef_[0]:.2f}"
                    f" * {self.selected_input} + {self.model.intercept_:.2f}"
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

            # Save model data to the selected file path.
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
            # Prompt user to select a file to load.
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Pickle files", "*.pkl"),
                    ("Joblib files", "*.joblib")
                ]
            )
            if not file_path:
                break  # Exit if no file is selected.

            try:
                # Load the model from the selected file.
                model_data = joblib.load(file_path)

                # Extract and update model information.
                self.selected_input = model_data['input_column']
                self.selected_output = model_data['output_column']
                self.model_description = model_data.get(
                    'model_description',
                    'No description provided'
                )
                formula = model_data['formula']
                r2 = model_data['metrics']['R²']
                mse = model_data['metrics']['MSE']

                # Update the interface to display the model information.
                self.update_interface_for_model(formula, r2, mse)

                # Reset the controls to default.
                self.reset_controls()

                # Confirmation message after successfully loading the model.
                messagebox.showinfo("Success", "Model loaded successfully.")
                break  # Exit the loop after successful load.

            except Exception as e:
                error_message = f"Error while loading the model: {str(e)}"
                retry = messagebox.askretrycancel(
                    "Error",
                    f"{error_message}\n\nMaybe try loading another file?"
                )
                if not retry:
                    break

    def update_interface_for_model(self, formula, r2, mse):
            """
            Actualiza la interfaz para mostrar los detalles del modelo cargado.

            :param formula: La fórmula del modelo cargado.
            :param r2: El valor de R² (coeficiente de determinación) del modelo.
            :param mse: El valor de MSE (error cuadrático medio) del modelo.
            """
            # Elimina los detalles anteriores del modelo si existen.
            if hasattr(self, 'model_details') and self.model_details:
                self.model_details.destroy()

                # Oculta secciones innecesarias de la interfaz.
                self.file_path_label.pack_forget()
                self.table_frame_border.pack_forget()
                self.controls_frame_border.pack_forget()
                self.graph_frame_border.pack_forget()

                # Crea un nuevo marco para mostrar los detalles del modelo.
                self.model_details = tk.Frame(self.root, bg="white")
                self.model_details.pack(fill=tk.BOTH, expand=True)

                # Prepara la información del modelo en formato texto.
                model_info = (
                    f"Formula: {formula}\n"
                    f"R²: {r2}\n"
                    f"MSE: {mse}\n\n"
                    f"Description: {self.model_description}"
                )

                # Crea una etiqueta para mostrar los detalles del modelo.
                model_info_label = tk.Label(
                    self.model_details,
                    text=model_info,
                    font=("Helvetica", 12),
                    fg="black",
                    justify="center",
                    bg="white"
                )
                model_info_label.pack(pady=10, expand=True)