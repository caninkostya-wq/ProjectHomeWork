from decimal import Decimal
import unittest
from unittest.mock import Mock, patch

import requests

from external_api.currency_converter import CurrencyConverter


class TestCurrencyConverter(unittest.TestCase):

    @patch("requests.get")
    def test_get_exchange_rate_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"rates": {"RUB": "75.50"}})
        mock_get.return_value = mock_response

        converter = CurrencyConverter()
        rate = converter.get_exchange_rate("USD")
        self.assertEqual(rate, Decimal("75.50"))

    @patch("requests.get")
    def test_convert_to_rubles_usd(self, mock_get):
        mock_get.return_value.json = Mock(return_value={"rates": {"RUB": "75.50"}})

        converter = CurrencyConverter()
        result = converter.convert_to_rubles(100.0, "USD")
        self.assertEqual(result, 7550.00)

    def test_convert_to_rubles_rub(self):
        converter = CurrencyConverter()
        result = converter.convert_to_rubles(5000.0, "RUB")
        self.assertEqual(result, 5000.0)

    @patch("requests.get")
    def test_convert_to_rubles_api_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        converter = CurrencyConverter()
        result = converter.convert_to_rubles(100.0, "EUR")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
