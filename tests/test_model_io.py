# tests/test_model_io.py

import unittest
import os
from src.models.model_io import save_model_data, load_model_data
from src.models.regression import LinearRegressionModel
import numpy as np


class TestModelIO(unittest.TestCase):

    def setUp(self):
        # Create a sample model
        self.model = LinearRegressionModel()
        self.X = np.array([[1], [2], [3]])
        self.y = np.array([2, 4, 6])
        self.model.fit(self.X, self.y)

        self.model_data = {
            'input_column': 'X',
            'output_column': 'y',
            'model_description': 'Test model',
            'formula': self.model.get_formula('X', 'y'),
            'metrics': {
                'R²': self.model.r2_score(self.y, self.model.predict(self.X)),
                'MSE': self.model.mean_squared_error(self.y, self.model.predict(self.X))
            },
            'model': self.model
        }
        self.file_path = "test_model.joblib"

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_save_model_data(self):
        save_model_data(self.model_data, self.file_path)
        self.assertTrue(os.path.exists(self.file_path))

    def test_load_model_data(self):
        save_model_data(self.model_data, self.file_path)
        loaded_model_data = load_model_data(self.file_path)
        self.assertEqual(loaded_model_data['input_column'], self.model_data['input_column'])
        self.assertEqual(loaded_model_data['output_column'], self.model_data['output_column'])
        self.assertEqual(loaded_model_data['model_description'], self.model_data['model_description'])
        self.assertEqual(loaded_model_data['formula'], self.model_data['formula'])
        self.assertAlmostEqual(loaded_model_data['metrics']['R²'], self.model_data['metrics']['R²'], places=5)
        self.assertAlmostEqual(loaded_model_data['metrics']['MSE'], self.model_data['metrics']['MSE'], places=5)
        # Test the loaded model's prediction
        loaded_model = loaded_model_data['model']
        predictions = loaded_model.predict(self.X)
        np.testing.assert_array_almost_equal(predictions, self.y)

    def test_predict_with_loaded_model(self):
        save_model_data(self.model_data, self.file_path)
        loaded_model_data = load_model_data(self.file_path)
        loaded_model = loaded_model_data['model']
        X_new = np.array([[4], [5]])
        y_expected = np.array([8, 10])
        y_pred = loaded_model.predict(X_new)
        np.testing.assert_array_almost_equal(y_pred, y_expected)


if __name__ == '__main__':
    unittest.main()
