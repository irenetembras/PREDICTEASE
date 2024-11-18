import os
import joblib
import pickle

def load_model(file_path):
    """
    Load and print model data from the specified file path.
    Supports .joblib and .pkl formats.
    
    Parameters:
    file_path (str): Path to the model file to load.

    Returns:
    model_data (Any): Loaded model data or None if loading fails.
    """
    if not os.path.isfile(file_path):
        print("Error: The file does not exist at the specified location.")
        return None

    print(f"Loading model from {file_path}...")

    try:
        # Check file extension and load model accordingly
        if file_path.endswith('.joblib'):
            model_data = joblib.load(file_path)
        elif file_path.endswith('.pkl'):
            with open(file_path, 'rb') as file:
                model_data = pickle.load(file)
        else:
            print("Unsupported file format. Please use .pkl or .joblib.")
            return None

        print("Model loaded successfully!")
        print(model_data)  # Display loaded model data for verification
        return model_data

    except Exception as e:
        print(f"An error occurred while loading the model: {e}")
        return None

# Specify the file paths for models in .pkl and .joblib formats
file_path_pkl = r"C:\Users\nawfa\OneDrive\Bureau\practica es\ok.pkl"
file_path_joblib = r"C:\Users\nawfa\OneDrive\Bureau\practica es\ppp.joblib"

# Load and display model data from the specified file paths
load_model(file_path_pkl)
load_model(file_path_joblib)
