# tests/test_data_handler.py

import unittest
import pandas as pd
from src.data.data_handler import handle_nan_values


class TestDataHandler(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            'A': [1, 2, None, 4],
            'B': [None, 2, 3, 4],
            'C': ['x', 'y', 'z', None]
        })

    def test_remove_rows_with_nan(self):
        df_processed, message = handle_nan_values(self.df.copy(), "1")
        expected_df = self.df.dropna()
        pd.testing.assert_frame_equal(df_processed, expected_df)

    def test_fill_with_mean(self):
        df_processed, message = handle_nan_values(self.df.copy(), "2")
        mean_A = self.df['A'].mean()
        mean_B = self.df['B'].mean()
        expected_df = self.df.copy()
        expected_df['A'] = expected_df['A'].fillna(mean_A)
        expected_df['B'] = expected_df['B'].fillna(mean_B)
        pd.testing.assert_frame_equal(df_processed, expected_df)

    def test_fill_with_median(self):
        df_processed, message = handle_nan_values(self.df.copy(), "3")
        median_A = self.df['A'].median()
        median_B = self.df['B'].median()
        expected_df = self.df.copy()
        expected_df['A'] = expected_df['A'].fillna(median_A)
        expected_df['B'] = expected_df['B'].fillna(median_B)
        pd.testing.assert_frame_equal(df_processed, expected_df)

    def test_fill_with_constant(self):
        # Mock the simpledialog to return a constant value
        from unittest.mock import patch
        with patch('src.data.data_handler.simpledialog.askstring', return_value='10'):
            df_processed, message = handle_nan_values(self.df.copy(), "4")
        expected_df = self.df.copy()
        expected_df['A'] = expected_df['A'].fillna(10)
        expected_df['B'] = expected_df['B'].fillna(10)
        pd.testing.assert_frame_equal(df_processed, expected_df)


if __name__ == '__main__':
    unittest.main()
