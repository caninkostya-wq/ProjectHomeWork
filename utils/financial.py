from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import pandas as pd

# Настройка логгера
logs_dir = Path(__file__).parent.parent / "logs"
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


def _load_json(file_path: Path) -> List[Dict[str, Any]]:
    """Загружает транзакции из JSON-файла."""
    if not file_path.exists():
        logger.error("Файл не найден: %s", file_path)
        return []

    if file_path.stat().st_size == 0:
        logger.warning("Файл пуст: %s", file_path)
        return []

    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            logger.error("Корневой элемент JSON не является списком: %s", file_path)
            return []
        return data
    except json.JSONDecodeError as e:
        logger.error("Ошибка JSON в файле %s: %s", file_path, e)
        return []
    except (IOError, OSError) as e:
        logger.error("Ошибка чтения файла %s: %s", file_path, e)
        return []


def _load_csv(file_path: Path) -> List[Dict[str, Any]]:
    """Загружает транзакции из CSV-файла с помощью pandas."""
    if not file_path.exists():
        logger.error("Файл не найден: %s", file_path)
        return []

    try:
        df = pd.read_csv(file_path)
        # Явно приводим тип результата
        return cast(List[Dict[str, Any]], df.to_dict(orient="records"))
    except pd.errors.EmptyDataError:
        logger.warning("CSV-файл пуст: %s", file_path)
        return []
    except Exception as e:
        logger.error("Ошибка при чтении CSV-файла %s: %s", file_path, e)
        return []


def _load_xlsx(file_path: Path) -> List[Dict[str, Any]]:
    """Загружает транзакции из XLSX-файла с помощью pandas."""
    if not file_path.exists():
        logger.error("Файл не найден: %s", file_path)
        return []

    try:
        df = pd.read_excel(file_path)
        # Явно приводим тип результата
        return cast(List[Dict[str, Any]], df.to_dict(orient="records"))
    except Exception as e:
        logger.error("Ошибка при чтении XLSX-файла %s: %s", file_path, e)
        return []


def load_financial_transactions(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из JSON, CSV или XLSX файла.

    Args:
        file_path: Путь к файлу (строка или Path).

    Returns:
        Список транзакций. Пустой список при ошибках.
    """
    path = Path(file_path)
    logger.info("Начало загрузки транзакций из файла: %s", path)

    # Определяем формат по расширению
    ext = path.suffix.lower()

    if ext == ".json":
        data = _load_json(path)
    elif ext == ".csv":
        data = _load_csv(path)
    elif ext in (".xlsx", ".xls"):
        data = _load_xlsx(path)
    else:
        logger.error("Неподдерживаемый формат файла: %s", ext)
        return []

    # Обрабатываем данные (общая логика для всех форматов)
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
            parsed_date = _parse_date(str(item["date"]))
            if parsed_date is not None:
                transaction["date"] = parsed_date
            else:
                logger.debug("Пропускаем транзакцию %d: неверная дата", i)
                continue

        # Извлекаем сумму и валюту
        if "operationAmount" in item:
            op_amount = item["operationAmount"]
            if isinstance(op_amount, dict) and "amount" in op_amount:
                try:
                    transaction["amount"] = float(op_amount["amount"])
                except (ValueError, TypeError):
                    logger.debug("Не удалось преобразовать amount в float для транзакции %d", i)
                    continue
            if isinstance(op_amount, dict) and "currency" in op_amount and "code" in op_amount["currency"]:
                transaction["currency_code"] = op_amount["currency"]["code"]

        transactions.append(transaction)
        logger.debug("Транзакция %d успешно обработана", i)

    logger.info("Загружено %d транзакций из файла %s", len(transactions), path)
    return transactions


def get_transaction_rubles(transaction: Dict[str, Any]) -> Optional[float]:
    """
    Возвращает сумму транзакции в рублях.

    Args:
        transaction: Транзакция с 'amount' и 'currency_code'.

    Returns:
        Сумма в рублях или None при ошибке.
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
