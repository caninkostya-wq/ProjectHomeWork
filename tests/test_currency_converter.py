import unittest
from unittest.mock import Mock, patch

import requests

from external_api.currency_converter import convert_transaction_to_rubles


class TestConvertTransactionToRubles(unittest.TestCase):

    @patch("requests.get")
    def test_usd_to_rub_success(self, mock_get):
        # Настраиваем mock для успешного ответа API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"rates": {"RUB": "75.50"}})
        mock_get.return_value = mock_response

        # Транзакция в USD
        transaction = {"amount": 100.0, "currency": {"code": "USD"}}

        result = convert_transaction_to_rubles(transaction)
        self.assertEqual(result, 7550.0)  # 100 * 75.50

    @patch("requests.get")
    def test_eur_to_rub_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"rates": {"RUB": "85.20"}})
        mock_get.return_value = mock_response

        transaction = {"amount": 50.0, "currency": {"code": "EUR"}}

        result = convert_transaction_to_rubles(transaction)
        self.assertEqual(result, 4260.0)  # 50 * 85.20

    def test_rub_to_rub(self):
        # Валюта уже RUB — конвертация не нужна
        transaction = {"amount": 3000.0, "currency": {"code": "RUB"}}

        result = convert_transaction_to_rubles(transaction)
        self.assertEqual(result, 3000.0)

    @patch("requests.get")
    def test_api_request_failure(self, mock_get):
        # Имитируем ошибку сети
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        transaction = {"amount": 100.0, "currency": {"code": "USD"}}

        with self.assertRaises(RuntimeError) as context:
            convert_transaction_to_rubles(transaction)

        self.assertIn("Ошибка при получении курса", str(context.exception))

    def test_invalid_transaction_missing_amount(self):
        # Нет поля "amount"
        transaction = {"currency": {"code": "USD"}}

        with self.assertRaises(ValueError) as context:
            convert_transaction_to_rubles(transaction)

        self.assertIn("Некорректный формат транзакции", str(context.exception))

    def test_invalid_transaction_missing_currency(self):
        # Нет поля "currency"
        transaction = {"amount": 100.0}

        with self.assertRaises(ValueError) as context:
            convert_transaction_to_rubles(transaction)

        self.assertIn("Некорректный формат транзакции", str(context.exception))

    def test_unsupported_currency(self):
        # Валюта не USD/EUR/RUB
        transaction = {"amount": 100.0, "currency": {"code": "GBP"}}

        with self.assertRaises(ValueError) as context:
            convert_transaction_to_rubles(transaction)

        self.assertEqual(str(context.exception), "Неподдерживаемая валюта: GBP")

    @patch("requests.get")
    def test_api_returns_invalid_json(self, mock_get):
        # API вернул невалидный JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(side_effect=ValueError("Invalid JSON"))
        mock_get.return_value = mock_response

        transaction = {"amount": 100.0, "currency": {"code": "USD"}}

        with self.assertRaises(RuntimeError) as context:
            convert_transaction_to_rubles(transaction)

        self.assertIn("Ошибка при получении курса", str(context.exception))


if __name__ == "__main__":
    unittest.main()
