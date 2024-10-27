import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
import threading
import matplotlib.pyplot as plt

class DataLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Loader and Model Creator")
        
        # Label and button for file loading
        self.file_path_label = tk.Label(root, text="No file selected", font=("Helvetica", 12))
        self.file_path_label.pack(pady=10)
        
        self.load_button = tk.Button(root, text="Load Dataset", command=self.load_file, font=("Helvetica", 12))
        self.load_button.pack(pady=10)

        # Progress bar (initially hidden)
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
        
        # Selectors for features and target columns
        self.features_label = tk.Label(root, text="Select Input Column (Feature):", font=("Helvetica", 12))
        self.features_label.pack(pady=5)
        self.features_listbox = tk.Listbox(root, selectmode="multiple", exportselection=0)
        self.features_listbox.pack(pady=5)

        self.target_label = tk.Label(root, text="Select Output Column (Target):", font=("Helvetica", 12))
        self.target_label.pack(pady=5)
        self.target_combobox = ttk.Combobox(root, state="readonly")
        self.target_combobox.pack(pady=5)
        
        # Button to confirm selections and start training the model
        self.create_model_button = tk.Button(root, text="Create Regression Model", command=self.create_model, font=("Helvetica", 12))
        self.create_model_button.pack(pady=10)

        # Label for showing model results and formula
        self.results_label = tk.Label(root, text="", font=("Helvetica", 12))
        self.results_label.pack(pady=10)
        self.model_formula_label = tk.Label(root, text="", font=("Helvetica", 12), wraplength=400, justify="left")
        self.model_formula_label.pack(pady=5)

        self.data_frame = None
        self.current_db_connection = None

    def load_file(self):
        # Load CSV, Excel, DB, or SQLite file
        file_types = [
            ("CSV files", ".csv"),
            ("Excel files", ".xlsx .xls"),
            ("Database files", ".db .sqlite")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            self.file_path_label.config(text=file_path)
            self.progress_bar.pack(fill=tk.X, padx=10, pady=10)
            self.progress_bar.start()

            threading.Thread(target=self.load_data, args=(file_path,)).start()

    def load_data(self, file_path):
        try:
            if file_path.endswith('.csv'):
                self.data_frame = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.data_frame = pd.read_excel(file_path)
            elif file_path.endswith(('.db', '.sqlite')):
                self.current_db_connection = self.connect_to_database(file_path)
                if not self.current_db_connection:
                    raise ValueError("Unable to connect to the database. Please check the file.")
                
                tables = self.get_table_names(self.current_db_connection)
                if not tables:
                    raise ValueError("No tables found in the database.")

                table_name = self.select_table(tables)
                if table_name:
                    self.data_frame = pd.read_sql_query(f"SELECT * FROM {table_name}", self.current_db_connection)
                else:
                    raise ValueError("No table selected.")

                self.current_db_connection.close()
            else:
                raise ValueError("Unsupported file type.")
                
            if self.data_frame.empty:
                raise ValueError("The file is empty.")
            
            self.update_column_selectors()
            self.show_message("Success", "File loaded successfully.")
        except Exception as e:
            self.show_message("Error", str(e))
        finally:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

    def connect_to_database(self, file_path):
        try:
            # Intenta conectar a la base de datos
            connection = sqlite3.connect(file_path)
            return connection
        except sqlite3.Error as e:
            # Maneja errores de conexión
            self.show_message("Database Error", f"Could not connect to database: {str(e)}")
            return None

    def get_table_names(self, connection):
        # Obtener nombres de tablas de la base de datos
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables]

    def select_table(self, tables):
        # Crear un cuadro de diálogo para seleccionar la tabla
        top = tk.Toplevel(self.root)
        top.title("Select Table")

        label = tk.Label(top, text="Select a table to load:", font=("Helvetica", 12))
        label.pack(pady=10)

        table_var = tk.StringVar(value=tables[0] if tables else "")
        table_combobox = ttk.Combobox(top, textvariable=table_var, values=tables, state="readonly")
        table_combobox.pack(pady=10)

        def confirm_selection():
            selected_table = table_var.get()
            top.destroy()
            return selected_table

        confirm_button = tk.Button(top, text="Confirm", command=confirm_selection)
        confirm_button.pack(pady=10)

        top.wait_window()
        return table_var.get()

    def update_column_selectors(self):
        # Update the feature (input) and target (output) selectors with the data columns
        self.features_listbox.delete(0, tk.END)
        for col in self.data_frame.columns:
            self.features_listbox.insert(tk.END, col)
        
        self.target_combobox["values"] = list(self.data_frame.columns)

    def create_model(self):
        try:
            selected_features = [self.features_listbox.get(i) for i in self.features_listbox.curselection()]
            selected_target = self.target_combobox.get()
        
            if not selected_features or not selected_target:
                self.show_message("Error", "Please select at least one feature and one target column.")
                return
        
            X = self.data_frame[selected_features]
            y = self.data_frame[selected_target]

            imputer = SimpleImputer(strategy='mean')
            X = imputer.fit_transform(X)
            y = pd.Series(SimpleImputer(strategy='mean').fit_transform(y.values.reshape(-1, 1)).flatten())

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            model = LinearRegression()
            model.fit(X_train, y_train)

            y_pred = model.predict(X)
            ecm_total = mean_squared_error(y, y_pred)
            r2_total = r2_score(y, y_pred)

            results_text = f"Model Results:\nTotal ECM: {ecm_total:.2f}\nTotal R²: {r2_total:.2f}"
            self.results_label.config(text=results_text)

            self.display_model_formula(model, selected_features, selected_target)

            if len(selected_features) == 1:
                self.plot_data_with_fit_line(pd.DataFrame(X, columns=selected_features), y, model)
            else:
                self.show_message("Info", "Cannot generate a plot for multiple input features.")

            self.show_message("Success", "The model has been created successfully.")
        
        except Exception as e:
            self.show_message("Error", f"An error occurred during model creation: {str(e)}")

    def display_model_formula(self, model, selected_features, target):
        intercept = model.intercept_
        coefficients = model.coef_
        terms = [f"{coef:.2f} * {feature}" for coef, feature in zip(coefficients, selected_features)]
        formula = f"{target} = {intercept:.2f} + " + " + ".join(terms)
        
        self.model_formula_label.config(text=f"Model Formula:\n{formula}")

    def plot_data_with_fit_line(self, X, y, model):
        if X.shape[1] == 1:
            plt.figure(figsize=(10, 6))
            plt.scatter(X, y, color='blue', label="Data Points")
            plt.plot(X, model.predict(X), color='red', linewidth=2, label="Fit Line")
            plt.xlabel(X.columns[0])
            plt.ylabel(y.name)
            plt.title("Data and Linear Fit Line")
            plt.legend()
            plt.show()
        else:
            self.show_message("Error", "Cannot generate plot with multiple input features.")

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataLoaderApp(root)
    root.mainloop()
