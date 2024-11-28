import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib
matplotlib.use('TkAgg')
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
        clear_graph 
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

                # Help menu button setup.
        self.help_menu_button = tk.Menubutton(
            self.toolbar,
            text="Help",  # Texto del botón
            font=self.font_style,
            bg="#e0e0e0",
            fg="black",
            bd=0,
            padx=20,
            pady=5
        )
        self.help_menu = tk.Menu(self.help_menu_button, tearoff=0)  
        self.help_menu.add_command(
            label="Tutorial",  
            command=self.display_tutorial 
        )
        self.help_menu_button.config(menu=self.help_menu)
        self.help_menu_button.pack(side="left", padx=2)  

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
        self.table_frame_border.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5)
        self.table_frame = tk.Frame(self.table_frame_border, bg="#f9f9f9")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for regression controls on the left side.
        self.controls_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.controls_frame_border.pack(side="left", fill="y", padx=10, pady=5)
        self.controls_frame = tk.Frame(self.controls_frame_border,
                                       bg="#f9f9f9")
        self.controls_frame.pack(fill=tk.BOTH, expand=True)

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
        self.result_label = tk.Label(self.root, text="Resultado de la predicción", font=('Arial', 12))
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
        self.input_fields = []
        self.dynamic_widgets = []

        messagebox.showinfo(
            "Welcome to Data Loader",
            "Welcome to the Data Loader application!\n\n"
            "This tool allows you to:\n"
            "1. Load and Visualize Data\n"
            "2. Manage Missing Values\n"
            "3. Create Linear Regression Models\n"
            "4. Save and Load Models\n\n"
            "To get started:\n"
            "Navigate to the 'Help' and click 'Tutorial'.\n"
        )
        self.prediction_frame = tk.Frame(root, bg="white")
        self.input_fields_frame = tk.Frame(self.prediction_frame, bg="white")
        self.input_fields_frame.pack(pady=10)

        self.prediction_result_label = tk.Label(
            self.prediction_frame,
            text="",
            bg="white",
            font=("Helvetica", 10)
        )
        self.prediction_result_label.pack(pady=5)

        # Configura el botón de predicción
        self.setup_prediction_button()

        # Inicialmente, el marco de predicción está oculto
        self.prediction_frame.pack_forget()

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
            self.table_frame_border.pack(fill=tk.BOTH,
                                         expand=True,
                                         padx=10,
                                         pady=5)
            self.controls_frame_border.pack(side="left",
                                            fill="y",
                                            padx=10,
                                            pady=5)
            self.graph_frame_border.pack(side="right",
                                         fill=tk.BOTH,
                                         expand=True,
                                         padx=10,
                                         pady=5)

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
        """Carga un modelo guardado y actualiza la interfaz en consecuencia."""
        # Limpiar campos de entrada antiguos
        self.clear_dynamic_widgets()

        while True:
            file_path = filedialog.askopenfilename(
                filetypes=[("Archivos Pickle", "*.pkl"), ("Archivos Joblib", "*.joblib")]
            )
            if not file_path:
                break  # Salir si no se selecciona un archivo

            try:
                # Cargar el modelo
                model_data = joblib.load(file_path)

                # Extraer información del modelo
                self.selected_input = model_data['input_column']
                self.selected_output = model_data['output_column']
                self.model_description = model_data.get('model_description', 'No hay descripción')
                formula = model_data['formula']
                r2 = model_data['metrics']['R²']
                mse = model_data['metrics']['MSE']

                # Asignar el modelo cargado a self.model
                self.model = model_data['model_object']  # Aquí es donde se carga el modelo completo

                # Verifica si el modelo se cargó correctamente
                if self.model is not None:
                    print(f"Modelo cargado correctamente: {self.model}")
                else:
                    print("Error: El modelo no se cargó correctamente.")

                # Actualizar la interfaz para mostrar la información del modelo
                self.update_interface_for_model(formula, r2, mse)

                # Confirmar que el modelo se cargó correctamente
                messagebox.showinfo("Éxito", "Modelo cargado correctamente.")
                break  # Salir del bucle después de cargar el modelo correctamente

            except Exception as e:
                error_message = f"Error al cargar el modelo: {str(e)}"
                retry = messagebox.askretrycancel("Error", f"{error_message}\n\n¿Quieres intentar cargar otro archivo?")
                if not retry:
                    break
        if self.selected_input:
            self.toggle_prediction(True)
            self.generate_input_fields()
            self.predict_button.config(state=tk.NORMAL)

    def clear_dynamic_widgets(self):
        """Destroy all dynamically created widgets."""
        if hasattr(self, 'dynamic_widgets'):
            for widget in self.dynamic_widgets:
                try:
                    widget.destroy()
                except Exception as e:
                    print(f"Error destroying widget: {e}")

            self.dynamic_widgets = []



    def display_tutorial(self):
        """Displays frequently asked questions."""
        messagebox.showinfo(
            "Tutorial",
            "Welcome to the step-by-step tutorial!\n\n"
            "Step 1: Start by loading a dataset.\n"
            "   -Use the 'File' button, then click 'Load Dataset' to select a file from your device.\n"
            "   -Once the dataset is loaded, you'll be able to view the data on screen.\n\n"
            "Step 2: Fill in any missing (NaN) values.\n"
            "   -Use the options available in the 'Data' button.\n\n"
            "Step 3: Create a linear regression model.\n"
            "   -Select input/output columns and description (optional) and then click 'Create Model'.\n\n"
            "Step 4: Save your model to your device.\n"
            "   -Click 'Save Model' to store the model for later use.\n\n"
            "Step 5: Load a previously saved model.\n"
            "   -Use the 'File' button, and then click 'Load Model' to load a model from your device.\n\n"
            "Congratulations, you have completed the tutorial!\n"
        )

    def show_loading_indicator(self, message):
        """
        Displays a larger, centered loading indicator window with a progress bar.
        
        Parameters:
        - message (str): The message to display above the progress bar.
        """
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Loading")
        self.loading_window.resizable(False, False)
        self.loading_window.grab_set()  # Prevent interaction with the main window

        # Define the size of the window
        width = 500  # Increased width
        height = 200  # Increased height

        # Calculate x and y coordinates to center the window
        screen_width = self.loading_window.winfo_screenwidth()
        screen_height = self.loading_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the geometry of the window
        self.loading_window.geometry(f"{width}x{height}+{x}+{y}")

        # Create and pack the message label
        label = tk.Label(self.loading_window, text=message, font=("Helvetica", 12))
        label.pack(pady=30)

        # Create and pack the progress bar
        progress = ttk.Progressbar(self.loading_window, mode='indeterminate', length=400)
        progress.pack(pady=20)
        progress.start(10)  # Adjust the speed as needed

    def hide_loading_indicator(self):
        """
        Closes the loading indicator window.
        """
        if hasattr(self, 'loading_window') and self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None

    def create_regression_model(self):
        """Crea un modelo de regresión lineal usando las columnas seleccionadas."""
        if self.df is None:
            messagebox.showwarning("Warning", "No se ha cargado ningún conjunto de datos.")
            return

        self.selected_input = self.input_selector.get()
        self.selected_output = self.output_selector.get()

        if not self.selected_input or not self.selected_output:
            messagebox.showwarning("Warning", "No se han seleccionado las columnas para la regresión.")
            return

        self.model_description = self.dtext.get("1.0", "end-1c").strip()
        if not self.model_description:
            proceed = messagebox.askyesno("Descripción faltante", 
                                          "No se ha proporcionado una descripción del modelo. ¿Deseas continuar?")
            if not proceed:
                return

        self.show_loading_indicator("Creando modelo de regresión, por favor espera...")

        # Crear el modelo en un hilo separado para no bloquear la interfaz de usuario
        threading.Thread(target=self._create_model_thread).start()

        # Verifica que el modelo está disponible
        if self.selected_input:
            self.toggle_prediction(True)
            self.generate_input_fields()
            self.predict_button.config(state=tk.NORMAL)

    def _create_model_thread(self):
        """
        Función en hilo separado para crear el modelo de regresión.
        Esto asegura que la interfaz de usuario siga siendo responsive.
        """
        try:
            X = self.df[[self.selected_input]].values
            y = self.df[self.selected_output].values

            # Crear el modelo de regresión
            self.model = LinearRegression()
            self.model.fit(X, y)

            predictions = self.model.predict(X)
            mse = mean_squared_error(y, predictions)
            r2 = r2_score(y, predictions)

            intercept = self.model.intercept_
            coef = self.model.coef_[0]
            formula = f"{self.selected_output} = {coef:.2f} * {self.selected_input} + {intercept:.2f}"
            result_text = f"Fórmula: {formula}\nR²: {r2:.2f}\nMSE: {mse:.2f}"

            # Actualiza la interfaz con los resultados
            self.root.after(0, lambda: self.result_label.config(text=result_text))

            # Crea y muestra la línea de regresión
            self.root.after(0, self.clear_graph)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(X, y, color="blue", label="Puntos de datos")
            ax.plot(X, predictions, color="red", label="Línea de regresión")
            ax.set_xlabel(self.selected_input)
            ax.set_ylabel(self.selected_output)
            ax.legend()
            ax.set_title("Línea de regresión")

            # Embebe el gráfico en la interfaz de Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            self.root.after(0, lambda: canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True))

            # Mensaje de éxito
            self.root.after(0, lambda: messagebox.showinfo("Éxito", "Modelo de regresión creado correctamente."))

        except Exception as e:
            error_message = f"Se produjo un error al crear el modelo: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))

        finally:
            # Ocultar el indicador de carga independientemente de si fue exitoso o no
            self.root.after(0, self.hide_loading_indicator)


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
                },
                'model_object': self.model  # Aquí se guarda el modelo completo.
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

    def toggle_prediction(self, enable=True):
        """
        Habilita o deshabilita la funcionalidad de predicción.
        """
        if enable:
            self.prediction_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.prediction_frame.pack_forget()

    def generate_input_fields(self):
        """Genera los campos de entrada para cada variable seleccionada."""
        # Limpiar widgets anteriores si existen.
        self.clear_dynamic_widgets()  # Limpia cualquier widget previo (campos de entrada, etc.)
    
        # Verifica si ya existen campos de entrada
        if hasattr(self, 'input_fields') and self.input_fields:
            self.input_fields.clear()  # Borra los campos previos

        # Aquí añadimos un campo de entrada para la columna seleccionada.
        input_label = tk.Label(
            self.prediction_frame,
            text=f"Ingrese valor para '{self.selected_input}':",
            font=self.font_style
        )
        input_label.pack(pady=5)

        input_entry = tk.Entry(self.prediction_frame, font=self.font_style)
        input_entry.pack(pady=5, fill=tk.X, padx=10)

        # Guarda la entrada dinámica para usarla más tarde
        self.input_fields.append(input_entry)  # Añadimos el campo de entrada a la lista.

        # Habilita el botón de predicción
        self.predict_button.config(state=tk.NORMAL)

        # Imprimir para depuración
        print(f"Campos de entrada generados: {len(self.input_fields)}")


    def setup_prediction_button(self):
        """
        Configura el botón para realizar predicciones.
        """
        self.predict_button = tk.Button(
            self.prediction_frame, 
            text="Realizar Predicción", 
            command=self.make_prediction, 
            state=tk.DISABLED
        )
        self.predict_button.pack(pady=10)
        

    def make_prediction(self):
        """Realiza la predicción utilizando los valores de entrada proporcionados."""
        try:
            # Verificar si el modelo está presente antes de predecir
            if not self.model:
                print("ERROR: No se ha configurado un modelo válido para la predicción.")
                messagebox.showerror("Error", "No se ha configurado un modelo válido para la predicción.")
                return

            # Recupera los valores de los campos de entrada
            input_values = []
            for entry in self.input_fields:  # Se asume que input_fields es una lista de widgets de entrada
                try:
                    input_values.append(float(entry.get()))  # Convierte cada valor a float
                except ValueError:
                    raise ValueError("Todos los campos de entrada deben ser numéricos.")

            print(f"Valores de entrada: {input_values}")

            # Realiza la predicción
            prediction = self.model.predict([input_values])  # El modelo recibe una lista de entradas
            print(f"Predicción: {prediction[0]}")

            # Muestra la predicción en la interfaz
            self.result_label.config(text=f"Predicción: {prediction[0]}")

        except ValueError as e:
            messagebox.showerror("Error", f"Valor de entrada no válido: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error al hacer la predicción: {str(e)}")
