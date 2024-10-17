import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
import sqlite3

class DataLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Loader")
        
        self.file_path_label = tk.Label(root, text="No file selected")
        self.file_path_label.pack()
        
        self.load_button = tk.Button(root, text="Load Dataset", command=self.load_file)
        self.load_button.pack()
        
        self.data_frame = None
        self.table = None

    def is_valid_sqlite(self, file_path):
        # Revisa el encabezado del archivo para ver si es una base de datos SQLite
        try:
            with open(file_path, 'rb') as file:
                header = file.read(16)
                return header == b'SQLite format 3\000'
        except Exception as e:
            print(f"Error checking file header: {e}")
            return False

    def load_file(self):
        file_types = [("CSV files", ".csv"), ("Excel files", ".xlsx .xls"), ("SQLite files", ".sqlite *.db")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            self.file_path_label.config(text=file_path)
            try:
                if file_path.endswith('.csv'):
                    self.data_frame = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.data_frame = pd.read_excel(file_path)
                elif file_path.endswith('.xls'):
                    self.data_frame = pd.read_excel(file_path, engine='xlrd')
                elif file_path.endswith(('.sqlite', '.db')):
                    # Verificar si el archivo es una base de datos SQLite válida
                    if not self.is_valid_sqlite(file_path):
                        raise ValueError("El archivo seleccionado no es una base de datos SQLite válida.")
                    
                    # Intentar conectar a la base de datos SQLite
                    conn = sqlite3.connect(file_path)
                    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
                    table_name = tables['name'].iloc[0]  # Seleccionar el primer nombre de tabla
                    print(f"Selected table: {table_name}")
                    self.data_frame = pd.read_sql_query(f"SELECT * FROM \"{table_name}\"", conn)
                    conn.close()
                
                # Verificar que el DataFrame no esté vacío
                if not self.data_frame.empty:
                    print("File loaded successfully")
                    self.display_data()
                else:
                    raise ValueError("El archivo seleccionado está vacío o no contiene datos.")
        
            except Exception as e:
                print(f"Error loading file: {e}")
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def display_data(self):
        if self.table:
            self.table.destroy()  # Destruir el Treeview existente si ya hay uno
        
        self.table = ttk.Treeview(self.root)
        self.table.pack(fill=tk.BOTH, expand=True)
        
        self.table["columns"] = list(self.data_frame.columns)
        self.table["show"] = "headings"
        
        for col in self.data_frame.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        
        for _, row in self.data_frame.iterrows():
            self.table.insert("", "end", values=list(row))
        
        print("Data displayed successfully")

if __name__ == "__main__":
    root = tk.Tk()  # Crear ventana principal de Tkinter
    app = DataLoaderApp(root)  # Crear instancia de la aplicación
    root.mainloop()  # Iniciar el bucle principal de la interfaz