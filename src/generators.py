from typing import Any, Dict, Generator, List


def filter_by_currency(transactions: List[Dict[str, Any]], currency: str) -> Generator[Dict[str, Any], None, None]:
    """
    Фильтрует транзакции по указанной валюте.

    Args:
        transactions: список транзакций (словарей)
        currency: код валюты (например, "USD", "RUB")

    Yields:
        Транзакции, где operationAmount.currency.code совпадает с заданной валютой

    Example:
        usd_transactions = filter_by_currency(transactions, "USD")
        for _ in range(2):
            print(next(usd_transactions))
    """
    if not isinstance(transactions, list):
        raise TypeError(f"transactions должен быть списком, получено {type(transactions).__name__}")

    if not isinstance(currency, str):
        raise TypeError(f"currency должен быть строкой, получено {type(currency).__name__}")

    for transaction in transactions:
        # Проверяем, что элемент — словарь
        if not isinstance(transaction, dict):
            continue

        # Получаем блок operationAmount
        operation_amount = transaction.get("operationAmount")
        if not operation_amount:
            continue  # Пропускаем транзакции без суммы операции

        # Получаем блок currency
        currency_info = operation_amount.get("currency")
        if not currency_info:
            continue  # Пропускаем, если нет информации о валюте

        # Получаем код валюты
        code = currency_info.get("code")
        if isinstance(code, str) and code == currency:
            yield transaction


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Generator[str, None, None]:
    """
    Возвращает описания транзакций по очереди.

    Args:
        transactions: список транзакций (словарей)

    Yields:
        Описание каждой транзакции (значение поля "description")

    Example:
        descriptions = transaction_descriptions(transactions)
        for _ in range(5):
            print(next(descriptions))
    """
    if not isinstance(transactions, list):
        raise TypeError(f"transactions должен быть списком, получено {type(transactions).__name__}")

    for transaction in transactions:
        # Проверяем, что элемент — словарь
        if not isinstance(transaction, dict):
            continue

        # Получаем описание операции
        description = transaction.get("description")

        # Если описание есть и это строка — отдаём
        if isinstance(description, str):
            yield description

        # Если описания нет или оно не строка — пропускаем
        else:
            continue


def card_number_generator(start: int, end: int) -> Generator[str, None, None]:
    """
    Генератор номеров банковских карт в формате XXXX XXXX XXXX XXXX.

    Args:
        start: начальное число диапазона (минимум 1)
        end: конечное число диапазона (максимум 9999999999999999)

    Yields:
        Строки с номерами карт в формате "XXXX XXXX XXXX XXXX"

    Raises:
        ValueError: если start < 1 или end > 9999999999999999
        TypeError: если start или end не являются целыми числами (или являются bool)

    Example:
        for card_number in card_number_generator(1, 5):
            print(card_number)
    """
    # Проверка типов (исключаем bool, т.к. он подкласс int)
    if not isinstance(start, int) or isinstance(start, bool):
        raise TypeError(f"start должен быть int (не bool), получено {type(start).__name__}")
    if not isinstance(end, int) or isinstance(end, bool):
        raise TypeError(f"end должен быть int (не bool), получено {type(end).__name__}")

    # Проверка значений
    if start < 1:
        raise ValueError("Начальное значение должно быть не меньше 1")
    if end > 9999999999999999:
        raise ValueError("Конечное значение не должно превышать 9999999999999999")
    if start > end:
        return  # Пустой генератор для пустого диапазона

    # Генерируем номера в заданном диапазоне
    for number in range(start, end + 1):
        # Форматируем число как 16‑значную строку с ведущими нулями
        num_str = f"{number:016d}"
        # Разбиваем на группы по 4 цифры
        formatted = f"{num_str[:4]} {num_str[4:8]} {num_str[8:12]} {num_str[12:16]}"
        yield formatted
