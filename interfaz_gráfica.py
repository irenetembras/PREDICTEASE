import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import threading
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import joblib
import modulo_importacion

class DataLoaderApp:
    """Application to load, clean, visualize data, and create linear regression models with error metrics."""

    def __init__(self, root):
        self.setup_root(root)
        self.setup_toolbar()
        self.setup_data_controls()
        self.setup_regression_controls()
        self.setup_result_display()
        self.setup_graph_display()
        
        # Initialize main variables
        self.data_frame = None
        self.model = None

    def setup_root(self, root):
        """Configure main window properties."""
        root.state('zoomed')
        root.title("Data Loader")
        root.configure(bg="white")
        self.root = root
        self.font_style = ("Helvetica", 10)

    def setup_toolbar(self):
        """Setup toolbar with file and data menu options."""
        toolbar = tk.Frame(self.root, bg="#e0e0e0", height=40)
        toolbar.pack(side="top", fill="x")

        file_menu_button = self.create_menu_button(toolbar, "File", [("Load Dataset", self.load_file),
                                                                     ("Load Model", self.load_model),
                                                                     ("Exit", self.root.quit)])
        file_menu_button.pack(side="left", padx=10)

        data_menu_button = self.create_menu_button(toolbar, "Data", [("Remove rows with NaN", lambda: self.handle_nan("1")),
                                                                     ("Fill with Mean", lambda: self.handle_nan("2")),
                                                                     ("Fill with Median", lambda: self.handle_nan("3")),
                                                                     ("Fill with Constant", lambda: self.handle_nan("4"))])
        data_menu_button.pack(side="left", padx=2)

    def create_menu_button(self, parent, text, commands):
        """Helper to create a menu button with commands."""
        menu_button = tk.Menubutton(parent, text=text, font=self.font_style, bg="#e0e0e0", fg="black", bd=0, padx=20, pady=5)
        menu = tk.Menu(menu_button, tearoff=0)
        for label, command in commands:
            if label == "Exit":
                menu.add_separator()
            menu.add_command(label=label, command=command)
        menu_button.config(menu=menu)
        return menu_button

    def setup_data_controls(self):
        """Setup the data controls for file path label and data table frame."""
        self.file_path_label = tk.Label(self.root, text="No file selected", font=self.font_style, bg="white", fg="black")
        self.file_path_label.pack(pady=10)
        self.table_frame = self.create_frame(self.root, "#cccccc", "#f9f9f9")

    def setup_regression_controls(self):
        """Setup the regression control panel for selecting input/output and creating the model."""
        self.controls_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.controls_frame_border.pack(side="left", fill="y", padx=10, pady=5)  # Usa fill="y" aquí sin conflicto
        self.controls_frame = tk.Frame(self.controls_frame_border, bg="#f9f9f9")
        self.controls_frame.pack(fill="both", padx=5, pady=5)

    def create_text_box(self, parent, label_text, height, width):
        """Helper to create a text box with a label."""
        label = tk.Label(parent, text=label_text, font=self.font_style, bg="#f9f9f9")
        label.pack(anchor="w", padx=10, pady=5)
        text_box = tk.Text(parent, height=height, width=width)
        text_box.pack(padx=10, pady=5)
        return text_box

    def setup_column_selectors(self):
        """Setup input/output column selectors for regression."""
        self.input_selector = self.create_combobox(self.controls_frame, "Select input column:")
        self.output_selector = self.create_combobox(self.controls_frame, "Select output column:")

    def create_combobox(self, parent, label_text):
        """Helper to create a combobox with a label."""
        label = tk.Label(parent, text=label_text, font=self.font_style, bg="#f9f9f9")
        label.pack(anchor="w", padx=10, pady=5)
        combobox = ttk.Combobox(parent, state="readonly")
        combobox.pack(fill=tk.X, padx=10, pady=5)
        return combobox

    def setup_result_display(self):
        """Setup label to display regression results."""
        self.result_label = tk.Label(self.controls_frame, text="", font=self.font_style, fg="blue", justify="left", bg="#f9f9f9")
        self.result_label.pack(pady=10)

    def setup_graph_display(self):
        """Setup frame for displaying the regression graph."""
        self.graph_frame = self.create_frame(self.root, "#cccccc", "#f9f9f9", side="right")

    def create_frame(self, parent, border_color, bg_color, **pack_options):
        """Helper to create a bordered frame with specified background."""
        frame_border = tk.Frame(parent, bg=border_color)
        frame_border.pack(fill=tk.BOTH, expand=True, padx=10, pady=5, **pack_options)
        frame = tk.Frame(frame_border, bg=bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return frame

    def create_button(self, parent, text, command):
        """Helper to create a button."""
        return tk.Button(parent, text=text, command=command, font=self.font_style)

    def load_file(self):
        """Load a data file for processing."""
        file_types = [("CSV Files", ".csv"), ("Excel Files", ".xlsx .xls"), ("SQLite Files", ".sqlite *.db")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.file_path_label.config(text=file_path)
            self.reset_interface()
            threading.Thread(target=self.process_import, args=(file_path,)).start()

    def reset_interface(self):
        """Reset selectors, description text, and graph display."""
        self.input_selector.set('')
        self.output_selector.set('')
        self.description_text.delete('1.0', tk.END)
        self.result_label.config(text='')
        self.clear_graph()

    def clear_graph(self):
        """Clear the graph display."""
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

    def process_import(self, file_path):
        """Process data file import and check for empty content."""
        try:
            if os.path.getsize(file_path) == 0:
                raise ValueError("The selected file is empty (size is zero bytes).")
            self.data_frame = modulo_importacion.importar_archivo(file_path)

            if self.data_frame is None or self.data_frame.empty:
                raise ValueError("The imported file has no valid content.")
            self.populate_selectors()
            messagebox.showinfo("Success", "File loaded successfully.")
            self.display_data()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def populate_selectors(self):
        """Populate column selectors with the DataFrame columns."""
        if self.data_frame is not None:
            columns = list(self.data_frame.columns)
            self.input_selector['values'] = columns
            self.output_selector['values'] = columns

    def display_data(self):
        """Display the loaded data in a table format."""
        self.clear_graph()
        self.table_frame.pack_forget()
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        vsb, hsb = ttk.Scrollbar(self.table_frame, orient="vertical"), ttk.Scrollbar(self.table_frame, orient="horizontal")
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

        self.table = ttk.Treeview(self.table_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set, style="Treeview")
        vsb.config(command=self.table.yview)
        hsb.config(command=self.table.xview)
        
        columns = list(self.data_frame.columns)
        self.table["columns"], self.table["show"] = columns, "headings"
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=100)
        for _, row in self.data_frame.iterrows():
            self.table.insert("", "end", values=list(row))



    def handle_nan(self, option):
        """Handle NaN values in the DataFrame based on the selected option."""
        if self.data_frame is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        if option == "1":
            self.data_frame = self.data_frame.dropna()
            messagebox.showinfo("Success", "Rows with NaN values removed.")
        else:
            numeric_columns = self.data_frame.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_columns:
                decimal_places = self.get_decimal_places(self.data_frame[col])
                
                if option == "2":  # Fill with mean
                    mean_value = round(self.data_frame[col].mean(), decimal_places)
                    self.data_frame[col].fillna(mean_value, inplace=True)
                elif option == "3":  # Fill with median
                    median_value = round(self.data_frame[col].median(), decimal_places)
                    self.data_frame[col].fillna(median_value, inplace=True)
                elif option == "4":  # Fill with constant
                    constant_value = simpledialog.askfloat("Input", "Enter a constant value:")
                    if constant_value is not None:
                        self.data_frame[col].fillna(round(constant_value, decimal_places), inplace=True)

            # Display success message
            fill_type = {"2": "mean", "3": "median", "4": "constant"}[option]
            messagebox.showinfo("Success", f"NaN values filled with {fill_type}.")
        
        self.display_data()

    def get_decimal_places(self, series):
        """Return the maximum number of decimal places in the series."""
        decimals = series.dropna().astype(str).str.split('.').str[1]
        return decimals.str.len().max() if not decimals.empty else 0

    def create_regression_model(self):
        """Create a linear regression model using the selected columns."""
        if self.data_frame is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        self.selected_input = self.input_selector.get()
        self.selected_output = self.output_selector.get()

        if not self.selected_input or not self.selected_output:
            messagebox.showwarning("Warning", "No columns selected for regression.")
            return

        self.model_description = self.description_text.get("1.0", "end-1c").strip()
        if not self.model_description:
            proceed = messagebox.askyesno("Missing Description", "No model description provided. Do you want to continue?")
            if not proceed:
                return

        try:
            X = self.data_frame[[self.selected_input]].values
            y = self.data_frame[self.selected_output].values

            self.model = LinearRegression()
            self.model.fit(X, y)
            predictions = self.model.predict(X)
            mse = mean_squared_error(y, predictions)
            r2 = r2_score(y, predictions)

            intercept = self.model.intercept_
            coef = self.model.coef_[0]
            formula = f"{self.selected_output} = {coef:.2f} * {self.selected_input} + {intercept:.2f}"
            self.result_label.config(text=f"Formula: {formula}\nR²: {r2:.2f}\nMSE: {mse:.2f}")

            # Clear previous graph
            self.clear_graph()

            # Create and display the graph
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(X, y, color="blue", label="Data Points")
            ax.plot(X, predictions, color="red", label="Regression Line")
            ax.set_xlabel(self.selected_input)
            ax.set_ylabel(self.selected_output)
            ax.legend()
            ax.set_title("Regression Line")

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the model: {e}")

    def save_model(self):
        """Save the linear regression model data to a file."""
        if self.model is None:
            messagebox.showwarning("Warning", "No model has been created to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pkl",
                                                 filetypes=[("Pickle files", "*.pkl"),
                                                            ("Joblib files", "*.joblib")])
        if not file_path:
            return  # Exit if no file is selected

        try:
            model_data = {
                'input_column': self.selected_input,
                'output_column': self.selected_output,
                'model_description': self.model_description,
                'formula': f"{self.selected_output} = {self.model.coef_[0]:.2f} * {self.selected_input} + {self.model.intercept_:.2f}",
                'metrics': {
                    'R²': round(r2_score(self.data_frame[self.selected_output], self.model.predict(self.data_frame[[self.selected_input]])), 2),
                    'MSE': round(mean_squared_error(self.data_frame[self.selected_output], self.model.predict(self.data_frame[[self.selected_input]])), 2)
                }
            }

            # Save model data
            joblib.dump(model_data, file_path)
            messagebox.showinfo("Success", f"Model data saved successfully at {file_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the model: {e}")

    def load_model(self):
        """Load a saved model and update the interface accordingly."""
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl"), ("Joblib files", "*.joblib")])
        if not file_path:
            return  # Exit if no file is selected

        try:
            model_data = joblib.load(file_path)

            # Extract model information
            self.selected_input = model_data['input_column']
            self.selected_output = model_data['output_column']
            self.model_description = model_data.get('model_description', 'No description provided')
            formula = model_data['formula']
            r2 = model_data['metrics']['R²']
            mse = model_data['metrics']['MSE']

            # Update the interface to display the model information
            self.update_interface_for_model(formula, r2, mse)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading the model: {str(e)}")

    def update_interface_for_model(self, formula, r2, mse):
        """Update the interface to display the loaded model's details and hide other sections."""
        if hasattr(self, 'model_details_frame') and self.model_details_frame:
            self.model_details_frame.destroy()

        # Hide sections
        self.file_path_label.pack_forget()
        self.table_frame.pack_forget()
        self.controls_frame.pack_forget()
        self.graph_frame.pack_forget()

        # Create a frame to display model details
        self.model_details_frame = tk.Frame(self.root, bg="white")
        self.model_details_frame.pack(fill=tk.BOTH, expand=True)

        # Display model details
        model_info = (
            f"Formula: {formula}\n"
            f"R²: {r2}\n"
            f"MSE: {mse}\n\n"
            f"Description: {self.model_description}"
        )
        model_info_label = tk.Label(
            self.model_details_frame,
            text=model_info,
            font=("Helvetica", 12),
            fg="black",
            justify="center",
            bg="white"
        )
        model_info_label.pack(pady=10, expand=True)




if __name__ == "__main__":
    root = tk.Tk()
    app = DataLoaderApp(root)
    root.mainloop()
