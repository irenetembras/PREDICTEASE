import os
import joblib
import pickle


def load_model(file_path):
    """
    Load and print model data from the specified file path.

    This function supports files in .joblib and .pkl formats. It checks
    the file's existence and handles errors during the loading process.

    Parameters:
        file_path (str): Path to the model file to load.

    Returns:
        Any: Loaded model data if successful, or None if the loading fails.
    """

    # Check if the file exists before proceeding
    if not os.path.isfile(file_path):
        print("Error: The file does not exist at the specified location.")
        return None

    print(f"Loading model from {file_path}...")

    try:
        # Load the model data using the appropriate library.

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

    except (joblib.exceptions.MemoryError, pickle.UnpicklingError) as e:
        # Handle specific errors for joblib and pickle formats
        print(f"Error loading model: {e}")
        return None

    except Exception as e:
        # Catch any other general errors
        print(f"An unexpected error occurred: {e}")
        return None


# Define the file paths for testing models saved in .pkl and .joblib formats.
pkl_file_path = r"C:\Users\nawfa\OneDrive\Bureau\practica es\ok.pkl"
joblib_file_path = r"C:\Users\nawfa\OneDrive\Bureau\practica es\ppp.joblib"

# Attempt to load and display the contents of the model files.
load_model(pkl_file_path)
load_model(joblib_file_path)
