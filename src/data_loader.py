import logging
from typing import Any, Dict, List, cast

import pandas as pd

logger = logging.getLogger(__name__)


def load_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Считывает транзакции из CSV-файла и приводит их к стандартному виду.
    """
    try:
        # utf-8-sig обрабатывает возможный BOM в начале файла
        df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")

        if df.empty:
            logger.info(f"Файл {file_path} пуст.")
            return []

        # Унификация: переименовываем колонку со статусом в 'state', если она называется иначе
        df = _normalize_columns(df)

        transactions = cast(List[Dict[str, Any]], df.to_dict(orient="records"))
        logger.info("Загружено %d транзакций из CSV: %s", len(transactions), file_path)
        return transactions

    except FileNotFoundError:
        logger.error("Файл не найден: %s", file_path)
        return []
    except Exception as e:
        logger.error("Ошибка при чтении CSV-файла %s: %s", file_path, e)
        return []


def load_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    Считывает транзакции из Excel-файла (XLSX).
    """
    try:
        # Добавлен engine='openpyxl' для надежности
        df = pd.read_excel(file_path, engine="openpyxl")

        if df.empty:
            return []

        df = _normalize_columns(df)

        transactions = cast(List[Dict[str, Any]], df.to_dict(orient="records"))
        logger.info("Загружено %d транзакций из Excel: %s", len(transactions), file_path)
        return transactions
    except Exception as e:
        logger.error("Ошибка при чтении Excel-файла %s: %s", file_path, e)
        return []


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Внутренняя функция для поиска колонки со статусом.
    Если колонки 'state' нет, ищет колонку, содержащую 'EXECUTED'.
    """
    # 1. Если колонка 'state' уже есть, ничего не делаем
    if "state" in df.columns:
        return df

    # 2. Ищем колонку, где встречаются банковские статусы
    possible_statuses = {"EXECUTED", "CANCELED", "PENDING"}

    for col in df.columns:
        # Проверяем первые 10 строк колонки на наличие статусов
        sample_values = df[col].astype(str).str.upper().unique()
        if any(status in sample_values for status in possible_statuses):
            logger.info(f"Колонка статуса определена как: '{col}'")
            return df.rename(columns={col: "state"})

    return df
