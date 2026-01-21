import logging
from typing import Any, Dict, List, cast  # ← добавили cast

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Считывает транзакции из CSV-файла.

    Args:
       file_path (str): Путь к CSV-файлу.

    Returns:
       List[Dict]: Список транзакций в виде словарей.
    """
    try:
        df = pd.read_csv(file_path)
        transactions = cast(List[Dict[str, Any]], df.to_dict(orient="records"))
        logger.info("Загружено %d транзакций из CSV: %s", len(transactions), file_path)
        return transactions
    except Exception as e:
        logger.error("Ошибка при чтении CSV-файла %s: %s", file_path, e)
        return []


def load_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    Считывает транзакции из Excel-файла (XLSX).

    Args:
        file_path (str): Путь к XLSX-файлу.

    Returns:
        List[Dict]: Список транзакций в виде словарей.
    """
    try:
        df = pd.read_excel(file_path)
        transactions = cast(List[Dict[str, Any]], df.to_dict(orient="records"))
        logger.info("Загружено %d транзакций из Excel: %s", len(transactions), file_path)
        return transactions
    except Exception as e:
        logger.error("Ошибка при чтении Excel-файла %s: %s", file_path, e)
        return []
