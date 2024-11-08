import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import joblib
import modulo_importacion  

class DataLoaderApp:
    """Application to load and visualize data, manage NaNs, and create a linear regression model with error metrics."""

    def __init__(self, root):
        root.state('zoomed')  # Maximiza la ventana
        self.root = root
        self.root.title("Data Loader")  # Título de la ventana
        self.root.configure(bg="white")  # Fondo blanco para la ventana
        self.font_style = ("Helvetica", 10)  # Estilo de fuente

        # Crear la barra de herramientas
        self.toolbar = tk.Frame(root, bg="#e0e0e0", height=40)
        self.toolbar.pack(side="top", fill="x")  # Empaqueta la barra en la parte superior

        # Botón de menú de archivo
        self.file_menu_button = tk.Menubutton(self.toolbar, text="File", font=self.font_style, bg="#e0e0e0", fg="black", bd=0, padx=20, pady=5)
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0)
        self.file_menu.add_command(label="Load Dataset", command=self.load_file)  # Opción para cargar datos
        self.file_menu.add_separator()  # Separador en el menú
        self.file_menu.add_command(label="Exit", command=self.root.quit)  # Opción para salir
        self.file_menu_button.config(menu=self.file_menu)  # Configura el menú
        self.file_menu_button.pack(side="left", padx=10)  # Empaqueta el botón en la barra de herramientas

        # Botón de menú de datos
        self.data_menu_button = tk.Menubutton(self.toolbar, text="Data", font=self.font_style, bg="#e0e0e0", fg="black", bd=0, padx=20, pady=5)
        self.data_menu = tk.Menu(self.data_menu_button, tearoff=0)
        self.data_menu.add_command(label="Remove rows with NaN", command=lambda: self.handle_nan(option="1"))  # Opción para eliminar NaN
        self.data_menu.add_command(label="Fill with Mean", command=lambda: self.handle_nan(option="2"))  # Opción para rellenar con media
        self.data_menu.add_command(label="Fill with Median", command=lambda: self.handle_nan(option="3"))  # Opción para rellenar con mediana
        self.data_menu.add_command(label="Fill with Constant", command=lambda: self.handle_nan(option="4"))  # Opción para rellenar con constante
        self.data_menu_button.config(menu=self.data_menu)  # Configura el menú
        self.data_menu_button.pack(side="left", padx=2)  # Empaqueta el botón en la barra de herramientas

        # Etiqueta para mostrar la ruta del archivo seleccionado
        self.file_path_label = tk.Label(root, text="No file selected", font=self.font_style, bg="white", fg="black")
        self.file_path_label.pack(pady=10)  # Empaqueta la etiqueta

        # Frame para la tabla de datos
        self.table_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.table_frame_border.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.table_frame = tk.Frame(self.table_frame_border, bg="#f9f9f9")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame para controles de regresión
        self.controls_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.controls_frame_border.pack(side="left", fill="y", padx=10, pady=5)
        self.controls_frame = tk.Frame(self.controls_frame_border, bg="#f9f9f9")
        self.controls_frame.pack(fill="both", padx=5, pady=5)

        # Contenido de la sección de control de regresión
        input_label = tk.Label(self.controls_frame, text="Select input column:", font=self.font_style, bg="#f9f9f9")
        input_label.pack(anchor="w", padx=10, pady=5)  # Etiqueta para columna de entrada
        self.input_selector = ttk.Combobox(self.controls_frame, state="readonly")  # Selector de columna de entrada
        self.input_selector.pack(fill=tk.X, padx=10, pady=5)

        output_label = tk.Label(self.controls_frame, text="Select output column:", font=self.font_style, bg="#f9f9f9")
        output_label.pack(anchor="w", padx=10, pady=5)  # Etiqueta para columna de salida
        self.output_selector = ttk.Combobox(self.controls_frame, state="readonly")  # Selector de columna de salida
        self.output_selector.pack(fill=tk.X, padx=10, pady=5)

        description_label = tk.Label(self.controls_frame, text="Enter model description (optional):", font=self.font_style, bg="#f9f9f9")
        description_label.pack(anchor="w", padx=10, pady=5)  # Etiqueta para descripción
        self.description_text = tk.Text(self.controls_frame, height=4, width=30)  # Caja de texto para descripción
        self.description_text.pack(padx=10, pady=5)

        create_button = tk.Button(self.controls_frame, text="Create Model", command=self.create_regression_model, font=self.font_style)  # Botón para crear modelo
        create_button.pack(pady=10)

        save_button = tk.Button(self.controls_frame, text="Save Model", command=self.save_model, font=self.font_style)  # Botón para guardar modelo
        save_button.pack(pady=5)

        # Sección para mostrar resultados
        self.result_label = tk.Label(self.controls_frame, text="", font=self.font_style, fg="blue", justify="left", bg="#f9f9f9")
        self.result_label.pack(pady=10)

        # Frame para el gráfico
        self.graph_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.graph_frame_border.pack(side="right", fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.graph_frame = tk.Frame(self.graph_frame_border, bg="#f9f9f9")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Inicialización de variables
        self.data_frame = None  # DataFrame para almacenar datos
        self.selected_input = None  # Columna de entrada seleccionada
        self.selected_output = None  # Columna de salida seleccionada
        self.model_description = ""  # Descripción del modelo
        self.model = None  # Modelo de regresión

    def load_file(self):
        """Loads a data file and processes it."""
        file_types = [("CSV Files", ".csv"), ("Excel Files", ".xlsx .xls"), ("SQLite Files", ".sqlite *.db")]
        file_path = filedialog.askopenfilename(filetypes=file_types)  # Diálogo de selección de archivo
        if file_path:  # Si se selecciona un archivo
            self.file_path_label.config(text=file_path)  # Actualiza la etiqueta con la ruta del archivo
            threading.Thread(target=self.process_import, args=(file_path,)).start()  # Carga el archivo en un hilo separado

    def process_import(self, file_path):
        """Processes the import of the selected file."""
        try:
            self.data_frame = modulo_importacion.importar_archivo(file_path)  # Utiliser le module importado
            if self.data_frame.empty:
                raise ValueError("Le fichier est vide.")
            self.root.after(0, self.display_data)  # Muestra los datos en la tabla
            self.root.after(0, self.populate_selectors)  # Llena los selectores de columna
            self.root.after(0, lambda: messagebox.showinfo("Success", "File loaded successfully."))  # Muestra mensaje de éxito
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))  # Manejo de errores

    def populate_selectors(self):
        """Fills the column selectors with the columns from the DataFrame."""
        if self.data_frame is not None:
            columns = list(self.data_frame.columns)
            self.input_selector['values'] = columns  # Llena el selector de entrada con columnas
            self.output_selector['values'] = columns  # Llena el selector de salida con columnas

    def display_data(self):
        """Displays the data in a table."""
        for widget in self.table_frame.winfo_children():
            widget.destroy()  # Limpia la tabla antes de mostrar nuevos datos
        
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical")  # Barra de desplazamiento vertical
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")  # Barra de desplazamiento horizontal
        hsb.pack(side='bottom', fill='x')
        
        self.table = ttk.Treeview(self.table_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set, style="Treeview")  # Tabla para mostrar datos
        self.table.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.table.yview)  # Configura la barra de desplazamiento vertical
        hsb.config(command=self.table.xview)  # Configura la barra de desplazamiento horizontal
        
        self.table["columns"] = list(self.data_frame.columns)
        self.table["show"] = "headings"
        
        for col in self.data_frame.columns:
            self.table.heading(col, text=col)  # Configura los encabezados de columna
            self.table.column(col, anchor="center", width=100)  # Centra el texto en las columnas
        
        for _, row in self.data_frame.iterrows():
            self.table.insert("", "end", values=list(row))  # Inserta filas en la tabla

    def handle_nan(self, option):
        """Handles NaN values in the DataFrame based on the selected option."""
        if self.data_frame is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        # Filtrer uniquement les colonnes numériques
        numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns

        if option == "1":
            # Supprimer les lignes contenant des NaN
            self.data_frame = self.data_frame.dropna()
            messagebox.showinfo("Success", "Rows with NaN values removed.")

        elif option == "2":
            for col in numeric_columns:
                # Vérifier si la colonne contient des données et est numérique
                if pd.api.types.is_numeric_dtype(self.data_frame[col]) and not self.data_frame[col].dropna().empty:
                    mean_value = self.data_frame[col].mean()
                    # Vérifier qu'il y a bien des décimales
                    first_non_nan = str(self.data_frame[col].dropna().iloc[0])
                    if '.' in first_non_nan:
                        decimals = len(first_non_nan.split(".")[1])
                    else:
                        decimals = 0  # Pas de décimales dans cette colonne
                    self.data_frame[col] = self.data_frame[col].fillna(round(mean_value, decimals))
            messagebox.showinfo("Success", "NaN values filled with column mean.")

        elif option == "3":
            for col in numeric_columns:
                if pd.api.types.is_numeric_dtype(self.data_frame[col]) and not self.data_frame[col].dropna().empty:
                    median_value = self.data_frame[col].median()
                    # Vérifier qu'il y a bien des décimales
                    first_non_nan = str(self.data_frame[col].dropna().iloc[0])
                    if '.' in first_non_nan:
                        decimals = len(first_non_nan.split(".")[1])
                    else:
                        decimals = 0  # Pas de décimales dans cette colonne
                    self.data_frame[col] = self.data_frame[col].fillna(round(median_value, decimals))
            messagebox.showinfo("Success", "NaN values filled with column median.")

        elif option == "4":
            constant_value = simpledialog.askstring("Input", "Enter a constant value:")
            if constant_value is not None:
                try:
                    constant_value = float(constant_value)
                    self.data_frame = self.data_frame.fillna(constant_value)
                    messagebox.showinfo("Success", f"NaN values filled with constant value: {constant_value}")
                except ValueError:
                    messagebox.showerror("Error", "Invalid constant value entered.")

        # Afficher les données mises à jour
        self.display_data()



    def create_regression_model(self):
        """Creates a linear regression model using the selected columns."""
        if self.data_frame is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        # Obtén las columnas seleccionadas de los comboboxes
        self.selected_input = self.input_selector.get()
        self.selected_output = self.output_selector.get()
        
        if not self.selected_input or not self.selected_output:
            messagebox.showwarning("Warning", "No columns selected for regression.")
            return

        # Verifica si la descripción está vacía
        self.model_description = self.description_text.get("1.0", "end-1c").strip()
        if not self.model_description:
            proceed = messagebox.askyesno("Missing Description", "No model description provided. Do you want to continue?")
            if not proceed:
                return

        try:
            X = self.data_frame[[self.selected_input]].values  # Valores de la columna de entrada
            y = self.data_frame[self.selected_output].values  # Valores de la columna de salida

            self.model = LinearRegression()  # Crea modelo de regresión
            self.model.fit(X, y)  # Ajusta el modelo a los datos
            predictions = self.model.predict(X)  # Realiza predicciones
            mse = mean_squared_error(y, predictions)  # Calcula el error cuadrático medio
            r2 = r2_score(y, predictions)  # Calcula el valor R²

            intercept = self.model.intercept_  # Intercepto del modelo
            coef = self.model.coef_[0]  # Coeficiente del modelo
            formula = f"{self.selected_output} = {coef:.2f} * {self.selected_input} + {intercept:.2f}"  # Fórmula del modelo
            self.result_label.config(text=f"Formula: {formula}\nR²: {r2:.2f}\nMSE: {mse:.2f}")  # Muestra resultados

            # Limpia gráficos existentes en la sección de gráficos
            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            # Crea el gráfico
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(X, y, color="blue", label="Data Points")  # Puntos de datos
            ax.plot(X, predictions, color="red", label="Regression Line")  # Línea de regresión
            ax.set_xlabel(self.selected_input)  # Etiqueta eje X
            ax.set_ylabel(self.selected_output)  # Etiqueta eje Y
            ax.legend()  # Leyenda
            ax.set_title("Regression Line")  # Título del gráfico

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)  # Crea un canvas para el gráfico
            canvas.draw()  # Dibuja el gráfico
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Empaqueta el canvas

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the model: {e}")  # Manejo de errores

    def save_model(self):
        """Saves the linear regression model data to a file."""
        if self.model is None:
            messagebox.showwarning("Warning", "No model has been created to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pkl",
                                                  filetypes=[("Pickle files", "*.pkl"), 
                                                             ("Joblib files", "*.joblib")])
        if not file_path:
            return  # Sale si no se seleccionó un archivo

        try:
            # Prepara los datos para guardar
            model_data = {
                'input_column': self.selected_input,
                'output_column': self.selected_output,
                'model_description': self.model_description,
                'formula': f"{self.selected_output} = {self.model.coef_[0]:.2f} * {self.selected_input} + {self.model.intercept_:.2f}",
                'metrics': {
                    'R²': round(r2_score(self.data_frame[self.selected_output], self.model.predict(self.data_frame[[self.selected_input]])), 2),
                    'MSE': round(mean_squared_error(self.data_frame[self.selected_output], self.model.predict(self.data_frame[[self.selected_input]])), 2)
                }
            }

            # Sauvegarde les données du modèle
            joblib.dump(model_data, file_path)
            messagebox.showinfo("Success", f"Model data saved successfully at {file_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the model: {e}")  # Manejo de errores

if __name__ == "__main__":
    root = tk.Tk()  # Inicializa la ventana principal
    app = DataLoaderApp(root)  # Crea la aplicación
    root.mainloop()  # Inicia el bucle principal de la aplicación
