import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import modulo_importacion  # Importamos el módulo externo

class DataLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Loader")
        
        self.file_path_label = tk.Label(root, text="No file selected", font=("Helvetica", 12))
        self.file_path_label.pack(pady=10)
        
        self.load_button = tk.Button(root, text="Load Dataset", command=self.load_file, font=("Helvetica", 12))
        self.load_button.pack(pady=10)

        # Crear la barra de progreso, inicialmente oculta
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
        
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
        except Exception as e:
            self.root.after(0, lambda: self.show_error_message(str(e)))  # Manejo de errores
        finally:
            self.progress_bar.stop()  # Detener la barra de progreso
            self.progress_bar.pack_forget()  # Ocultar la barra de progreso

    def display_data(self):
        # Destruir el frame de la tabla existente si hay uno
        if self.table_frame:
            self.table_frame.destroy()
        
        # Crear un nuevo frame para la tabla y scrollbars
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        # Crear las scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')

        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        # Crear el Treeview
        self.table = ttk.Treeview(self.table_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.table.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.table.yview)
        hsb.config(command=self.table.xview)

        # Configurar las columnas del Treeview
        self.table["columns"] = list(self.data_frame.columns)
        self.table["show"] = "headings"
        
        for col in self.data_frame.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)  # Ajustar el ancho de las columnas
        
        for _, row in self.data_frame.iterrows():
            self.table.insert("", "end", values=list(row))
        
        print("Data displayed successfully")

    def show_success_message(self):
        messagebox.showinfo("Success", "File loaded successfully.")

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()  # Crear la ventana principal
    app = DataLoaderApp(root)  # Crear la instancia de la app
    root.mainloop()  # Iniciar el bucle principal de la interfaz
