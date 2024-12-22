# src/gui/app.py
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import pandas as pd
from src.gui.hover_tooltip import HoverTooltip
from src.data.file_importer import import_file
from src.data.data_handler import handle_nan_values
from src.models.regression import LinearRegressionModel
from src.models.model_io import save_model_data, load_model_data
from src.visualization.plotting import plot_regression_line
from src.visualization.data_display import display_dataframe_in_treeview
from src.gui.loading_indicator import show_loading_indicator, hide_loading_indicator


class DataLoaderApp:
    """
    This class implements an application that allows the user to:
    1. Load and visualize data (displaying it in a table),
    2. Manage missing values (NaNs),
    3. Create a linear regression model with error metrics,
    4. Save and load models,
    5. Make predictions with a trained model.
    """

    def __init__(self, root):
        # Maximize the main window (or set it to a 'zoomed' state)
        root.state('zoomed')
        self.root = root
        self.root.title("PredictEase")
        self.root.configure(bg="#f0f0f0")

        # Tooltip instance (for showing formula on hover)
        self.tooltip = None

        # Set a default font style
        self.font_style = ("Helvetica", 10)

        # Initialize variables to store data and model info
        self.df = None                # Will store the loaded dataset (pandas DataFrame)
        self.selected_input = None    # The chosen input column (for regression)
        self.selected_output = None   # The chosen output column (for regression)
        self.model_description = ""   # Optional text describing the model
        self.model = None             # Will hold the trained regression model

        # Build the various parts of the GUI
        self.build_toolbar()
        self.build_labels()
        self.build_table_frame()
        self.build_controls_frame()
        self.build_results_table()
        self.build_graph_frame()

        # Display a welcome message to the user
        messagebox.showinfo(
            "Welcome to PredictEase",
            "Welcome to the PredictEase application!\n\n"
            "This tool allows you to:\n"
            "1. Load and Visualize Data\n"
            "2. Manage Missing Values\n"
            "3. Create Linear Regression Models\n"
            "4. Save and Load Models\n"
            "5. Make a Prediction\n\n"
            "To get started:\n"
            "- Navigate to the 'File' menu to load a dataset or an existing model.\n"
            "- Use the 'Data' menu to preprocess your data.\n"
            "- In the 'Regression Controls' section, select your desired columns and create a regression model.\n"
            "- Save your model using the 'Save Model' button for future reference.\n"
            "- Use the 'Prediction' menu to make a prediction using your model."
        )

    def build_toolbar(self):
        """
        Build the top toolbar that contains menus: File, Data, and Prediction.
        """
        self.toolbar = tk.Frame(self.root, bg="#3e3e3e", height=40)
        self.toolbar.pack(side="top", fill="x")

        # -- FILE MENU --
        self.file_menu_button = tk.Menubutton(
            self.toolbar, text="File", font=self.font_style,
            bg="#3e3e3e", fg="white", bd=0,
            padx=20, pady=5,
            activebackground="#5e5e5e", activeforeground="white"
        )
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0, bg="#5e5e5e", fg="white")
        self.file_menu.add_command(label="Load Dataset", command=self.load_file)
        self.file_menu.add_command(label="Load Model", command=self.load_model)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.file_menu_button.config(menu=self.file_menu)
        self.file_menu_button.pack(side="left", padx=10)

        # -- DATA MENU --
        self.data_menu_button = tk.Menubutton(
            self.toolbar, text="Data", font=self.font_style,
            bg="#3e3e3e", fg="white", bd=0,
            padx=20, pady=5,
            activebackground="#5e5e5e", activeforeground="white"
        )
        self.data_menu = tk.Menu(self.data_menu_button, tearoff=0, bg="#5e5e5e", fg="white")
        self.data_menu.add_command(label="Remove rows with NaN", command=lambda: self.handle_nan(option="1"))
        self.data_menu.add_command(label="Fill with Mean", command=lambda: self.handle_nan(option="2"))
        self.data_menu.add_command(label="Fill with Median", command=lambda: self.handle_nan(option="3"))
        self.data_menu.add_command(label="Fill with Constant", command=lambda: self.handle_nan(option="4"))
        self.data_menu_button.config(menu=self.data_menu)
        self.data_menu_button.pack(side="left", padx=2)

        # -- PREDICTION MENU (DISABLED INITIALLY) --
        self.prediction_menu_button = tk.Menubutton(
            self.toolbar, text="Prediction", font=self.font_style,
            bg="#3e3e3e", fg="white", bd=0,
            padx=20, pady=5, state='disabled',
            activebackground="#5e5e5e", activeforeground="white"
        )
        self.prediction_menu = tk.Menu(self.prediction_menu_button, tearoff=0, bg="#5e5e5e", fg="white")
        self.prediction_menu.add_command(label="Make Prediction", command=self.make_prediction_dialog)
        self.prediction_menu_button.config(menu=self.prediction_menu)
        self.prediction_menu_button.pack(side="left", padx=2)

    def build_labels(self):
        """
        Build the label that displays the path of the file currently loaded.
        """
        self.file_path_label = tk.Label(
            self.root, text="No file selected", font=self.font_style,
            bg="#f0f0f0", fg="black"
        )
        self.file_path_label.pack(pady=10)

    def build_table_frame(self):
        """
        Create the frame that will contain the data table (DataFrame).
        """
        self.table_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.table_frame_border.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.table_frame = tk.Frame(self.table_frame_border, bg="white")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def build_controls_frame(self):
        """
        Create the frame on the left side that contains the controls
        (column selectors, buttons, etc.) for regression and model handling.
        """
        self.controls_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.controls_frame_border.pack(side="left", fill="y", padx=10, pady=5)

        self.controls_frame = tk.Frame(self.controls_frame_border, bg="white")
        self.controls_frame.pack(fill="both", padx=5, pady=5)

        # -- Input column selector --
        input_label = tk.Label(
            self.controls_frame, text="Select input column:",
            font=self.font_style, bg="white"
        )
        input_label.pack(anchor="w", padx=10, pady=5)
        self.input_selector = ttk.Combobox(self.controls_frame, state="readonly")
        self.input_selector.pack(fill=tk.X, padx=10, pady=5)

        # -- Output column selector --
        output_label = tk.Label(
            self.controls_frame, text="Select output column:",
            font=self.font_style, bg="white"
        )
        output_label.pack(anchor="w", padx=10, pady=5)
        self.output_selector = ttk.Combobox(self.controls_frame, state="readonly")
        self.output_selector.pack(fill=tk.X, padx=10, pady=5)

        # -- Model description --
        description_label = tk.Label(
            self.controls_frame, text="Enter model description (optional):",
            font=self.font_style, bg="white"
        )
        description_label.pack(anchor="w", padx=10, pady=5)
        self.dtext = tk.Text(self.controls_frame, height=2, width=30)
        self.dtext.pack(padx=10, pady=5)

        # -- Create Model button --
        create_button = tk.Button(
            self.controls_frame, text="Create Model", command=self.create_regression_model,
            font=self.font_style, bg="#4CAF50", fg="white", activebackground="#45a049"
        )
        create_button.pack(pady=10, padx=10, fill=tk.X)

        # -- Save Model button --
        save_button = tk.Button(
            self.controls_frame, text="Save Model", command=self.save_model,
            font=self.font_style, bg="#2196F3", fg="white", activebackground="#0b7dda"
        )
        save_button.pack(pady=5, padx=10, fill=tk.X)

    def build_results_table(self):
        """
        Create a small results table (treeview) inside the controls_frame
        to display metrics like Formula, R², MSE, etc.
        """
        self.results_table = ttk.Treeview(
            self.controls_frame, columns=("Name", "Value"), show='headings', height=5
        )
        self.results_table.heading("Name", text="Name")
        self.results_table.heading("Value", text="Value")
        self.results_table.column("Name", anchor="center", width=150)
        self.results_table.column("Value", anchor="center", width=200)
        self.results_table.pack(pady=10, padx=10, fill=tk.BOTH)

        # Initialize table with placeholders
        self.results_names = ["Formula", "R²", "MSE", "Description", "Prediction Result"]
        self.results_items = []
        for name in self.results_names:
            item_id = self.results_table.insert("", "end", values=(name, "-"))
            self.results_items.append(item_id)

        # BIND the motion event so we can show tooltips on the "Value" column
        self.results_table.bind("<Motion>", self.on_treeview_motion)

    def on_treeview_motion(self, event):
        """
        Called whenever the mouse moves over the results_table.
        We'll check which row/column we're on, and show/hide tooltip accordingly.
        """
        # Identify the row and column under the mouse
        row_id = self.results_table.identify_row(event.y)
        col_id = self.results_table.identify_column(event.x)

        # Nous ne voulons l'infobulle que sur la colonne "Value" (#2)
        if col_id == "#2" and row_id:
            # Récupère le texte complet dans le tuple "values"
            item_values = self.results_table.item(row_id, "values")
            if len(item_values) >= 2:
                full_text = item_values[1]  # La deuxième valeur = "Value"

                # Calcule la position où afficher l'infobulle (décalage léger)
                x_root = self.results_table.winfo_rootx() + event.x + 20
                y_root = self.results_table.winfo_rooty() + event.y + 20

                # Affiche ou met à jour l'infobulle
                if not self.tooltip:
                    self.tooltip = HoverTooltip(self.root, text=full_text)
                    self.tooltip.show(x_root, y_root)
                else:
                    self.tooltip.text = full_text
                    self.tooltip.hide()
                    self.tooltip.show(x_root, y_root)
            else:
                # Pas de texte -> on masque l'infobulle
                if self.tooltip:
                    self.tooltip.hide()
        else:
            # Souris hors de la colonne #2 ou ligne invalide -> on masque l'infobulle
            if self.tooltip:
                self.tooltip.hide()

    def build_graph_frame(self):
        """
        Create the frame (on the right side) that will hold the graph / plot.
        """
        self.graph_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.graph_frame_border.pack(side="right", fill="y", padx=10, pady=5)

        self.graph_frame_border.pack_propagate(False)
        self.graph_frame_border.config(height=300)  # Ajuster selon vos besoins

        self.graph_frame = tk.Frame(self.graph_frame_border, bg="white")
        self.graph_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def load_file(self):
        """
        Load a data file (CSV, Excel, or SQLite) using a file dialog, then process it.
        """
        file_types = [
            ("CSV Files", ".csv"),
            ("Excel Files", ".xlsx .xls"),
            ("SQLite Files", ".sqlite *.db")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            # Update the label to show the selected file path
            self.file_path_label.config(text=file_path)

            # Reset controls and clear existing graph
            self.reset_controls()
            self.clear_graph()

            # If a model was previously loaded, remove that UI and restore main frames
            if hasattr(self, 'model_details_frame') and self.model_details_frame:
                self.model_details_frame.destroy()
            if hasattr(self, 'prediction_frame') and self.prediction_frame:
                self.prediction_frame.destroy()

            # Re-pack the frames that might have been hidden
            self.file_path_label.pack(pady=10)
            self.table_frame_border.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            self.controls_frame_border.pack(side="left", fill="y", padx=10, pady=5)
            self.graph_frame_border.pack(side="right", fill=tk.BOTH, expand=True, padx=10, pady=5)

            # Disable the "Prediction" menu again if a new dataset is loaded
            self.prediction_menu_button.config(state='disabled')

            # Use a separate thread to import/process the file
            threading.Thread(target=self.process_import, args=(file_path,)).start()

    def process_import(self, file_path):
        """
        Threaded function that imports the dataset and updates the GUI accordingly.
        """
        show_loading_indicator(self.root, "Loading dataset, please wait...")
        try:
            # Check if the file is empty
            if os.path.getsize(file_path) == 0:
                raise ValueError("The selected file is empty (size is zero bytes).")

            # Import the file (CSV, Excel, or SQLite)
            self.df = import_file(file_path)

            # Check if the resulting DataFrame is empty
            if self.df is None or self.df.empty:
                raise ValueError("The imported file is empty (no rows or columns found).")

            # Check if columns are all empty
            if not self.df.columns.any() or self.df.dropna(how='all').empty:
                raise ValueError("The imported file has only empty columns or rows.")

            # Check for missing values
            if self.df.isnull().values.any():
                nan_counts = self.df.isnull().sum()
                nan_columns = nan_counts[nan_counts > 0].index.tolist()
                total_nans = nan_counts.sum()
                message = (
                    f"The dataset contains {total_nans} missing values "
                    f"in columns: {', '.join(nan_columns)}"
                )
                self.root.after(0, lambda: messagebox.showinfo("Missing Values Detected", message))

            # Update the UI in the main thread
            self.root.after(0, self.display_data)
            self.root.after(0, self.populate_selectors)
            self.root.after(0, lambda: messagebox.showinfo("Success", "File loaded successfully."))

        except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError):
            error_message = "Invalid or corrupted file."
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))
        finally:
            hide_loading_indicator(self.root)

    def display_data(self):
        """
        Display the current DataFrame 'self.df' in the table_frame using the helper function.
        """
        display_dataframe_in_treeview(self.df, self.table_frame)

    def populate_selectors(self):
        """
        Fill the comboboxes (input_selector, output_selector) with the columns from the loaded DataFrame.
        """
        if self.df is not None:
            columns = list(self.df.columns)
            self.input_selector['values'] = columns
            self.output_selector['values'] = columns

    def handle_nan(self, option):
        """
        Handle NaN values in the DataFrame by removing or filling them (mean, median, etc.),
        depending on the user's choice (option).
        """
        if self.df is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        show_loading_indicator(self.root, "Processing data, please wait...")
        threading.Thread(target=self._handle_nan_thread, args=(option,)).start()

    def _handle_nan_thread(self, option):
        """
        Threaded function to handle NaN values (remove rows, fill with mean, median, or constant).
        """
        try:
            self.df, success_message = handle_nan_values(self.df, option)
            if self.df is not None:
                self.root.after(0, self.display_data)
                self.root.after(0, lambda: messagebox.showinfo("Success", success_message))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Info", success_message))

        except Exception as e:
            error_message = f"An error occurred while handling NaN values: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))
        finally:
            hide_loading_indicator(self.root)

    def create_regression_model(self):
        """
        Triggered when user clicks 'Create Model'. Creates a linear regression model
        using the selected columns from the DataFrame.
        """
        if self.df is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        self.selected_input = self.input_selector.get()
        self.selected_output = self.output_selector.get()

        if not self.selected_input or not self.selected_output:
            messagebox.showwarning("Warning", "No columns selected for regression.")
            return

        self.model_description = self.dtext.get("1.0", "end-1c").strip()
        if not self.model_description:
            proceed = messagebox.askyesno("Missing Description", "No model description provided. Do you want to continue?")
            if not proceed:
                return

        show_loading_indicator(self.root, "Creating regression model, please wait...")
        threading.Thread(target=self._create_model_thread).start()

    def _create_model_thread(self):
        """
        Threaded function that actually builds the linear regression model,
        calculates metrics, and updates the UI.
        """
        try:
            # Extract X and y from the DataFrame columns
            X = self.df[[self.selected_input]].values
            y = self.df[self.selected_output].values

            # Create and fit the model
            model = LinearRegressionModel()
            model.fit(X, y)

            # Generate predictions and compute metrics
            predictions = model.predict(X)
            mse = model.mean_squared_error(y, predictions)
            r2 = model.r2_score(y, predictions)
            formula = model.get_formula(self.selected_input, self.selected_output)

            # Store data for plotting
            self.X_plot = X
            self.y_plot = y
            self.predictions_plot = predictions
            self.model = model

            # Update the GUI (main thread)
            self.root.after(0, lambda: self.update_after_model_creation(formula, r2, mse))

        except Exception as e:
            error_message = f"An error occurred while creating the model: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))
        finally:
            hide_loading_indicator(self.root)

    def update_after_model_creation(self, formula, r2, mse):
        """
        Called once the regression model is created. Plots the regression line,
        displays success info, and updates the results table.
        """
        # Clear the previous graph and plot the new one
        self.clear_graph()
        plot_regression_line(
            self.X_plot, self.y_plot, self.predictions_plot,
            self.selected_input, self.selected_output, self.graph_frame
        )

        # Inform the user
        messagebox.showinfo("Success", "Regression model created successfully.")

        # Enable the 'Prediction' menu
        self.prediction_menu_button.config(state='normal')

        # Update the table of results (Formula, R², MSE, etc.)
        self.update_results_table({
            "Formula": formula,
            "R²": f"{r2:.2f}",
            "MSE": f"{mse:.2f}",
            "Description": self.model_description or "No description provided",
            "Prediction Result": "-"
        })

    def save_model(self):
        """
        Saves the current regression model and its info (formula, metrics, etc.) to a file.
        """
        if self.model is None:
            messagebox.showwarning("Warning", "No model has been created to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".joblib",
            filetypes=[("Joblib files", "*.joblib"), ("Pickle files", "*.pkl")]
        )
        if not file_path:
            return  # The user canceled the save dialog

        try:
            # Prepare the model data to save
            model_data = {
                'input_column': self.selected_input,
                'output_column': self.selected_output,
                'model_description': self.model_description or "No description provided",
                'formula': self.model.get_formula(self.selected_input, self.selected_output),
                'metrics': {
                    'R²': self.model.r2_score(self.y_plot, self.predictions_plot),
                    'MSE': self.model.mean_squared_error(self.y_plot, self.predictions_plot)
                },
                'model': self.model  # The actual model object
            }
            # Save it
            save_model_data(model_data, file_path)
            messagebox.showinfo("Success", f"Model data saved successfully at {file_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the model: {e}")

    def load_model(self):
        """
        Loads a previously saved model (joblib/pickle), displays the model info,
        and allows the user to make predictions with it.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Joblib files", "*.joblib"), ("Pickle files", "*.pkl")]
        )
        if not file_path:
            return  # User canceled

        try:
            # Load the model data
            model_data = load_model_data(file_path)

            # Extract info from the loaded dictionary
            self.selected_input = model_data['input_column']
            self.selected_output = model_data['output_column']
            self.model_description = model_data.get('model_description', 'No description provided')
            formula = model_data['formula']
            r2 = model_data['metrics']['R²']
            mse = model_data['metrics']['MSE']
            self.model = model_data.get('model', None)

            if self.model is None:
                raise ValueError("The model object is missing in the loaded file.")

            # Update the interface to show the model's details
            self.update_interface_for_model(formula, r2, mse)
            messagebox.showinfo("Success", "Model loaded successfully.")

        except Exception as e:
            error_message = f"Error while loading the model: {str(e)}"
            messagebox.showerror("Error", error_message)

    def update_interface_for_model(self, formula, r2, mse):
        """
        When a model is loaded, we hide the normal frames (table, controls, etc.)
        and show a new frame with the model info, plus a separate area for predictions.
        """
        # Hide the usual sections
        self.file_path_label.pack_forget()
        self.table_frame_border.pack_forget()
        self.controls_frame_border.pack_forget()
        self.graph_frame_border.pack_forget()

        # Destroy any existing frames (if we had a model loaded previously)
        if hasattr(self, 'model_details_frame') and self.model_details_frame:
            self.model_details_frame.destroy()
        if hasattr(self, 'prediction_frame') and self.prediction_frame:
            self.prediction_frame.destroy()

        # Create a new frame to display the model details
        self.model_details_frame = tk.Frame(self.root, bg="white", bd=2, relief="groove")
        self.model_details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        if not self.model_description or self.model_description.strip() == "":
            self.model_description = "No description provided"

        model_info = (
            f"Formula: {formula}\n"
            f"R²: {r2:.2f}\n"
            f"MSE: {mse:.2f}\n\n"
            f"Description: {self.model_description}"
        )
        self.model_info_label = tk.Label(
            self.model_details_frame, text=model_info, font=("Helvetica", 12),
            fg="black", justify="center", bg="white"
        )
        self.model_info_label.pack(pady=10, padx=10, expand=True)

        self.prediction_frame = tk.Frame(self.root, bg="white", bd=2, relief="groove")
        self.prediction_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.prediction_result_label_loaded = tk.Label(
            self.prediction_frame,
            text="Prediction Result: (No prediction made yet)",
            font=("Helvetica", 12),
            fg="green",
            justify="center",
            bg="white"
        )
        self.prediction_result_label_loaded.pack(pady=10, padx=10, expand=True)

        # Re-enable the Prediction menu
        self.prediction_menu_button.config(state='normal')

    def make_prediction_dialog(self):
        """
        Opens a dialog so the user can type in a value for the input column,
        then it performs the prediction using the loaded/created model.
        """
        if self.model is None:
            messagebox.showwarning("Warning", "No model is available for prediction.")
            return

        input_prompt = f"Enter a value for {self.selected_input}:"
        input_value = simpledialog.askstring("Prediction Input", input_prompt)
        if input_value is None:
            # User canceled the dialog
            return

        try:
            input_value = float(input_value)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input value. Please enter a numeric value.")
            return

        try:
            X_new = [[input_value]]
            y_pred = self.model.predict(X_new)
            prediction_text = f"Predicted {self.selected_output}: {y_pred[0]:.2f}"

            if hasattr(self, 'prediction_result_label_loaded'):
                self.prediction_result_label_loaded.config(text=prediction_text)
            else:
                self.update_results_table({"Prediction Result": f"{y_pred[0]:.2f}"})

        except Exception as e:
            messagebox.showerror("Prediction Error", f"An error occurred during prediction: {e}")

    def update_results_table(self, updates):
        """
        Update the Treeview results table (Formula, R², MSE, etc.).
        'updates' is a dict where the keys match our self.results_names entries.
        """
        for idx, name in enumerate(self.results_names):
            if name in updates:
                value = updates[name]
                item_id = self.results_items[idx]
                self.results_table.item(item_id, values=(name, value))

    def reset_controls(self):
        """
        Clears the input/output combo boxes, the description field,
        and resets the results table placeholders.
        """
        self.input_selector.set('')
        self.output_selector.set('')
        self.dtext.delete('1.0', tk.END)
        for idx, name in enumerate(self.results_names):
            item_id = self.results_items[idx]
            self.results_table.item(item_id, values=(name, "-"))

    def clear_graph(self):
        """
        Destroys any existing widgets in the graph_frame (i.e., clears the plot).
        """
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
