from datetime import datetime
import json
from pathlib import Path
import unittest
from unittest.mock import mock_open, patch

import pandas as pd

from utils.financial import _parse_date, get_transaction_rubles, load_financial_transactions

# Глобальные тестовые данные (вне класса)
JSON_DATA = [
    {
        "id": 1,
        "state": "EXECUTED",
        "date": "2023-01-01T12:00:00.123456",
        "operationAmount": {"amount": "100.50", "currency": {"code": "RUB"}},
    }
]

DF_DATA = pd.DataFrame(
    [
        {
            "id": 2,
            "state": "FAILED",
            "date": "2023-01-02",
            "operationAmount": {"amount": "200", "currency": {"code": "USD"}},
        }
    ]
)


class TestLoadFinancialTransactions(unittest.TestCase):

    def setUp(self):
        """Подготовка путей к тестовым файлам."""
        self.json_path = Path("tests/data/test.json")
        self.csv_path = Path("tests/data/test.csv")
        self.xlsx_path = Path("tests/data/test.xlsx")

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps(JSON_DATA))
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_json_success(self, mock_exists, mock_file):
        """Тест загрузки корректного JSON-файла."""
        result = load_financial_transactions(self.json_path)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        self.assertIsInstance(result[0]["date"], datetime)
        self.assertEqual(result[0]["amount"], 100.5)
        self.assertEqual(result[0]["currency_code"], "RUB")

    @patch("pathlib.Path.exists", return_value=False)
    def test_load_json_file_not_found(self, mock_exists):
        """Тест: JSON-файл не найден."""
        result = load_financial_transactions(self.json_path)
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_json_empty_file(self, mock_file, mock_exists):
        """Тест: пустой JSON-файл."""
        result = load_financial_transactions(self.json_path)
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open, read_data="{invalid json}")
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_json_invalid_format(self, mock_file, mock_exists):
        """Тест: некорректный JSON."""
        result = load_financial_transactions(self.json_path)
        self.assertEqual(result, [])

    @patch("pandas.read_csv", return_value=DF_DATA)
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_csv_success(self, mock_read, mock_exists):  # Порядок аргументов важен!
        """Тест загрузки CSV-файла."""
        result = load_financial_transactions(self.csv_path)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 2)
        self.assertEqual(result[0]["state"], "FAILED")

    @patch("pandas.read_excel", return_value=DF_DATA)
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_xlsx_success(self, mock_read, mock_exists):  # Порядок аргументов важен!
        """Тест загрузки XLSX-файла."""
        result = load_financial_transactions(self.xlsx_path)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 2)

    @patch("pathlib.Path.exists", return_value=True)
    def test_unsupported_file_format(self, mock_exists):
        """Тест: неподдерживаемый формат файла."""
        result = load_financial_transactions("tests/data/test.txt")
        self.assertEqual(result, [])

    def test_parse_date_valid(self):
        """Тест корректного преобразования даты."""
        date_str = "2023-01-01T12:00:00.123456"
        result = _parse_date(date_str)
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2023)

    def test_parse_date_invalid(self):
        """Тест некорректной даты."""
        result = _parse_date("invalid-date")
        self.assertIsNone(result)

    @patch("external_api.currency_converter.convert_transaction_to_rubles", return_value=7500.0)
    def test_get_transaction_rubles_success(self, mock_convert):
        """Тест конвертации суммы в рубли."""
        transaction = {"amount": 100, "currency_code": "USD"}
        result = get_transaction_rubles(transaction)
        self.assertEqual(result, 7500.0)

    def test_get_transaction_rubles_missing_amount(self):
        """Тест: отсутствует поле 'amount'."""
        transaction = {"currency_code": "USD"}
        result = get_transaction_rubles(transaction)
        self.assertIsNone(result)

    def test_get_transaction_rubles_missing_currency(self):
        """Тест: отсутствует поле 'currency_code'."""
        transaction = {"amount": 100}
        result = get_transaction_rubles(transaction)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
