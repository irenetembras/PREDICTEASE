import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import modulo_importacion  # Importamos el módulo externo

class DataLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Loader")
        
        # Configuración del fondo blanco
        self.root.configure(bg="white")

        # Fuente más gruesa y minimalista
        self.font_style = ("Helvetica", 12)
        
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
        self.load_button.pack()

        # Aplicar un estilo redondeado al botón
        self.load_button.config(relief="flat", overrelief="flat", highlightthickness=0, borderwidth=0)

        # Añadir la barra de progreso
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=300, style="TProgressbar")

        # Estilo de la barra de progreso
        style = ttk.Style()
        style.configure("TProgressbar", thickness=5, troughcolor="white", background="#007BFF", troughrelief="flat")

        # Modernizar la tabla con estilo Treeview
        style.configure("Treeview.Heading", font=("Helvetica", 12), background="#f0f0f0", foreground="black", borderwidth=1)
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#007BFF")], foreground=[("selected", "white")])

        self.data_frame = None
        self.table_frame = None

        # Botón para manejar NaN
        self.nan_button = tk.Button(button_frame, text="Handle Missing Values", command=self.handle_nan, 
                                    font=self.font_style, bg="#28a745", fg="white", 
                                    activebackground="#218838", bd=0, padx=20, pady=10)
        self.nan_button.pack(pady=10)

    def load_file(self):
        file_types = [("CSV files", ".csv"), ("Excel files", ".xlsx .xls"), ("SQLite files", ".sqlite *.db")]
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
            error_message = f"Unexpected error: {str(e)}"
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

    def handle_nan(self):
        nan_counts = self.data_frame.isna().sum()
        nan_columns = nan_counts[nan_counts > 0]

        if nan_columns.empty:
            messagebox.showinfo("No Missing Values", "No missing values found in the data.")
            return

        nan_info = "\n".join([f"{col}: {count} missing values" for col, count in nan_columns.items()])
        messagebox.showinfo("Missing Values Detected", f"The following columns have missing values:\n\n{nan_info}")

        option = simpledialog.askstring("Handle Missing Values", 
                                        "Choose an option to handle missing values:\n"
                                        "1. Remove rows with missing values\n"
                                        "2. Fill with mean (for numeric columns only)\n"
                                        "3. Fill with median (for numeric columns only)\n"
                                        "4. Fill with constant")

        if option == "1":
            self.data_frame.dropna(inplace=True)
            messagebox.showinfo("Success", "Rows with missing values removed.")
        elif option == "2":
            numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns
            self.data_frame[numeric_columns] = self.data_frame[numeric_columns].fillna(self.data_frame[numeric_columns].mean())
            messagebox.showinfo("Success", "Missing values filled with mean.")
        elif option == "3":
            numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns
            self.data_frame[numeric_columns] = self.data_frame[numeric_columns].fillna(self.data_frame[numeric_columns].median())
            messagebox.showinfo("Success", "Missing values filled with median.")
        elif option == "4":
            constant_value = simpledialog.askfloat("Fill with Constant", "Enter a constant value to fill missing values:")
            if constant_value is not None:
                self.data_frame.fillna(constant_value, inplace=True)
                messagebox.showinfo("Success", f"Missing values filled with constant: {constant_value}")
        else:
            messagebox.showwarning("Invalid Option", "Please choose a valid option.")

        self.display_data()

    def show_success_message(self):
        messagebox.showinfo("Success", "File loaded successfully.")

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()  # Crear la ventana principal
    app = DataLoaderApp(root)  # Crear la instancia de la app
    root.mainloop()  # Iniciar el bucle principal de la interfaz
