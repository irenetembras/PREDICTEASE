# src/models/regression.py

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


class LinearRegressionModel:
    """
    A wrapper class for sklearn's LinearRegression to encapsulate model training and evaluation.
    """

    def __init__(self):
        self.model = LinearRegression()
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X, y):
        """
        Fits the linear regression model.

        Parameters:
        - X (array-like): Feature matrix.
        - y (array-like): Target vector.
        """
        self.model.fit(X, y)
        self.coef_ = self.model.coef_[0]
        self.intercept_ = self.model.intercept_

    def predict(self, X):
        """
        Predicts target values using the trained model.

        Parameters:
        - X (array-like): Feature matrix.

        Returns:
        - array-like: Predicted target values.
        """
        return self.model.predict(X)

    def mean_squared_error(self, y_true, y_pred):
        """
        Calculates the Mean Squared Error.

        Parameters:
        - y_true (array-like): True target values.
        - y_pred (array-like): Predicted target values.

        Returns:
        - float: Mean Squared Error.
        """
        return mean_squared_error(y_true, y_pred)

    def r2_score(self, y_true, y_pred):
        """
        Calculates the R² score.

        Parameters:
        - y_true (array-like): True target values.
        - y_pred (array-like): Predicted target values.

        Returns:
        - float: R² score.
        """
        return r2_score(y_true, y_pred)

    def get_formula(self, input_var, output_var):
        """
        Generates the formula of the linear regression model.

        Parameters:
        - input_var (str): Name of the input variable.
        - output_var (str): Name of the output variable.

        Returns:
        - str: The formula as a string.
        """
        formula = f"{output_var} = {self.coef_:.2f} * {input_var} + {self.intercept_:.2f}"
        return formula
