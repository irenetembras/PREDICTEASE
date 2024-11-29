# src/models/model_io.py

import joblib


def save_model_data(model_data, file_path):
    """
    Saves the model data to a file.

    Parameters:
    - model_data (dict): The model data to save.
    - file_path (str): The file path where to save the model data.
    """
    joblib.dump(model_data, file_path)


def load_model_data(file_path):
    """
    Loads the model data from a file.

    Parameters:
    - file_path (str): The file path from where to load the model data.

    Returns:
    - dict: The loaded model data.
    """
    model_data = joblib.load(file_path)
    return model_data
