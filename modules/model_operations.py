import tkinter as tk
from tkinter import filedialog, messagebox

import joblib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


def create_regression_model(self):
    """Creates a linear regression model using the selected columns."""
    if self.df is None:
        messagebox.showwarning("Warning", "No dataset loaded.")
        return

    self.selected_input = self.input_selector.get()
    self.selected_output = self.output_selector.get()

    if not self.selected_input or not self.selected_output:
        messagebox.showwarning(
            "Warning", "No columns selected for regression."
        )
        return

    self.model_description = self.dtext.get("1.0", "end-1c").strip()
    if not self.model_description:
        proceed = messagebox.askyesno(
            "Missing Description",
            "No model description provided. Do you want to continue?"
        )
        if not proceed:
            return

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
        formula = (
            f"{self.selected_output} = {coef:.2f} * {self.selected_input}"
            f" + {intercept:.2f}"
        )
        self.result_label.config(
            text=f"Formula: {formula}\nR²: {r2:.2f}\nMSE: {mse:.2f}"
        )

        # Clear previous graph to avoid overlap with new one.
        self.clear_graph()

        # Create and display the regression line plot.
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(X, y, color="blue", label="Data Points")
        ax.plot(X, predictions, color="red", label="Regression Line")
        ax.set_xlabel(self.selected_input)
        ax.set_ylabel(self.selected_output)
        ax.legend()
        ax.set_title("Regression Line")

        # Embed the plot in the Tkinter window.
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"An error occurred while creating the model: {e}"
        )


def save_model(self):
    """Saves the linear regression model data to a file."""
    if self.model is None:
        messagebox.showwarning(
            "Warning",
            "No model has been created to save."
        )
        return

    # Prompt user to select a file path to save the model.
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pkl",
        filetypes=[
            ("Pickle files", "*.pkl"),
            ("Joblib files", "*.joblib")
        ]
    )
    if not file_path:
        return  # Exit if no file is selected.

    try:
        # Prepare model data for saving.
        model_data = {
            'input_column': self.selected_input,
            'output_column': self.selected_output,
            'model_description': self.model_description,
            'formula': (
                f"{self.selected_output} = {self.model.coef_[0]:.2f}"
                f" * {self.selected_input} + {self.model.intercept_:.2f}"
            ),
            'metrics': {
                'R²': round(
                    r2_score(
                        self.df[self.selected_output],
                        self.model.predict(self.df[[self.selected_input]])
                    ),
                    2
                ),
                'MSE': round(
                    mean_squared_error(
                        self.df[self.selected_output],
                        self.model.predict(self.df[[self.selected_input]])
                    ),
                    2
                )
            }
        }

        # Save model data to the selected file path.
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
        # Prompt user to select a file to load.
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Pickle files", "*.pkl"),
                ("Joblib files", "*.joblib")
            ]
        )
        if not file_path:
            break  # Exit if no file is selected.

        try:
            # Load the model from the selected file.
            model_data = joblib.load(file_path)

            # Extract and update model information.
            self.selected_input = model_data['input_column']
            self.selected_output = model_data['output_column']
            self.model_description = model_data.get(
                'model_description',
                'No description provided'
            )
            formula = model_data['formula']
            r2 = model_data['metrics']['R²']
            mse = model_data['metrics']['MSE']

            # Update the interface to display the model information.
            self.update_interface_for_model(formula, r2, mse)

            # Reset the controls to default.
            self.reset_controls()

            # Confirmation message after successfully loading the model.
            messagebox.showinfo("Success", "Model loaded successfully.")
            break  # Exit the loop after successful load.

        except Exception as e:
            error_message = f"Error while loading the model: {str(e)}"
            retry = messagebox.askretrycancel(
                "Error",
                f"{error_message}\n\nMaybe try loading another file?"
            )
            if not retry:
                break
