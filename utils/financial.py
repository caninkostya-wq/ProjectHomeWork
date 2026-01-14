from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Настройка логгера для модуля utils
logs_dir = Path(__file__).parent / "logs"
logs_dir.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_file = logs_dir / "utils.log"
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def _parse_date(date_str: str) -> Optional[datetime]:
    """Преобразует строку в datetime. Поддерживает ISO-формат с микросекундами."""
    try:
        if "." in date_str:
            date_str = date_str[: date_str.find(".") + 7]
        parsed = datetime.fromisoformat(date_str)
        logger.debug("Дата успешно преобразована: %s → %s", date_str, parsed)
        return parsed
    except ValueError as e:
        logger.warning("Не удалось преобразовать дату '%s': %s", date_str, e)
        return None


def load_financial_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из JSON-файла.
    """
    logger.info("Начало загрузки транзакций из файла: %s", file_path)

    if not os.path.exists(file_path):
        logger.error("Файл не найден: %s", file_path)
        return []

    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.warning("Файл пуст: %s", file_path)
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            logger.error("Корневой элемент JSON не является списком: %s", file_path)
            return []

        transactions = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                logger.debug("Элемент %d не является словарём, пропускаем", i)
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
                    logger.debug("Пропускаем транзакцию %d: неверная дата", i)
                    continue  # пропускаем транзакцию при ошибке даты

            # Извлекаем сумму и валюту
            if "operationAmount" in item:
                op_amount = item["operationAmount"]
                if "amount" in op_amount:
                    try:
                        transaction["amount"] = float(op_amount["amount"])
                    except (ValueError, TypeError) as e:
                        logger.debug("Не удалось преобразовать amount в float для транзакции %d: %s", i, e)
                        continue

                if "currency" in op_amount and "code" in op_amount["currency"]:
                    transaction["currency_code"] = op_amount["currency"]["code"]

            transactions.append(transaction)
            logger.debug("Транзакция %d успешно обработана", i)

        logger.info("Загружено %d транзакций из файла %s", len(transactions), file_path)
        return transactions

    except json.JSONDecodeError as e:
        logger.error("Ошибка JSON в файле %s: %s", file_path, e)
        return []
    except (IOError, OSError) as e:
        logger.error("Ошибка чтения файла %s: %s", file_path, e)
        return []


def get_transaction_rubles(transaction: Dict[str, Any]) -> Optional[float]:
    """
    Возвращает сумму транзакции в рублях.
    """
    logger.info("Расчёт суммы в рублях для транзакции: %s", transaction)

    amount = transaction.get("amount")
    currency = transaction.get("currency_code")

    if amount is None:
        logger.warning("В транзакции отсутствует поле 'amount'")
        return None
    if currency is None:
        logger.warning("В транзакции отсутствует поле 'currency_code'")
        return None

    try:
        from external_api.currency_converter import convert_transaction_to_rubles

        result = convert_transaction_to_rubles({"amount": amount, "currency": {"code": currency}})
        logger.info("Сумма в рублях рассчитана: %s %s → %f RUB", amount, currency, result)
        return result
    except Exception as e:
        logger.error("Ошибка при конвертации в рубли: %s", e)
        return None
