# src/data/data_handler.py

import pandas as pd
from tkinter import messagebox, simpledialog


def handle_nan_values(df, option):
    """
    Handles NaN values in the DataFrame based on the selected option.

    Parameters:
    - df (pd.DataFrame): The DataFrame to process.
    - option (str): The option selected for handling NaN values ("1" to "4").

    Returns:
    - pd.DataFrame: The processed DataFrame.
    - str: A success message to display to the user.
    """
    try:
        if option == "1":
            # Remove rows with NaN values
            df = df.dropna()
            success_message = "Rows with NaN values have been removed."
        else:
            if option == "4":  # Fill with a constant
                constant_value_input = simpledialog.askstring(
                    "Input",
                    "Enter a constant value:"
                )
                if constant_value_input is None:
                    return None, "Operation cancelled by user."
                try:
                    constant_value = float(constant_value_input)
                except ValueError:
                    return None, "Invalid constant value entered."

            # Select numeric columns
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_columns:
                if option == "2":  # Fill with mean
                    mean_value = df[col].mean()
                    df[col] = df[col].fillna(mean_value)
                elif option == "3":  # Fill with median
                    median_value = df[col].median()
                    df[col] = df[col].fillna(median_value)
                elif option == "4":  # Fill with a constant
                    df[col] = df[col].fillna(constant_value)

            # Define success message
            if option == "2":
                success_message = "NaN values have been filled with the column mean."
            elif option == "3":
                success_message = "NaN values have been filled with the column median."
            elif option == "4":
                success_message = f"NaN values have been filled with the constant value: {constant_value}"

        return df, success_message

    except Exception as e:
        error_message = f"An error occurred while handling NaN values: {str(e)}"
        messagebox.showerror("Error", error_message)
        return None, error_message
