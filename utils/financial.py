from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional


def _parse_date(date_str: str) -> Optional[datetime]:
    """Преобразует строку в datetime. Поддерживает ISO-формат с микросекундами."""
    try:
        # Удаляем лишние микросекунды, если их больше 6 цифр
        if "." in date_str:
            date_str = date_str[: date_str.find(".") + 7]
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None


def load_financial_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из JSON-файла.

    Args:
        file_path (str): Путь к JSON-файлу.

    Returns:
        List[Dict]: Список транзакций. Пустой список при ошибках.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            if os.path.getsize(file_path) == 0:
                return []

            data = json.load(file)
            if not isinstance(data, list):
                return []

            transactions = []
            for item in data:
                if not isinstance(item, dict):
                    continue

                transaction = {}

                # Копируем простые поля
                for key in ["id", "state"]:
                    if key in item:
                        transaction[key] = item[key]

                # Обрабатываем дату
                if "date" in item:
                    parsed_date = _parse_date(item["date"])
                    if parsed_date is not None:
                        transaction["date"] = parsed_date
                    else:
                        continue  # Пропускаем при ошибке даты

                # Извлекаем сумму и валюту
                if "operationAmount" in item:
                    op_amount = item["operationAmount"]
                    if "amount" in op_amount:
                        try:
                            transaction["amount"] = float(op_amount["amount"])
                        except (ValueError, TypeError):
                            continue

                    if "currency" in op_amount and "code" in op_amount["currency"]:
                        transaction["currency_code"] = op_amount["currency"]["code"]

                transactions.append(transaction)

            return transactions

    except (json.JSONDecodeError, IOError, OSError):
        return []


def get_transaction_rubles(transaction: Dict[str, Any]) -> Optional[float]:
    """
    Возвращает сумму транзакции в рублях.

    Args:
        transaction (Dict): Транзакция с 'amount' и 'currency_code'.

    Returns:
        float: Сумма в рублях или None при ошибке.
    """
    amount = transaction.get("amount")
    currency = transaction.get("currency_code")

    if amount is None or currency is None:
        return None

    from external_api.currency_converter import CurrencyConverter

    converter = CurrencyConverter()
    return converter.convert_to_rubles(amount, currency)
