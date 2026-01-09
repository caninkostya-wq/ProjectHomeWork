from decimal import ROUND_HALF_UP, Decimal
import os
from typing import Any

from dotenv import load_dotenv
import requests

load_dotenv()


def convert_transaction_to_rubles(transaction: dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction: Словарь с полями:
            - "amount": число (сумма)
            - "currency": словарь с полем "code" (код валюты)

    Returns:
        Сумма в рублях как float.
    Raises:
        ValueError: Если валюта не поддерживается или данные некорректны.
        RuntimeError: Если ошибка при запросе к API.
    """
    # 1. Извлекаем данные из словаря
    try:
        amount = transaction["amount"]
        currency_code = transaction["currency"]["code"]
    except KeyError as e:
        raise ValueError(f"Некорректный формат транзакции: отсутствует поле {e}")

    # 2. Если валюта уже RUB — возвращаем сумму как float
    if currency_code == "RUB":
        return float(amount)

    # 3. Проверяем поддерживаемые валюты
    if currency_code not in ["USD", "EUR"]:
        raise ValueError(f"Неподдерживаемая валюта: {currency_code}")

    # 4. Получаем API-ключи из .env
    api_key = os.getenv("EXCHANGE_API_KEY")
    base_url = os.getenv("EXCHANGE_API_URL")

    if not api_key:
        raise ValueError("EXCHANGE_API_KEY не задан в .env")
    if not base_url:
        raise ValueError("EXCHANGE_API_URL не задан в .env")

    # 5. Делаем запрос к API
    try:
        headers = {"apikey": api_key}
        params = {"base": currency_code, "symbols": "RUB"}
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        rate = Decimal(str(data["rates"]["RUB"]))
    except (requests.RequestException, KeyError, ValueError) as e:
        raise RuntimeError(f"Ошибка при получении курса: {e}")

    # 6. Конвертируем сумму
    rubles = Decimal(str(amount)) * rate
    rubles = rubles.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return float(rubles)
