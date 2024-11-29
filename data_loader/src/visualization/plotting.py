# src/visualization/plotting.py

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def plot_regression_line(X, y, predictions, input_var, output_var, parent_frame):
    """
    Plots the regression line and data points.

    Parameters:
    - X (array-like): Feature matrix.
    - y (array-like): True target values.
    - predictions (array-like): Predicted target values.
    - input_var (str): Name of the input variable.
    - output_var (str): Name of the output variable.
    - parent_frame (tk.Frame): The parent frame to place the plot in.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(X, y, color="blue", label="Data Points")
    ax.plot(X, predictions, color="red", label="Regression Line")
    ax.set_xlabel(input_var)
    ax.set_ylabel(output_var)
    ax.legend()
    ax.set_title("Regression Line")

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
