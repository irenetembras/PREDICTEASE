import joblib
import os
import pickle

def load_model(file_path):
    """Loads the model data from the specified file path and prints the entire contents."""
    if os.path.isfile(file_path):
        print(f"Loading the model from {file_path}...")
        
        try:
            # Check the file extension and load the model accordingly
            if file_path.endswith('.joblib'):
                model_data = joblib.load(file_path)
            elif file_path.endswith('.pkl'):
                with open(file_path, 'rb') as file:
                    model_data = pickle.load(file)
            else:
                print("Unsupported file format. Please use .pkl or .joblib")
                return None
            
            # Print the entire contents of the model
            print("Model loaded successfully!")
            print(model_data)  # Display the whole model data
            return model_data  # Return the loaded model data
        except Exception as e:
            print(f"An error occurred while loading the model: {e}")
    else:
        print("The file does not exist at the specified location.")

# Specify the file paths
file_path_pkl = r"C:\Users\nawfa\OneDrive\Bureau\practica es\ok.pkl"
file_path_joblib = r"C:\Users\nawfa\OneDrive\Bureau\practica es\ppp.joblib"

# Load and display the model data
load_model(file_path_pkl)
load_model(file_path_joblib)
