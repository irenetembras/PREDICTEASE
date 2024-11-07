import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import modulo_importacion
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DataLoaderApp:
    """Aplicación para cargar y visualizar datos, manejar NaNs, y crear un modelo de regresión lineal con métricas de error."""
    
    def __init__(self, root):
        root.state('zoomed')
        self.root = root
        self.root.title("Data Loader")
        self.root.configure(bg="white")
        self.font_style = ("Helvetica", 10)

        self.toolbar_color = "#e0e0e0"
        self.hover_color = "#c0c0c0"

        self.toolbar = tk.Frame(root, bg=self.toolbar_color, height=40)
        self.toolbar.pack(side="top", fill="x")

        self.file_menu_button = tk.Menubutton(self.toolbar, text="File", font=self.font_style, bg=self.toolbar_color, fg="black", bd=0, padx=20, pady=5)
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0)
        self.file_menu.add_command(label="Load Dataset", command=self.load_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.file_menu_button.config(menu=self.file_menu)
        self.file_menu_button.pack(side="left", padx=10)
        self.add_hover_effect(self.file_menu_button)

        self.data_menu_button = tk.Menubutton(self.toolbar, text="Data", font=self.font_style, bg=self.toolbar_color, fg="black", bd=0, padx=20, pady=5)
        self.data_menu = tk.Menu(self.data_menu_button, tearoff=0)
        self.data_menu.add_command(label="Remove rows with NaN", command=lambda: self.handle_nan(option="1"))
        self.data_menu.add_command(label="Fill with Mean", command=lambda: self.handle_nan(option="2"))
        self.data_menu.add_command(label="Fill with Median", command=lambda: self.handle_nan(option="3"))
        self.data_menu.add_command(label="Fill with Constant", command=lambda: self.handle_nan(option="4"))
        self.data_menu_button.config(menu=self.data_menu)
        self.data_menu_button.pack(side="left", padx=2)
        self.add_hover_effect(self.data_menu_button)

        self.regression_menu_button = tk.Menubutton(self.toolbar, text="Regression", font=self.font_style, bg=self.toolbar_color, fg="black", bd=0, padx=20, pady=5)
        self.regression_menu = tk.Menu(self.regression_menu_button, tearoff=0)
        self.regression_menu.add_command(label="Select Columns for Regression", command=self.show_regression_selector)
        self.regression_menu.add_command(label="Create Regression Model", command=self.create_regression_model)
        self.regression_menu_button.config(menu=self.regression_menu)
        self.regression_menu_button.pack(side="left", padx=2)
        self.add_hover_effect(self.regression_menu_button)

        self.file_path_label = tk.Label(root, text="No file selected", font=self.font_style, bg="white", fg="black")
        self.file_path_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=300, style="TProgressbar")
        style = ttk.Style()
        style.configure("TProgressbar", thickness=5, troughcolor="white", background="#007BFF", troughrelief="flat")
        style.configure("Treeview.Heading", font=("Helvetica", 12), background="#f0f0f0", foreground="black", borderwidth=1)
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#007BFF")], foreground=[("selected", "white")])

        self.data_frame = None
        self.table_frame = None
        self.selected_input = None
        self.selected_output = None
        self.model_description = ""  # Variable to hold the model description

        self.root.bind("<Escape>", lambda e: self.root.state('normal'))

    def add_hover_effect(self, widget):
        widget.bind("<Enter>", lambda e: widget.config(bg=self.hover_color))
        widget.bind("<Leave>", lambda e: widget.config(bg=self.toolbar_color))

    def load_file(self):
        file_types = [("CSV Files", ".csv"), ("Excel Files", ".xlsx .xls"), ("SQLite Files", ".sqlite *.db")]
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

    def show_success_message(self):
        messagebox.showinfo("Success", "File loaded successfully.")

    def show_error_message(self, message):
        messagebox.showerror("Error", f"An error occurred: {message}")

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
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        regression_window = tk.Toplevel(self.root)
        regression_window.title("Select Columns for Regression")
        regression_window.geometry("400x300")

        input_label = tk.Label(regression_window, text="Select input column:", font=self.font_style)
        input_label.pack(anchor="w", padx=10, pady=5)

        input_selector = ttk.Combobox(regression_window, values=list(self.data_frame.columns), state="readonly")
        input_selector.pack(fill=tk.X, padx=10, pady=5)

        output_label = tk.Label(regression_window, text="Select output column:", font=self.font_style)
        output_label.pack(anchor="w", padx=10, pady=5)

        output_selector = ttk.Combobox(regression_window, values=list(self.data_frame.columns), state="readonly")
        output_selector.pack(fill=tk.X, padx=10, pady=5)

        description_label = tk.Label(regression_window, text="Enter model description (optional):", font=self.font_style)
        description_label.pack(anchor="w", padx=10, pady=5)

        self.description_text = tk.Text(regression_window, height=5, width=40)
        self.description_text.pack(padx=10, pady=5)

        select_button = tk.Button(regression_window, text="Select", command=lambda: self.confirm_selection(input_selector, output_selector, regression_window))
        select_button.pack(pady=10)

    def confirm_selection(self, input_selector, output_selector, regression_window):
        self.selected_input = input_selector.get()
        self.selected_output = output_selector.get()
        self.model_description = self.description_text.get("1.0", "end-1c").strip()  # Get the description text
        
        if not self.selected_input or not self.selected_output:
            messagebox.showwarning("Warning", "Please select both an input and an output column.")
            return
        
        if not self.model_description:
            messagebox.showinfo("Info", "Model description is optional. Proceeding without it.")

        messagebox.showinfo("Success", f"Selected columns:\nInput: {self.selected_input}\nOutput: {self.selected_output}")
        regression_window.destroy()

    def handle_nan(self, option):
        """Maneja valores NaN en el DataFrame según la opción seleccionada: eliminar, rellenar con media, mediana o un valor constante."""
        if self.data_frame is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        def get_decimal_places(series):
            decimals = series.astype(str).str.extract(r'\.(\d+)').dropna()
            return max(decimals[0].str.len().max(), 0) if not decimals.empty else 0

        if option == "1":
            self.data_frame.dropna(inplace=True)
            messagebox.showinfo("Success", "Rows with NaN values removed.")
        elif option == "2":
            numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_columns:
                mean_value = self.data_frame[col].mean()
                decimal_places = get_decimal_places(self.data_frame[col])
                rounded_mean_value = round(mean_value, int(decimal_places))
                self.data_frame[col].fillna(rounded_mean_value, inplace=True)
            messagebox.showinfo("Success", "NaN values filled with column mean.")
        elif option == "3":
            numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_columns:
                median_value = self.data_frame[col].median()
                decimal_places = get_decimal_places(self.data_frame[col])
                rounded_median_value = round(median_value, int(decimal_places))
                self.data_frame[col].fillna(rounded_median_value, inplace=True)
            messagebox.showinfo("Success", "NaN values filled with column median.")
        elif option == "4":
            constant_value = simpledialog.askstring("Input", "Enter a constant value:")
            if constant_value is not None:
                try:
                    constant_value = float(constant_value)
                except ValueError:
                    pass
                self.data_frame.fillna(constant_value, inplace=True)
                messagebox.showinfo("Success", f"NaN values filled with constant value: {constant_value}")
        
        self.display_data()

    def create_regression_model(self):
        """Crea el modelo de regresión lineal, mostrando los resultados, métricas y gráfico, si es aplicable."""
        if self.data_frame is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return
        if not self.selected_input or not self.selected_output:
            messagebox.showwarning("Warning", "No columns selected for regression.")
            return

        try:
            X = self.data_frame[[self.selected_input]].values
            y = self.data_frame[self.selected_output].values

            model = LinearRegression()
            model.fit(X, y)
            predictions = model.predict(X)
            mse = mean_squared_error(y, predictions)
            r2 = r2_score(y, predictions)

            print(f"Model Description: {self.model_description}")

            messagebox.showinfo("Model Created", f"Model created successfully.\nR²: {r2:.2f}\nMSE: {mse:.2f}")
            intercept = model.intercept_
            coef = model.coef_[0]
            formula = f"{self.selected_output} = {coef:.2f} * {self.selected_input} + {intercept:.2f}"
            messagebox.showinfo("Formula", f"Regression formula:\n{formula}")

            if self.data_frame[self.selected_input].dtype in [np.float64, np.int64] and self.data_frame[self.selected_output].dtype in [np.float64, np.int64]:
                fig, ax = plt.subplots()
                ax.scatter(X, y, color="blue", label="Data points")
                ax.plot(X, predictions, color="red", label="Regression line")
                ax.set_xlabel(self.selected_input)
                ax.set_ylabel(self.selected_output)
                ax.legend()
                ax.set_title("Regression Line")

                graph_window = tk.Toplevel(self.root)
                graph_window.title("Regression Plot")
                description_label = tk.Label(graph_window, text=f"Model Description: {self.model_description}", font=self.font_style, justify="left", wraplength=400)
                description_label.pack(padx=10, pady=10)
                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                messagebox.showinfo("Graph Not Available", "Graph not available for non-numeric or multiple input columns.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the model: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataLoaderApp(root)
    root.mainloop()
