### Functional Testing Plan for Release

#### Overview:

The functional testing plan was executed successfully to ensure that all project functionalities work correctly and without significant errors. Below is a summary of the process and results.

---

### Key Functionalities Tested:

1. *Data Loading*:

   - *Actions Performed*:
     1. Open the application and navigate to the "Load Data" section.
     2. Select a file for loading (CSV, Excel, or SQLite).
     3. Attempt to load corrupted.csv to simulate handling of corrupted files.
     4. Attempt to load empty.xlsx to test handling of empty files.
   - *Expected Results*:
     - The system should successfully load valid files and display: "File loaded successfully."
     - The system should identify missing values and display them to the user.
     - For corrupted.csv, the system should display the error message: "Invalid or corrupted file."
     - For empty.xlsx, the system should handle the file gracefully and notify the user of its empty content with the same message as the corrupted file.

2. *Column Selection*:

   - *Actions Performed*:

     1. Navigate to the "Column Selection" section.
     2. Select input columns from the loaded data.
     3. Choose an output column for prediction.
     4. Select a column with non-numeric values or NaN values.

   - *Expected Results*:

     - The system should allow valid selections and highlight the chosen columns clearly.
     - The system displays an error message: "An error occurred while creating the model."

3. *Data Preprocessing*:

   - *Actions Performed*:
     1. Navigate to the "Data" section.
     2. Identify and handle missing values in the dataset.
     3. Apply mean, median, or constant replacements for missing values or remove the rows with NaN values.
   - *Expected Results*:
     - Selected preprocessing methods (mean/median/constant) should be applied accurately, with updated data visible.

4. *Regression Model Creation*:

   - *Actions Performed*:
     1. Click on the "Create Model" button.
     2. Add a description if desired.
     3. Create a linear regression model using the preprocessed data.
     4. Visualize the model's graph and metrics (R², MSE).
   - *Expected Results*:
     - If the description is not provided, the system should notify the user.
     - The system should generate a regression model without errors.
     - The graph and metrics should match the input data accurately.

5. *Predictions*:

   - *Actions Performed*:
     1. Load a new model or create one.
     2. Click on the prediction button.
     3. Add a value for prediction.
   - *Expected Results*:
     - The system should generate predictions accurately for valid inputs.
     - For invalid inputs, the system should display clear error messages.

6. *Model Persistence*:

   - *Actions Performed*:
     1. Click the "Save Model" button.
     2. Save the created model to disk.
     3. Click the "Load Model" button.
     4. Load the saved model and use it for predictions.
   - *Expected Results*:
     - Models should be saved and loaded without data loss or corruption.
     - Predictions using the loaded model should match those from the original.
     - If the model is corrupted, the system should display an error message.

---

### Final Notes:

The functional testing process ensured that the system is stable, reliable, and ready for release. All stakeholders have reviewed and approved the test report, confirming the project is ready for deployment.