import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import modulo_importacion  # Importamos el módulo externo

class DataLoaderApp:
    def __init__(self, root):
        root.state('zoomed')  # Maximizar la ventana
        self.root = root
        self.root.title("Cargador de Datos")  # Título de la ventana
        self.root.configure(bg="white")
        self.font_style = ("Helvetica", 10)

        # Color y color de hover para los botones
        self.toolbar_color = "#e0e0e0"
        self.hover_color = "#c0c0c0"

        # Crear una barra superior para los botones
        self.toolbar = tk.Frame(root, bg=self.toolbar_color, height=40)
        self.toolbar.pack(side="top", fill="x")

        # Botón desplegable para cargar dataset y salir
        self.file_menu_button = tk.Menubutton(self.toolbar, text="Archivo", font=self.font_style, bg=self.toolbar_color, fg="black", bd=0, padx=20, pady=5)
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0)

        # Opciones del menú desplegable
        self.file_menu.add_command(label="Cargar Dataset", command=self.load_file)
        self.file_menu.add_separator()  # Separador entre opciones
        self.file_menu.add_command(label="Salir", command=self.root.quit)  # Cerrar la aplicación

        self.file_menu_button.config(menu=self.file_menu)
        self.file_menu_button.pack(side="left", padx=10)
        self.add_hover_effect(self.file_menu_button)

        # Botón desplegable para manejar valores (cambiado a "Datos")
        self.data_menu_button = tk.Menubutton(self.toolbar, text="Datos", font=self.font_style, bg=self.toolbar_color, fg="black", bd=0, padx=20, pady=5)
        self.data_menu = tk.Menu(self.data_menu_button, tearoff=0)

        # Opciones del menú desplegable
        self.data_menu.add_command(label="Eliminar filas con NaN", command=lambda: self.handle_nan(option="1"))
        self.data_menu.add_command(label="Rellenar con Media", command=lambda: self.handle_nan(option="2"))
        self.data_menu.add_command(label="Rellenar con Mediana", command=lambda: self.handle_nan(option="3"))
        self.data_menu.add_command(label="Rellenar con Constante", command=lambda: self.handle_nan(option="4"))

        self.data_menu_button.config(menu=self.data_menu)
        self.data_menu_button.pack(side="left", padx=2)  # Acercado aún más con padding de 2
        self.add_hover_effect(self.data_menu_button)

        # Botón desplegable para regresión
        self.regression_menu_button = tk.Menubutton(self.toolbar, text="Regresión", font=self.font_style, bg=self.toolbar_color, fg="black", bd=0, padx=20, pady=5)
        self.regression_menu = tk.Menu(self.regression_menu_button, tearoff=0)

        # Opciones del menú desplegable de regresión
        self.regression_menu.add_command(label="Seleccionar Columnas para Regresión", command=self.show_regression_selector)

        self.regression_menu_button.config(menu=self.regression_menu)
        self.regression_menu_button.pack(side="left", padx=2)
        self.add_hover_effect(self.regression_menu_button)

        # Etiqueta para la ruta del archivo
        self.file_path_label = tk.Label(root, text="Ningún archivo seleccionado", font=self.font_style, bg="white", fg="black")
        self.file_path_label.pack(pady=10)

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=300, style="TProgressbar")

        # Estilo de la barra de progreso y Treeview
        style = ttk.Style()
        style.configure("TProgressbar", thickness=5, troughcolor="white", background="#007BFF", troughrelief="flat")
        style.configure("Treeview.Heading", font=("Helvetica", 12), background="#f0f0f0", foreground="black", borderwidth=1)
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#007BFF")], foreground=[("selected", "white")])

        self.data_frame = None
        self.table_frame = None

        # Agregar evento para salir de la ventana maximizada con la tecla Esc
        self.root.bind("<Escape>", lambda e: self.root.state('normal'))

    def add_hover_effect(self, widget):
        # Cambiar el color de fondo del botón cuando el ratón esté encima
        widget.bind("<Enter>", lambda e: widget.config(bg=self.hover_color))
        widget.bind("<Leave>", lambda e: widget.config(bg=self.toolbar_color))

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

    def show_regression_selector(self):
        if self.data_frame is None:
            messagebox.showwarning("Advertencia", "No se ha cargado ningún dataset.")
            return

        # Crear un nuevo cuadro de diálogo para seleccionar columnas
        regression_window = tk.Toplevel(self.root)
        regression_window.title("Seleccionar Columnas para Regresión")
        regression_window.geometry("400x300")  # Ajustar el tamaño de la ventana

        input_label = tk.Label(regression_window, text="Selecciona columna(s) de entrada:", font=self.font_style)
        input_label.pack(anchor="w", padx=10, pady=5)

        input_selector = tk.Listbox(regression_window, selectmode=tk.MULTIPLE, exportselection=0, height=5)
        for col in self.data_frame.columns:
            input_selector.insert(tk.END, col)
        input_selector.pack(fill=tk.X, padx=10, pady=5)

        output_label = tk.Label(regression_window, text="Selecciona columna de salida:", font=self.font_style)
        output_label.pack(anchor="w", padx=10, pady=5)

        output_selector = ttk.Combobox(regression_window, values=list(self.data_frame.columns), state="readonly")
        output_selector.pack(fill=tk.X, padx=10, pady=5)

        select_button = tk.Button(regression_window, text="Seleccionar", command=lambda: self.confirm_selection(input_selector, output_selector, regression_window))
        select_button.pack(pady=10)

    def confirm_selection(self, input_selector, output_selector, regression_window):
        selected_inputs = [input_selector.get(i) for i in input_selector.curselection()]
        selected_output = output_selector.get()

        if not selected_inputs or not selected_output:
            messagebox.showwarning("Advertencia", "Por favor selecciona columnas de entrada y salida.")
            return

        # Aquí puedes agregar la lógica para ejecutar la regresión con las columnas seleccionadas
        messagebox.showinfo("Éxito", f"Columnas seleccionadas:\nEntradas: {', '.join(selected_inputs)}\nSalida: {selected_output}")
        regression_window.destroy()

    def handle_nan(self, option):
        if self.data_frame is None:
            messagebox.showwarning("Advertencia", "No se ha cargado ningún dataset.")
            return

        if option == "1":
            self.data_frame.dropna(inplace=True)
            messagebox.showinfo("Éxito", "Filas con valores NaN eliminadas.")
        elif option == "2":
            numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns
            self.data_frame[numeric_columns] = self.data_frame[numeric_columns].fillna(self.data_frame[numeric_columns].mean())
            messagebox.showinfo("Éxito", "Valores faltantes rellenados con la media.")
        elif option == "3":
            numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns
            self.data_frame[numeric_columns] = self.data_frame[numeric_columns].fillna(self.data_frame[numeric_columns].median())
            messagebox.showinfo("Éxito", "Valores faltantes rellenados con la mediana.")
        elif option == "4":
            constant_value = simpledialog.askfloat("Rellenar con Constante", "Ingresa un valor constante para rellenar los valores faltantes:")
            if constant_value is not None:
                self.data_frame.fillna(constant_value, inplace=True)
                messagebox.showinfo("Éxito", f"Valores faltantes rellenados con el valor constante: {constant_value}")
        else:
            messagebox.showwarning("Opción Inválida", "Por favor elige una opción válida.")

        self.display_data()

    def show_success_message(self):
        messagebox.showinfo("Éxito", "Archivo cargado exitosamente.")

    def show_error_message(self, message):
        messagebox.showerror("Error", f"No se pudo cargar el archivo: {message}")

root = tk.Tk()
app = DataLoaderApp(root)
root.mainloop()
