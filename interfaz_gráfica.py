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

        # Create the progress bar but keep it hidden initially
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
        
        self.data_frame = None
        self.table_frame = None  # Frame for the table

    def load_file(self):
        file_types = [("CSV files", ".csv"), ("Excel files", ".xlsx .xls"), ("SQLite files", ".sqlite *.db")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            self.file_path_label.config(text=file_path)
            self.progress_bar.pack(fill=tk.X, padx=10, pady=10)  # Show the progress bar
            self.progress_bar.start()  # Start the progress bar

            # Use a thread to avoid freezing the interface
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

            # Additional validations for DataFrame
            if self.data_frame.empty:
                raise ValueError("The selected file is empty or contains no data.")
            
            # Validate that the columns contain the expected data types
            if not all(isinstance(val, (int, float, str)) for col in self.data_frame.columns for val in self.data_frame[col]):
                raise ValueError("The file contains invalid or malformed data.")

            self.root.after(0, self.display_data)  # Call display_data in the main thread
            self.root.after(0, self.show_success_message)  # Show success message
        except Exception as e:
            self.root.after(0, lambda: self.show_error_message(str(e)))  # Error handling in the main thread
        finally:
            self.progress_bar.stop()  # Stop the progress bar
            self.progress_bar.pack_forget()  # Hide the progress bar

    def display_data(self):
        # Destroy the existing frame and its elements if there is one
        if self.table_frame:
            self.table_frame.destroy()
        
        # Create a new frame for the table and scrollbars
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')

        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        # Create the Treeview
        self.table = ttk.Treeview(self.table_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.table.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.table.yview)
        hsb.config(command=self.table.xview)

        self.table["columns"] = list(self.data_frame.columns)
        self.table["show"] = "headings"
        
        for col in self.data_frame.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)  # You can adjust the width of the columns here
        
        for _, row in self.data_frame.iterrows():
            self.table.insert("", "end", values=list(row))
        
        print("Data displayed successfully")

    def show_success_message(self):
        messagebox.showinfo("Success", "File loaded successfully.")

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()  # Create the main Tkinter window
    app = DataLoaderApp(root)  # Create an instance of the application
    root.mainloop()  # Start the main loop of the interface
