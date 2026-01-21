import unittest
from unittest.mock import patch

import pandas as pd

from src.data_loader import load_from_csv, load_from_excel


class TestDataLoader(unittest.TestCase):

    @patch("pandas.read_csv")
    def test_load_from_csv_success(self, mock_read_csv):
        # Подготавливаем тестовые данные
        mock_df = pd.DataFrame(
            [{"id": 1, "amount": 100.0, "currency": "RUB"}, {"id": 2, "amount": 200.0, "currency": "USD"}]
        )
        mock_read_csv.return_value = mock_df

        # Вызываем функцию
        result = load_from_csv("dummy.csv")

        # Проверяем результат
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["amount"], 100.0)
        self.assertEqual(result[1]["currency"], "USD")

    @patch("pandas.read_csv", side_effect=Exception("File not found"))
    def test_load_from_csv_failure(self, mock_read_csv):
        result = load_from_csv("nonexistent.csv")
        self.assertEqual(result, [])  # При ошибке возвращается пустой список

    @patch("pandas.read_excel")
    def test_load_from_excel_success(self, mock_read_excel):
        mock_df = pd.DataFrame(
            [{"id": 3, "amount": 300.0, "currency": "EUR"}, {"id": 4, "amount": 400.0, "currency": "GBP"}]
        )
        mock_read_excel.return_value = mock_df

        result = load_from_excel("dummy.xlsx")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["currency"], "EUR")

    @patch("pandas.read_excel", side_effect=Exception("Invalid Excel format"))
    def test_load_from_excel_failure(self, mock_read_excel):
        result = load_from_excel("invalid.xlsx")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
