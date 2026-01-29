import re


def process_bank_search(data: list[dict], search: str) -> list[dict]:
    """
    Ищет в списке операций записи, где описание (description) содержит заданную строку (с учётом рег. выражений).

    Args:
        data: список словарей с данными о банковских операциях.
              Каждый словарь должен содержать ключ 'description'.
        search: строка поиска (может быть регулярным выражением).

    Returns:
        Список словарей, где в 'description' найдено совпадение.
    """
    if not data or not search:
        return []

    # Создаём шаблон регулярного выражения (игнорируем регистр)
    pattern = re.compile(search, re.IGNORECASE)

    result = []
    for operation in data:
        description = operation.get("description", "")
        if pattern.search(description):
            result.append(operation)

    return result
