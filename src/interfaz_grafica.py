import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import joblib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import modulo_importacion

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class DataLoaderApp:
    """
    Application to load and visualize data, manage NaNs, and create a
    linear regression model with error metrics.
    """
    def __init__(self, root):
        root.state('zoomed')
        self.root = root
        self.root.title("Data Loader")
        self.root.configure(bg="#f0f0f0")  # Changed background color to a light grey
        self.font_style = ("Helvetica", 10)

        # Create the toolbar
        self.toolbar = tk.Frame(root, bg="#3e3e3e", height=40)
        self.toolbar.pack(side="top", fill="x")

        # File menu button
        self.file_menu_button = tk.Menubutton(
            self.toolbar,
            text="File",
            font=self.font_style,
            bg="#3e3e3e",
            fg="white",
            bd=0,
            padx=20,
            pady=5,
            activebackground="#5e5e5e",
            activeforeground="white"
        )
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0, bg="#5e5e5e", fg="white")
        self.file_menu.add_command(
            label="Load Dataset", command=self.load_file
        )
        self.file_menu.add_command(
            label="Load Model", command=self.load_model
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.file_menu_button.config(menu=self.file_menu)
        self.file_menu_button.pack(side="left", padx=10)

        # Data menu button
        self.data_menu_button = tk.Menubutton(
            self.toolbar,
            text="Data",
            font=self.font_style,
            bg="#3e3e3e",
            fg="white",
            bd=0,
            padx=20,
            pady=5,
            activebackground="#5e5e5e",
            activeforeground="white"
        )
        self.data_menu = tk.Menu(self.data_menu_button, tearoff=0, bg="#5e5e5e", fg="white")
        self.data_menu.add_command(
            label="Remove rows with NaN",  # Option 1
            command=lambda: self.handle_nan(option="1")
        )
        self.data_menu.add_command(
            label="Fill with Mean",  # Option 2
            command=lambda: self.handle_nan(option="2")
        )
        self.data_menu.add_command(
            label="Fill with Median",  # Option 3
            command=lambda: self.handle_nan(option="3")
        )
        self.data_menu.add_command(
            label="Fill with Constant",  # Option 4
            command=lambda: self.handle_nan(option="4")
        )
        self.data_menu_button.config(menu=self.data_menu)
        self.data_menu_button.pack(side="left", padx=2)

        # Prediction menu button (initially disabled)
        self.prediction_menu_button = tk.Menubutton(
            self.toolbar,
            text="Prediction",
            font=self.font_style,
            bg="#3e3e3e",
            fg="white",
            bd=0,
            padx=20,
            pady=5,
            state='disabled',  # Initially disabled
            activebackground="#5e5e5e",
            activeforeground="white"
        )
        self.prediction_menu = tk.Menu(self.prediction_menu_button, tearoff=0, bg="#5e5e5e", fg="white")
        self.prediction_menu.add_command(
            label="Make Prediction",
            command=self.make_prediction_dialog
        )
        self.prediction_menu_button.config(menu=self.prediction_menu)
        self.prediction_menu_button.pack(side="left", padx=2)

        # Label to display the selected file path
        self.file_path_label = tk.Label(
            root,
            text="No file selected",
            font=self.font_style,
            bg="#f0f0f0",
            fg="black"
        )
        self.file_path_label.pack(pady=10)

        # Frame for the data table
        self.table_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.table_frame_border.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.table_frame = tk.Frame(
            self.table_frame_border, bg="white"
        )
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for regression controls
        self.controls_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.controls_frame_border.pack(
            side="left", fill="y", padx=10, pady=5
        )
        self.controls_frame = tk.Frame(
            self.controls_frame_border, bg="white"
        )
        self.controls_frame.pack(fill="both", padx=5, pady=5)

        # Contents of regression control section
        input_label = tk.Label(
            self.controls_frame,
            text="Select input column:",
            font=self.font_style,
            bg="white"
        )
        input_label.pack(anchor="w", padx=10, pady=5)
        self.input_selector = ttk.Combobox(
            self.controls_frame, state="readonly"
        )
        self.input_selector.pack(fill=tk.X, padx=10, pady=5)

        output_label = tk.Label(
            self.controls_frame,
            text="Select output column:",
            font=self.font_style,
            bg="white"
        )
        output_label.pack(anchor="w", padx=10, pady=5)
        self.output_selector = ttk.Combobox(
            self.controls_frame, state="readonly"
        )
        self.output_selector.pack(fill=tk.X, padx=10, pady=5)

        description_label = tk.Label(
            self.controls_frame,
            text="Enter model description (optional):",
            font=self.font_style,
            bg="white"
        )
        description_label.pack(anchor="w", padx=10, pady=5)
        self.dtext = tk.Text(
            self.controls_frame, height=2, width=30
        )
        self.dtext.pack(padx=10, pady=5)

        create_button = tk.Button(
            self.controls_frame,
            text="Create Model",
            command=self.create_regression_model,
            font=self.font_style,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049"
        )
        create_button.pack(pady=10, padx=10, fill=tk.X)

        save_button = tk.Button(
            self.controls_frame,
            text="Save Model",
            command=self.save_model,
            font=self.font_style,
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda"
        )
        save_button.pack(pady=5, padx=10, fill=tk.X)

        # Create a results table
        self.results_table = ttk.Treeview(
            self.controls_frame,
            columns=("Name", "Value"),
            show='headings',
            height=5
        )
        self.results_table.heading("Name", text="Name")
        self.results_table.heading("Value", text="Value")
        self.results_table.column("Name", anchor="center", width=150)
        self.results_table.column("Value", anchor="center", width=200)
        self.results_table.pack(pady=10, padx=10, fill=tk.BOTH)

        # Initialize the table with placeholders
        self.results_names = ["Formula", "R²", "MSE", "Description", "Prediction Result"]
        self.results_items = []
        for name in self.results_names:
            item_id = self.results_table.insert("", "end", values=(name, "-"))
            self.results_items.append(item_id)

        # Frame for the graph
        self.graph_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.graph_frame_border.pack(
            side="right",
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )
        self.graph_frame = tk.Frame(self.graph_frame_border, bg="white")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Initialization of variables
        self.df = None
        self.selected_input = None
        self.selected_output = None
        self.model_description = ""
        self.model = None

        # Welcome message
        messagebox.showinfo(
            "Welcome to Data Loader",
            "Welcome to the Data Loader application!\n\n"
            "This tool allows you to:\n"
            "1. Load and Visualize Data\n"
            "2. Manage Missing Values\n"
            "3. Create Linear Regression Models\n"
            "4. Save and Load Models\n\n"
            "To get started:\n"
            "- Navigate to the 'File' menu to load a dataset or an existing model.\n"
            "- Use the 'Data' menu to preprocess your data.\n"
            "- In the 'Regression Controls' section, select your desired columns and create a regression model.\n"
            "- Save your model using the 'Save Model' button for future reference."
        )

    def show_loading_indicator(self, message):
        """
        Displays a loading indicator window with a progress bar.

        Parameters:
        - message (str): The message to display above the progress bar.
        """
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Loading")
        self.loading_window.resizable(False, False)
        self.loading_window.grab_set()  # Prevent interaction with the main window

        # Define the size of the window
        width = 500  # Increased width
        height = 200  # Increased height

        # Calculate x and y coordinates to center the window
        screen_width = self.loading_window.winfo_screenwidth()
        screen_height = self.loading_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the geometry of the window
        self.loading_window.geometry(f"{width}x{height}+{x}+{y}")

        # Create and pack the message label
        label = tk.Label(self.loading_window, text=message, font=("Helvetica", 12))
        label.pack(pady=30)

        # Create and pack the progress bar
        progress = ttk.Progressbar(self.loading_window, mode='indeterminate', length=400)
        progress.pack(pady=20)
        progress.start(10)  # Adjust the speed as needed

    def hide_loading_indicator(self):
        """
        Closes the loading indicator window.
        """
        if hasattr(self, 'loading_window') and self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None

    def load_file(self):
        """Loads a data file and processes it."""
        file_types = [
            ("CSV Files", ".csv"),
            ("Excel Files", ".xlsx .xls"),
            ("SQLite Files", ".sqlite *.db")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.file_path_label.config(text=file_path)

            # If model details frame exists, destroy it
            if hasattr(self, 'model_details_frame') and self.model_details_frame:
                self.model_details_frame.destroy()
            if hasattr(self, 'prediction_frame') and self.prediction_frame:
                self.prediction_frame.destroy()

            # Ensure data components are visible
            self.file_path_label.pack(pady=10)
            self.table_frame_border.pack(
                fill=tk.BOTH, expand=True, padx=10, pady=5
            )
            self.controls_frame_border.pack(
                side="left", fill="y", padx=10, pady=5
            )
            self.graph_frame_border.pack(
                side="right",
                fill=tk.BOTH,
                expand=True,
                padx=10,
                pady=5
            )
            threading.Thread(
                target=self.process_import,
                args=(file_path,)
            ).start()

            # Reset the selectors and description
            self.reset_controls()

            # Clear the graph
            self.clear_graph()

    def process_import(self, file_path):
        """Processes the import of the selected file."""
        self.show_loading_indicator("Loading dataset, please wait...")
        try:
            # Check file size before importing
            if os.path.getsize(file_path) == 0:
                raise ValueError("The selected file is empty (size is zero bytes).")

            # Import the file
            self.df = modulo_importacion.import_file(file_path)

            # Check if the DataFrame is empty after import
            if self.df is None or self.df.empty:
                raise ValueError("The imported file is empty (no rows or columns found).")

            # Check if the file contains only empty columns
            if not self.df.columns.any() or self.df.dropna(how='all').empty:
                raise ValueError("The imported file has only empty columns or rows.")

            # If everything is correct, display the data
            self.root.after(0, self.display_data)
            self.root.after(0, self.populate_selectors)
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success", "File loaded successfully."
                )
            )

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", error_message)
            )

        finally:
            self.hide_loading_indicator()

    def populate_selectors(self):
        """Fills the column selectors with the columns from the DataFrame."""
        if self.df is not None:
            columns = list(self.df.columns)
            self.input_selector['values'] = columns
            self.output_selector['values'] = columns

    def display_data(self):
        """Displays the data in a table."""
        # Ensure data frames are visible
        self.file_path_label.pack(pady=10)
        self.table_frame_border.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=5
        )
        self.controls_frame_border.pack(
            side="left", fill="y", padx=10, pady=5
        )
        self.graph_frame_border.pack(
            side="right",
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )

        # Reset controls and clear graph
        self.reset_controls()
        self.clear_graph()

        # Destroy all existing widgets in the table frame
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Create vertical and horizontal scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        # Create the treeview to display data
        self.table = ttk.Treeview(
            self.table_frame,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            style="Treeview"
        )
        self.table.pack(fill=tk.BOTH, expand=True)

        # Configure the scrollbars
        vsb.config(command=self.table.yview)
        hsb.config(command=self.table.xview)

        # Configure the columns of the table
        self.table["columns"] = list(self.df.columns)
        self.table["show"] = "headings"

        for col in self.df.columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=100)

        # Insert the data into the table
        for _, row in self.df.iterrows():
            self.table.insert("", "end", values=list(row))

    def handle_nan(self, option):
        """Handles NaN values in the DataFrame with a loading indicator."""
        if self.df is None:
            messagebox.showwarning("Warning", "No dataset loaded.")
            return

        # Define messages based on the option
        loading_messages = {
            "1": "Removing rows with NaN values, please wait...",
            "2": "Filling NaN values with column mean, please wait...",
            "3": "Filling NaN values with column median, please wait...",
            "4": "Filling NaN values with a constant value, please wait..."
        }

        # Show the loading indicator with the appropriate message
        self.show_loading_indicator(loading_messages.get(option, "Processing, please wait..."))

        # Start a thread to handle NaNs
        threading.Thread(target=self._handle_nan_thread, args=(option,)).start()

    def _handle_nan_thread(self, option):
        """
        Threaded function to handle NaN values based on the selected option.
        This ensures the GUI remains responsive during the operation.

        Parameters:
        - option (str): The option selected for handling NaN values ("1" to "4").
        """
        try:
            if option == "1":
                # Remove rows with NaN values
                self.df = self.df.dropna()
                success_message = "Rows with NaN values have been removed."
            else:
                if option == "4":  # Fill with a constant
                    constant_value_input = simpledialog.askstring(
                        "Input",
                        "Enter a constant value:"
                    )
                    if constant_value_input is None:
                        self.root.after(0, lambda: messagebox.showinfo("Cancelled", "Operation cancelled by user."))
                        self.root.after(0, self.hide_loading_indicator)
                        return  # Exit the method if the user cancels
                    try:
                        constant_value = float(constant_value_input)
                    except ValueError:
                        self.root.after(0, lambda: messagebox.showerror("Error", "Invalid constant value entered."))
                        self.root.after(0, self.hide_loading_indicator)
                        return  # Exit the method if the input is invalid

                # Select numeric columns
                numeric_columns = self.df.select_dtypes(include=['float64', 'int64']).columns
                for col in numeric_columns:
                    if option == "2":  # Fill with mean
                        mean_value = self.df[col].mean()
                        rounded_mean_value = round(mean_value, 3)
                        self.df[col] = self.df[col].fillna(rounded_mean_value)
                    elif option == "3":  # Fill with median
                        median_value = self.df[col].median()
                        rounded_median_value = round(median_value, 3)
                        self.df[col] = self.df[col].fillna(rounded_median_value)
                    elif option == "4":  # Fill with a constant
                        self.df[col] = self.df[col].fillna(constant_value)

                # Define success message
                if option == "2":
                    success_message = "NaN values have been filled with the column mean."
                elif option == "3":
                    success_message = "NaN values have been filled with the column median."
                elif option == "4":
                    success_message = f"NaN values have been filled with the constant value: {constant_value}"

            # Update the UI in the main thread
            self.root.after(0, lambda: messagebox.showinfo("Success", success_message))
            self.root.after(0, self.display_data)

        except Exception as e:
            error_message = f"An error occurred while handling NaN values: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))

        finally:
            # Hide the loading indicator
            self.root.after(0, self.hide_loading_indicator)

    def create_regression_model(self):
        """Creates a linear regression model using the selected columns."""
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

        # Start the loading indicator
        self.show_loading_indicator("Creating regression model, please wait...")

        # Start a new thread for model creation
        threading.Thread(target=self._create_model_thread).start()

    def _create_model_thread(self):
        """
        Threaded function to create the regression model.
        This ensures that the GUI remains responsive during model creation.
        """
        try:
            X = self.df[[self.selected_input]].values
            y = self.df[self.selected_output].values

            self.model = LinearRegression()
            self.model.fit(X, y)
            predictions = self.model.predict(X)
            mse = mean_squared_error(y, predictions)
            r2 = r2_score(y, predictions)

            intercept = self.model.intercept_
            coef = self.model.coef_[0]
            formula = f"{self.selected_output} = {coef:.2f} * {self.selected_input} + {intercept:.2f}"
            result_text = f"Formula: {formula}\nR²: {r2:.2f}\nMSE: {mse:.2f}"

            # Store data for plotting
            self.X_plot = X
            self.y_plot = y
            self.predictions_plot = predictions

            # Update the GUI in the main thread
            self.root.after(0, lambda: self.update_after_model_creation(result_text))

        except Exception as e:
            # Handle any errors that occur during model creation
            error_message = f"An error occurred while creating the model: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))

        finally:
            # Hide the loading indicator regardless of success or failure
            self.root.after(0, self.hide_loading_indicator)

    def update_after_model_creation(self, result_text):
        """Updates the GUI after model creation in the main thread."""
        # Clear previous graph and plot the new one
        self.clear_graph()
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(self.X_plot, self.y_plot, color="blue", label="Data Points")
        ax.plot(self.X_plot, self.predictions_plot, color="red", label="Regression Line")
        ax.set_xlabel(self.selected_input)
        ax.set_ylabel(self.selected_output)
        ax.legend()
        ax.set_title("Regression Line")

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Inform the user of successful model creation
        messagebox.showinfo("Success", "Regression model created successfully.")

        # Enable the prediction menu item
        self.prediction_menu_button.config(state='normal')

        # Extract values from result_text
        formula = result_text.split('\n')[0].replace('Formula: ', '')
        r2 = result_text.split('\n')[1].replace('R²: ', '')
        mse = result_text.split('\n')[2].replace('MSE: ', '')

        # Update the results table
        self.update_results_table({
            "Formula": formula,
            "R²": r2,
            "MSE": mse,
            "Description": self.model_description or "No description provided",
            "Prediction Result": "-"
        })

    def save_model(self):
        """Saves the linear regression model data to a file."""
        if self.model is None:
            messagebox.showwarning("Warning", "No model has been created to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".joblib",
            filetypes=[
                ("Joblib files", "*.joblib"),
                ("Pickle files", "*.pkl")
            ]
        )
        if not file_path:
            return  # Exit if no file is selected

        try:
            # Prepare the data to save
            model_data = {
                'input_column': self.selected_input,
                'output_column': self.selected_output,
                'model_description': self.model_description or "No description provided",
                'formula': (
                    f"{self.selected_output} = {self.model.coef_[0]:.2f}"
                    f"* {self.selected_input} + {self.model.intercept_:.2f}"
                ),
                'metrics': {
                    'R²': round(
                        r2_score(
                            self.y_plot,
                            self.model.predict(self.X_plot)
                        ),
                        2
                    ),
                    'MSE': round(
                        mean_squared_error(
                            self.y_plot,
                            self.model.predict(self.X_plot)
                        ),
                        2
                    )
                },
                'model': self.model  # Save the actual model
            }

            # Save the model data
            joblib.dump(model_data, file_path)
            messagebox.showinfo(
                "Success",
                f"Model data saved successfully at {file_path}."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred while saving the model: {e}"
            )

    def load_model(self):
        """Load a saved model and update the interface accordingly."""
        while True:
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Joblib files", "*.joblib"),
                    ("Pickle files", "*.pkl")
                ]
            )
            if not file_path:
                break  # Exit if no file is selected

            try:
                # Load the model
                model_data = joblib.load(file_path)

                # Extract model information
                self.selected_input = model_data['input_column']
                self.selected_output = model_data['output_column']
                self.model_description = model_data.get(
                    'model_description',
                    'No description provided'
                )
                formula = model_data['formula']
                r2 = model_data['metrics']['R²']
                mse = model_data['metrics']['MSE']
                self.model = model_data.get('model', None)  # Load the actual model

                if self.model is None:
                    raise ValueError("The model object is missing in the loaded file.")

                # Update the interface to display the model information
                self.update_interface_for_model(formula, r2, mse)

                # Confirmation message
                messagebox.showinfo("Success", "Model loaded successfully.")
                break  # Exit the loop after successful load

            except Exception as e:
                error_message = f"Error while loading the model: {str(e)}"
                retry = messagebox.askretrycancel(
                    "Error",
                    f"{error_message}\n\nMaybe try loading another file?"
                )
                if not retry:
                    break  

    def update_interface_for_model(self, formula, r2, mse):
        """Update the interface to display the loaded model."""
        # Hide unnecessary sections
        self.file_path_label.pack_forget()
        self.table_frame_border.pack_forget()
        self.controls_frame_border.pack_forget()
        self.graph_frame_border.pack_forget()

        # Destroy existing frames if they exist
        if hasattr(self, 'model_details_frame') and self.model_details_frame:
            self.model_details_frame.destroy()
        if hasattr(self, 'prediction_frame') and self.prediction_frame:
            self.prediction_frame.destroy()

        # Create a new frame to display the model details
        self.model_details_frame = tk.Frame(self.root, bg="white", bd=2, relief="groove")
        self.model_details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Adjust the description if empty
        if not self.model_description or self.model_description.strip() == "":
            self.model_description = "No description provided"

        # Display the model details
        model_info = (
            f"Formula: {formula}\n"
            f"R²: {r2}\n"
            f"MSE: {mse}\n\n"
            f"Description: {self.model_description}"
        )
        self.model_info_label = tk.Label(
            self.model_details_frame,
            text=model_info,
            font=("Helvetica", 12),
            fg="black",
            justify="center",
            bg="white"
        )
        self.model_info_label.pack(pady=10, padx=10, expand=True)

        # Create a frame for prediction results
        self.prediction_frame = tk.Frame(self.root, bg="white", bd=2, relief="groove")
        self.prediction_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Label to display prediction result
        self.prediction_result_label_loaded = tk.Label(
            self.prediction_frame,
            text="Prediction Result: (No prediction made yet)",
            font=("Helvetica", 12),
            fg="green",
            justify="center",
            bg="white"
        )
        self.prediction_result_label_loaded.pack(pady=10, padx=10, expand=True)

        # Enable the prediction menu item
        self.prediction_menu_button.config(state='normal')

    def reset_controls(self):
        """Resets the input/output selectors and description field."""
        self.input_selector.set('')
        self.output_selector.set('')
        self.dtext.delete('1.0', tk.END)
        # Reset the results table values to placeholders
        for idx, name in enumerate(self.results_names):
            item_id = self.results_items[idx]
            self.results_table.item(item_id, values=(name, "-"))

    def clear_graph(self):
        """Clears the graph frame."""
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

    def make_prediction_dialog(self):
        """Opens a dialog to input prediction values and displays the result."""
        if self.model is None:
            messagebox.showwarning("Warning", "No model is available for prediction.")
            return

        # Prompt the user to enter the input value
        input_prompt = f"Enter a value for {self.selected_input}:"
        input_value = simpledialog.askstring("Prediction Input", input_prompt)

        if input_value is None:
            # User cancelled the dialog
            return

        try:
            input_value = float(input_value)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input value. Please enter a numeric value.")
            return

        # Perform the prediction
        try:
            X_new = [[input_value]]
            y_pred = self.model.predict(X_new)
            prediction_text = f"Predicted {self.selected_output}: {y_pred[0]:.2f}"

            # Update the results table with prediction result
            if hasattr(self, 'prediction_result_label_loaded'):
                self.prediction_result_label_loaded.config(text=prediction_text)
            else:
                self.update_results_table({
                    "Prediction Result": f"{y_pred[0]:.2f}"
                })

        except Exception as e:
            messagebox.showerror("Prediction Error", f"An error occurred during prediction: {e}")

    def update_results_table(self, updates):
        # Update the results table with new values
        for idx, name in enumerate(self.results_names):
            if name in updates:
                value = updates[name]
                item_id = self.results_items[idx]
                self.results_table.item(item_id, values=(name, value))

if __name__ == "__main__":
    root = tk.Tk()
    app = DataLoaderApp(root)
    root.mainloop()
