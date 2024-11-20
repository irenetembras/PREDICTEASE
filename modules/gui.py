import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from modules.data_operations import *
from modules.model_operations import *
from modules.modulo_importacion import import_file

class DataLoaderApp:
    """
    Application to load and visualize data, manage NaNs, and create a
    linear regression model with error metrics.
    """
    from modules.model_operations import create_regression_model, save_model
    from modules.data_operations import process_import, display_data, handle_nan
    from modules.main_window import reset_controls, clear_graph, get_decimal_places, update_interface_for_model, populate_selectors

    def __init__(self, root):
        root.state('zoomed')
        self.root = root
        self.root.title("Data Loader")
        self.root.configure(bg="white")
        self.font_style = ("Helvetica", 10)

        # Create the toolbar
        self.toolbar = tk.Frame(root, bg="#e0e0e0", height=40)
        self.toolbar.pack(side="top", fill="x")

        # File menu button
        self.file_menu_button = tk.Menubutton(
            self.toolbar,
            text="File",
            font=self.font_style,
            bg="#e0e0e0",
            fg="black",
            bd=0,
            padx=20,
            pady=5
        )
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0)
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
            bg="#e0e0e0",
            fg="black",
            bd=0,
            padx=20,
            pady=5
        )
        self.data_menu = tk.Menu(self.data_menu_button, tearoff=0)
        self.data_menu.add_command(
            label="Remove rows with NaN",
            command=lambda: self.handle_nan(option="1")
        )
        self.data_menu.add_command(
            label="Fill with Mean",
            command=lambda: self.handle_nan(option="2")
        )
        self.data_menu.add_command(
            label="Fill with Median",
            command=lambda: self.handle_nan(option="3")
        )
        self.data_menu.add_command(
            label="Fill with Constant",
            command=lambda: self.handle_nan(option="4")
        )
        self.data_menu_button.config(menu=self.data_menu)
        self.data_menu_button.pack(side="left", padx=2)

        # Label to display the selected file path
        self.file_path_label = tk.Label(
            root,
            text="No file selected",
            font=self.font_style,
            bg="white",
            fg="black"
        )
        self.file_path_label.pack(pady=10)

        # Frame for the data table
        self.table_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.table_frame_border.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.table_frame = tk.Frame(
            self.table_frame_border, bg="#f9f9f9"
        )
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for regression controls
        self.controls_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.controls_frame_border.pack(
            side="left", fill="y", padx=10, pady=5
        )
        self.controls_frame = tk.Frame(
            self.controls_frame_border, bg="#f9f9f9"
        )
        self.controls_frame.pack(fill="both", padx=5, pady=5)

        # Content of the regression control section
        input_label = tk.Label(
            self.controls_frame,
            text="Select input column:",
            font=self.font_style,
            bg="#f9f9f9"
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
            bg="#f9f9f9"
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
            bg="#f9f9f9"
        )
        description_label.pack(anchor="w", padx=10, pady=5)
        self.dtext = tk.Text(
            self.controls_frame, height=4, width=30
        )
        self.dtext.pack(padx=10, pady=5)

        create_button = tk.Button(
            self.controls_frame,
            text="Create Model",
            command=self.create_regression_model,
            font=self.font_style
        )
        create_button.pack(pady=10)

        save_button = tk.Button(
            self.controls_frame,
            text="Save Model",
            command=self.save_model,
            font=self.font_style
        )
        save_button.pack(pady=5)

        # Section to display results
        self.result_label = tk.Label(
            self.controls_frame,
            text="",
            font=self.font_style,
            fg="blue",
            justify="left",
            bg="#f9f9f9"
        )
        self.result_label.pack(pady=10)

        # Frame for the graph
        self.graph_frame_border = tk.Frame(self.root, bg="#cccccc")
        self.graph_frame_border.pack(
            side="right",
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )
        self.graph_frame = tk.Frame(self.graph_frame_border, bg="#f9f9f9")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Initialization of variables
        self.df = None
        self.selected_input = None
        self.selected_output = None
        self.model_description = ""
        self.model = None

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
            if hasattr(self, 'model_details') and self.model_details:
                self.model_details.destroy()

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

    def load_model(self):
        """Method to load a model using the load_model function."""
        file_path = filedialog.askopenfilename(filetypes=[("Model Files", "*.model")])
        if file_path:
            # Call the load_model function (defined in model_operations)
            model = load_model(file_path)  # Call the function from the model_operations module
            if model:
                messagebox.showinfo("Model Loaded", "Model loaded successfully!")
            else:
                messagebox.showerror("Error", "Failed to load the model.")
