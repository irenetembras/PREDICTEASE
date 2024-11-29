# tests/test_regression.py

import unittest
import numpy as np
from src.models.regression import LinearRegressionModel


class TestRegressionModel(unittest.TestCase):

    def setUp(self):
        # Simple linear relationship
        self.X = np.array([[1], [2], [3], [4], [5]])
        self.y = np.array([2, 4, 6, 8, 10])  # y = 2x
        self.model = LinearRegressionModel()
        self.model.fit(self.X, self.y)

    def test_fit(self):
        self.assertAlmostEqual(self.model.coef_, 2.0, places=5)
        self.assertAlmostEqual(self.model.intercept_, 0.0, places=5)

    def test_predict(self):
        predictions = self.model.predict(self.X)
        np.testing.assert_array_almost_equal(predictions, self.y)

    def test_mean_squared_error(self):
        predictions = self.model.predict(self.X)
        mse = self.model.mean_squared_error(self.y, predictions)
        self.assertAlmostEqual(mse, 0.0, places=5)

    def test_r2_score(self):
        predictions = self.model.predict(self.X)
        r2 = self.model.r2_score(self.y, predictions)
        self.assertAlmostEqual(r2, 1.0, places=5)

    def test_get_formula(self):
        formula = self.model.get_formula("X", "y")
        self.assertEqual(formula, "y = 2.00 * X + 0.00")

    def test_prediction_with_new_data(self):
        # Test prediction with new input
        X_new = np.array([[6], [7]])
        y_expected = np.array([12, 14])
        y_pred = self.model.predict(X_new)
        np.testing.assert_array_almost_equal(y_pred, y_expected)


if __name__ == '__main__':
    unittest.main()
