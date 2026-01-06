from decimal import ROUND_HALF_UP, Decimal
import os
from typing import Optional

from dotenv import load_dotenv
import requests

load_dotenv()


class CurrencyConverter:
    api_key: Optional[str]
    base_url: Optional[str]

    def __init__(self) -> None:
        self.api_key = os.getenv("EXCHANGE_API_KEY")
        self.base_url = os.getenv("EXCHANGE_API_URL")

        if not self.api_key:
            raise ValueError("EXCHANGE_API_KEY не задан в .env")
        if not self.base_url:
            raise ValueError("EXCHANGE_API_URL не задан в .env")

        # mypy пока не сужает тип, но мы проверим в методе
        self.api_key = self.api_key
        self.base_url = self.base_url

    def get_exchange_rate(self, currency: str) -> Optional[Decimal]:
        """Получает курс валюты к RUB через apilayer.com."""
        assert self.base_url is not None  # ← Ключевая строка для mypy

        try:
            headers = {"apikey": self.api_key}
            params = {"base": currency, "symbols": "RUB"}
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return Decimal(str(data["rates"]["RUB"]))
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"Ошибка получения курса: {e}")
            return None

    def convert_to_rubles(self, amount: float, currency: str) -> Optional[float]:
        """Конвертирует сумму в рубли."""
        if currency == "RUB":
            return amount

        if currency not in ["USD", "EUR"]:
            raise ValueError(f"Неподдерживаемая валюта: {currency}")

        rate = self.get_exchange_rate(currency)
        if rate is None:
            return None

        rubles = Decimal(str(amount)) * rate
        rubles = rubles.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(rubles)
