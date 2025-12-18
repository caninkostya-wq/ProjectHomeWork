from datetime import datetime
from typing import Dict, List


def filter_by_state(operations: List[Dict], state: str = "EXECUTED") -> List[Dict]:
    """
    Возвращает список операций, у которых ключ 'state' равен заданному значению.

    :param operations: Список словарей с данными об операциях
    :param state: Значение ключа 'state' для фильтрации (по умолчанию 'EXECUTED')
    :return: Отфильтрованный список операций
    """
    return [op for op in operations if op.get("state") == state]


def sort_by_date(operations: List[Dict], reverse: bool = True) -> List[Dict]:
    """
    Возвращает список операций, отсортированный по дате (по умолчанию — от новых к старым).

    :param operations: Список словарей с данными об операциях
    :param reverse: Порядок сортировки: True — от новых к старым, False — от старых к новым
    :return: Отсортированный список операций
    """
    return sorted(operations, key=lambda op: datetime.strptime(op["date"], "%Y-%m-%d"), reverse=reverse)
