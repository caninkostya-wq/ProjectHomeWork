from typing import Any, Dict, Generator


def filter_by_currency(transactions: list[Dict[str, Any]], currency: str) -> Generator[Dict[str, Any], None, None]:
    """
    Генератор, фильтрующий транзакции по указанной валюте.

    Args:
        transactions: список словарей с транзакциями
        currency: код валюты (например, "USD")


    Yields:
        Транзакции (словари), где валюта операции соответствует заданной


    Example:
        usd_transactions = filter_by_currency(transactions, "USD")
        for _ in range(2):
            print(next(usd_transactions))
    """
    for transaction in transactions:
        # Проверяем наличие всех необходимых ключей
        operation_amount = transaction.get("operationAmount")
        if not operation_amount:
            continue

        currency_info = operation_amount.get("currency")
        if not currency_info:
            continue

        code = currency_info.get("code")
        if code == currency:
            yield transaction


def transaction_descriptions(transactions: list[Dict[str, Any]]) -> Generator[str, None, None]:
    """
    Генератор, возвращающий описания транзакций по очереди.

    Args:
        transactions: список словарей с транзакциями

    Yields:
        Строка с описанием операции (значение поля "description")

    Example:
        descriptions = transaction_descriptions(transactions)
        for _ in range(5):
            print(next(descriptions))
    """
    for transaction in transactions:
        description = transaction.get("description")
        if isinstance(description, str) and description:  # Проверяем, что это не None и не пустая строка
            yield description


def card_number_generator(start: int, end: int) -> Generator[str, None, None]:
    """
    Генератор номеров банковских карт в формате XXXX XXXX XXXX XXXX.

    Args:
        start: начальное число диапазона (от 1 до 9999999999999999)
        end: конечное число диапазона (до 9999999999999999)


    Yields:
        Строка с номером карты в формате "XXXX XXXX XXXX XXXX"


    Example:
        for card_number in card_number_generator(1, 5):
            print(card_number)

    Raises:
        ValueError: Если диапазон некорректен (start > end, выход за границы)
    """
    # Проверяем корректность диапазона
    if start < 1 or end > 9999999999999999 or start > end:
        raise ValueError("Диапазон должен быть от 1 до 9999999999999999, start <= end")

    for number in range(start, end + 1):
        # Формируем строку из 16 цифр с ведущими нулями
        num_str = f"{number:016d}"
        # Разбиваем на группы по 4 цифры
        formatted = f"{num_str[:4]} {num_str[4:8]} {num_str[8:12]} {num_str[12:16]}"
        yield formatted
