import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import modulo_importacion  # Importamos el módulo externo

class DataLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cargador de Datos")
        
        # Configuración del fondo blanco
        self.root.configure(bg="white")
        self.font_style = ("Helvetica", 12)

        # Etiqueta para mostrar la ruta del archivo
        self.file_path_label = tk.Label(root, text="Ningún archivo seleccionado", font=self.font_style, bg="white", fg="black")
        self.file_path_label.pack(pady=10)

        # Crear un frame para centrar el botón
        button_frame = tk.Frame(root, bg="white")
        button_frame.pack(pady=10)

        # Botón para cargar archivo
        self.load_button = tk.Button(button_frame, text="Cargar Archivo", command=self.load_file, font=self.font_style, bg="#007BFF", fg="white", bd=0, padx=20, pady=10)
        self.load_button.pack()

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=300, style="TProgressbar")

        # Estilo de la barra de progreso
        style = ttk.Style()
        style.configure("TProgressbar", thickness=5, troughcolor="white", background="#007BFF", troughrelief="flat")
        style.configure("Treeview.Heading", font=("Helvetica", 12), background="#f0f0f0", foreground="black", borderwidth=1)
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#007BFF")], foreground=[("selected", "white")])

        self.data_frame = None
        self.table_frame = None

        # Botón para manejar NaN
        self.nan_button = tk.Button(button_frame, text="Manejar Valores Faltantes", command=self.handle_nan, font=self.font_style, bg="#28a745", fg="white", bd=0, padx=20, pady=10)
        self.nan_button.pack(pady=10)

        # Secciones para los selectores de entrada y salida
        self.selector_frame = tk.Frame(self.root, bg="white")
        self.selector_frame.pack(pady=10, fill=tk.X)
        self.input_columns = []
        self.output_column = None

    def load_file(self):
        file_types = [("Archivos CSV", ".csv"), ("Archivos Excel", ".xlsx .xls"), ("Archivos SQLite", ".sqlite *.db")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            self.file_path_label.config(text=file_path)
            self.progress_bar.pack(fill=tk.X, padx=10, pady=10)
            self.progress_bar.start()

            threading.Thread(target=self.process_import, args=(file_path,)).start()

    def process_import(self, file_path):
        try:
            self.data_frame = modulo_importacion.importar_archivo(file_path)
            self.root.after(0, self.display_data)
            self.root.after(0, self.show_success_message)
        except ValueError as e:
            error_message = str(e)
            self.root.after(0, lambda: self.show_error_message(error_message))
        except Exception as e:
            error_message = f"Error inesperado: {str(e)}"
            self.root.after(0, lambda: self.show_error_message(error_message))
        finally:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

    def display_data(self):
        if self.table_frame:
            self.table_frame.destroy()
        
        self.table_frame = tk.Frame(self.root, bg="white")
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(self.table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')

        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        self.table = ttk.Treeview(self.table_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set, style="Treeview")
        self.table.pack(fill=tk.BOTH, expand=True)

        vsb.config(command=self.table.yview)
        hsb.config(command=self.table.xview)

        self.table["columns"] = list(self.data_frame.columns)
        self.table["show"] = "headings"

        for col in self.data_frame.columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=100)

        for _, row in self.data_frame.iterrows():
            self.table.insert("", "end", values=list(row))

        # Mostrar selectores después de cargar datos
        self.display_column_selectors()

    def display_column_selectors(self):
        # Limpiar frame de selectores si ya existe
        for widget in self.selector_frame.winfo_children():
            widget.destroy()

        # Selector de tipo de regresion
        self.regression_type_var = tk.StringVar(value="simple")
        tk.Label(self.selector_frame, text="Tipo de regresion:", font=self.font_style, bg="white").pack(anchor="w")
        tk.Radiobutton(self.selector_frame, text="Simple", variable=self.regression_type_var, value="simple", command=self.update_input_selector, bg="white").pack(anchor="w")
        tk.Radiobutton(self.selector_frame, text="Multiple", variable=self.regression_type_var, value="multiple", command=self.update_input_selector, bg="white").pack(anchor="w")

        # Selector de columnas de entrada
        self.input_label = tk.Label(self.selector_frame, text="Selecciona columna(s) de entrada:", font=self.font_style, bg="white")
        self.input_label.pack(anchor="w")

        self.input_selector = tk.Listbox(self.selector_frame, selectmode=tk.SINGLE if self.regression_type_var.get() == "simple" else tk.MULTIPLE, exportselection=0, height=5)
        for col in self.data_frame.columns:
            self.input_selector.insert(tk.END, col)
        self.input_selector.pack(fill=tk.X, pady=5)

        # Selector de columna de salida
        tk.Label(self.selector_frame, text="Selecciona columna de salida:", font=self.font_style, bg="white").pack(anchor="w")
        self.output_selector = ttk.Combobox(self.selector_frame, values=list(self.data_frame.columns), state="readonly")
        self.output_selector.pack(fill=tk.X, pady=5)

        # Botón para confirmar selección
        confirm_button = tk.Button(self.selector_frame, text="Confirmar selección", command=self.confirm_selection, font=self.font_style, bg="#007BFF", fg="white")
        confirm_button.pack(pady=10)

    def update_input_selector(self):
        # Actualizar el selector de entrada en función del tipo de regresión
        mode = tk.SINGLE if self.regression_type_var.get() == "simple" else tk.MULTIPLE
        self.input_selector.config(selectmode=mode)

    def confirm_selection(self):
        # Obtener columnas seleccionadas de entrada y salida
        self.input_columns = [self.input_selector.get(i) for i in self.input_selector.curselection()]
        self.output_column = self.output_selector.get()

        # Validar que se seleccionó al menos una columna de entrada y una de salida
        if not self.input_columns:
            messagebox.showerror("Error", "Por favor selecciona al menos una columna de entrada.")
            return
        if not self.output_column:
            messagebox.showerror("Error", "Por favor selecciona una columna de salida.")
            return

        # Confirmación exitosa
        messagebox.showinfo("Exito", "Selección de columnas confirmada.")

    def handle_nan(self):
        nan_counts = self.data_frame.isna().sum()
        nan_columns = nan_counts[nan_counts > 0]

        if nan_columns.empty:
            messagebox.showinfo("Sin Valores Faltantes", "No se encontraron valores faltantes en los datos.")
            return

        nan_info = "\n".join([f"{col}: {count} valores faltantes" for col, count in nan_columns.items()])
        messagebox.showinfo("Valores Faltantes Detectados", f"Las siguientes columnas tienen valores faltantes:\n\n{nan_info}")

        option = simpledialog.askstring("Manejar Valores Faltantes", 
                                        "Elige una opcion para manejar los valores faltantes:\n"
                                        "1. Eliminar filas con valores faltantes\n"
                                        "2. Rellenar con la media (solo columnas numericas)\n"
                                        "3. Rellenar con la mediana (solo columnas numericas)\n"
                                        "4. Rellenar con un valor constante")

        if option == "1":
            self.data_frame.dropna(inplace=True)
            messagebox.showinfo("Exito", "Filas con valores faltantes eliminadas.")
        elif option == "2":
            numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns
            self.data_frame[numeric_columns] = self.data_frame[numeric_columns].fillna(self.data_frame[numeric_columns].mean())
            messagebox.showinfo("Exito", "Valores faltantes rellenados con la media.")
        elif option == "3":
            numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns
            self.data_frame[numeric_columns] = self.data_frame[numeric_columns].fillna(self.data_frame[numeric_columns].median())
            messagebox.showinfo("Exito", "Valores faltantes rellenados con la mediana.")
        elif option == "4":
            constant_value = simpledialog.askfloat("Rellenar con Constante", "Ingresa un valor constante para rellenar los valores faltantes:")
            if constant_value is not None:
                self.data_frame.fillna(constant_value, inplace=True)
                messagebox.showinfo("Exito", f"Valores faltantes rellenados con el valor constante: {constant_value}")
        else:
            messagebox.showwarning("Opcion Invalida", "Por favor elige una opcion valida.")

        self.display_data()

    def show_success_message(self):
        messagebox.showinfo("Exito", "Archivo cargado exitosamente.")

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()  # Crear la ventana principal
    app = DataLoaderApp(root)  # Crear la instancia de la app
    root.mainloop()  # Iniciar el bucle principal de la interfaz
