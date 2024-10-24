import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import modulo_importacion  # Importamos el módulo externo

class DataLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Loader")
        
        # Configuración del fondo blanco
        self.root.configure(bg="white")

        # Fuente más gruesa y minimalista
        self.font_style = ("Helvetica", 12)  # Cambiamos a una fuente más gruesa
        
        # Etiqueta para mostrar la ruta del archivo
        self.file_path_label = tk.Label(root, text="No file selected", font=self.font_style, 
                                        bg="white", fg="black")
        self.file_path_label.pack(pady=10)

        # Crear un frame para centrar el botón
        button_frame = tk.Frame(root, bg="white")
        button_frame.pack(pady=10)

        # Crear un botón moderno y minimalista con esquinas redondeadas
        self.load_button = tk.Button(button_frame, text="Load File", command=self.load_file, 
                                     font=self.font_style, bg="#007BFF", fg="white", 
                                     activebackground="#0056b3", bd=0, padx=20, pady=10)
        self.load_button.pack()  # Colocar el botón en el frame

        # Aplicar un estilo redondeado al botón
        self.load_button.config(relief="flat", overrelief="flat", highlightthickness=0, borderwidth=0)
        self.load_button.config(highlightbackground="white", highlightcolor="white")

        # Añadimos el estilo de la barra de progreso con colores minimalistas
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", 
                                            length=300, style="TProgressbar")

        # Ajustes de la barra de progreso
        style = ttk.Style()
        style.configure("TProgressbar", thickness=5, troughcolor="white", 
                        background="#007BFF", troughrelief="flat")

        # Modernizamos la tabla con estilos de Treeview
        style.configure("Treeview.Heading", font=("Helvetica", 12), background="#f0f0f0", 
                        foreground="black", borderwidth=1)
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#007BFF")], foreground=[("selected", "white")])

        self.data_frame = None
        self.table_frame = None  # Frame para la tabla

    def load_file(self):
        file_types = [("CSV files", ".csv"), ("Excel files", ".xlsx .xls"), ("SQLite files", ".sqlite *.db")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            self.file_path_label.config(text=file_path)
            self.progress_bar.pack(fill=tk.X, padx=10, pady=10)  # Mostrar la barra de progreso
            self.progress_bar.start()  # Iniciar la barra de progreso

            # Usar un hilo para evitar congelar la interfaz
            threading.Thread(target=self.load_data, args=(file_path,)).start()

    def load_data(self, file_path):
        try:
            # Llamamos a la función de importación desde el módulo
            self.data_frame = modulo_importacion.importar_archivo(file_path)

            # Verificar si se cargó correctamente y mostrar los datos
            self.root.after(0, self.display_data)
            self.root.after(0, self.show_success_message)
        except ValueError as e:
            error_message = str(e)  # Capturar el mensaje de error para evitar problemas con lambda
            self.root.after(0, lambda: self.show_error_message(error_message))
        except Exception as e:
            # Captura cualquier otro tipo de error inesperado
            error_message = f"Error inesperado: {str(e)}"
            self.root.after(0, lambda: self.show_error_message(error_message))
        finally:
            self.progress_bar.stop()  # Detener la barra de progreso
            self.progress_bar.pack_forget()  # Ocultar la barra de progreso

    def display_data(self):
        # Destruir el frame de la tabla existente si hay uno
        if self.table_frame:
            self.table_frame.destroy()
        
        # Crear un nuevo frame para la tabla
        self.table_frame = tk.Frame(self.root, bg="white")
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')

        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')
        
        # Crear la tabla
        self.table = ttk.Treeview(self.table_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set, 
                                  style="Treeview")
        self.table.pack(fill=tk.BOTH, expand=True)

        vsb.config(command=self.table.yview)
        hsb.config(command=self.table.xview)
        
        # Configurar las columnas del Treeview
        self.table["columns"] = list(self.data_frame.columns)
        self.table["show"] = "headings"

        for col in self.data_frame.columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=100)

        # Insertar datos
        for _, row in self.data_frame.iterrows():
            self.table.insert("", "end", values=list(row))

        print("Data displayed successfully")

    def show_success_message(self):
        messagebox.showinfo("Success", "Archivo cargado exitosamente.")

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()  # Crear la ventana principal
    app = DataLoaderApp(root)  # Crear la instancia de la app
    root.mainloop()  # Iniciar el bucle principal de la interfaz
