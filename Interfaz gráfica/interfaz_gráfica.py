import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import sqlite3
import threading

class DataLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Loader")

        self.file_path_label = tk.Label(root, text="No file selected", font=("Helvetica", 12))
        self.file_path_label.pack(pady=10)
        
        self.load_button = tk.Button(root, text="Load Dataset", command=self.load_file, font=("Helvetica", 12))
        self.load_button.pack(pady=10)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
        
        self.data_frame = None
        self.table_frame = None  # Frame for the table
        self.selector_frame = None  # Frame for the selectors

    def load_file(self):
        file_types = [("CSV files", ".csv"), ("Excel files", ".xlsx .xls"), ("SQLite files", ".sqlite *.db")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            self.file_path_label.config(text=file_path)
            self.progress_bar.pack(fill=tk.X, padx=10, pady=10)
            self.progress_bar.start()
            threading.Thread(target=self.load_data, args=(file_path,)).start()

    def load_data(self, file_path):
        try:
            extension = file_path.split('.')[-1].lower()

            if extension == 'csv':
                self.data_frame = pd.read_csv(file_path)
            elif extension in ['xlsx', 'xls']:
                self.data_frame = pd.read_excel(file_path, engine='openpyxl')
            elif extension in ['sqlite', 'db']:
                conn = sqlite3.connect(file_path)
                tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
                table_name = tables['name'].iloc[0]
                self.data_frame = pd.read_sql_query(f"SELECT * FROM \"{table_name}\"", conn)
                conn.close()
            else:
                raise ValueError("Unsupported file type.")

            if self.data_frame.empty:
                raise ValueError("The selected file is empty or contains no data.")
            
            self.root.after(0, self.display_data)
            self.root.after(0, self.show_selectors)  # Display selectors after loading data
            self.root.after(0, self.show_success_message)
        except Exception as e:
            self.root.after(0, lambda: self.show_error_message(str(e)))
        finally:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

    def display_data(self):
        if self.table_frame:
            self.table_frame.destroy()
        
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(self.table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        self.table = ttk.Treeview(self.table_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.table.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.table.yview)
        hsb.config(command=self.table.xview)

        self.table["columns"] = list(self.data_frame.columns)
        self.table["show"] = "headings"
        
        for col in self.data_frame.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        
        for _, row in self.data_frame.iterrows():
            self.table.insert("", "end", values=list(row))
        
    def show_selectors(self):
        if self.selector_frame:
            self.selector_frame.destroy()
        
        self.selector_frame = tk.Frame(self.root)
        self.selector_frame.pack(pady=10)
        
        tk.Label(self.selector_frame, text="Select Input Columns:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5)
        
        # Casillas de verificación para columnas de entrada
        self.input_vars = []
        for col in self.data_frame.columns:
            var = tk.BooleanVar()
            self.input_vars.append(var)
            chk = tk.Checkbutton(self.selector_frame, text=col, variable=var)
            chk.grid(sticky="w")
        
        tk.Label(self.selector_frame, text="Select Target Column:", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=5)

        # Selector único para columna de salida
        self.target_var = tk.StringVar()
        self.target_combobox = ttk.Combobox(self.selector_frame, textvariable=self.target_var)
        self.target_combobox['values'] = list(self.data_frame.columns)
        self.target_combobox.grid(row=1, column=1, padx=10, pady=5)

        # Botón para confirmar la selección de columnas
        self.confirm_button = tk.Button(self.selector_frame, text="Confirm Selection", command=self.confirm_selection)
        self.confirm_button.grid(row=2, column=0, columnspan=2, pady=10)

    def confirm_selection(self):
        # Obtener las columnas de entrada seleccionadas
        input_columns = [col for var, col in zip(self.input_vars, self.data_frame.columns) if var.get()]
        target_column = self.target_var.get()

        # Validar las selecciones
        if not input_columns and not target_column:
            messagebox.showerror("Error", "Please select at least one input column and one target column.")
        elif not input_columns:
            messagebox.showerror("Error", "Please select at least one input column.")
        elif not target_column:
            messagebox.showerror("Error", "Please select a target column.")
        else:
            messagebox.showinfo("Selection Confirmed", f"Input Columns: {input_columns}\nTarget Column: {target_column}")
            print("Selected input columns:", input_columns)
            print("Selected target column:", target_column)

    def show_success_message(self):
        messagebox.showinfo("Success", "File loaded successfully.")

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataLoaderApp(root)
    root.mainloop()
