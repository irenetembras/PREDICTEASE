from sklearn.linear_model import LinearRegression
import numpy as np
import pickle
import joblib

# 1. Create sample data and train a linear regression model
X = np.array([[1], [2], [3], [4], [5]])  # Feature
y = np.array([2, 4, 6, 8, 10])           # Target

model = LinearRegression().fit(X, y)  # Train the model

# 2. Save and load the model using Pickle
# Save the model with Pickle
with open('model_pickle.pkl', 'wb') as file:
    pickle.dump(model, file)

# Load the model with Pickle
with open('model_pickle.pkl', 'rb') as file:
    loaded_model_pickle = pickle.load(file)

# Prediction test with the model loaded using Pickle
print("Prediction using model loaded with Pickle:", loaded_model_pickle.predict([[6]]))


# 3. Save and load the model using Joblib
# Save the model with Joblib
joblib.dump(model, 'model_joblib.pkl')

# Load the model with Joblib
loaded_model_joblib = joblib.load('model_joblib.pkl')

# Prediction test with the model loaded using Joblib
print("Prediction using model loaded with Joblib:", loaded_model_joblib.predict([[6]]))
