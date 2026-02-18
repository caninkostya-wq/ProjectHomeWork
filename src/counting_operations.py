from collections import Counter


def process_bank_operations(data: list[dict], categories: list) -> dict:
    """
    Подсчитывает количество операций для каждой указанной категории.
    Категория определяется по наличию подстроки в 'description'.

    Args:
        data: список словарей с данными о банковских операциях.
        categories: список строк‑категорий (подстрок для поиска в description).

    Returns:
        Словарь: ключи — названия категорий, значения — количество операций.
    """
    if not data or not categories:
        return {category: 0 for category in categories}

    # Преобразуем категории в нижний регистр для сравнения
    categories_lower = [category.lower() for category in categories]

    # Собираем все подходящие категории для каждой операции
    matched_categories = []
    for operation in data:
        description = operation.get("description", "").lower()
        for category in categories_lower:
            if category in description:
                matched_categories.append(category)

    # Подсчитываем количество для каждой категории
    counter = Counter(matched_categories)

    # Формируем итоговый словарь с исходными названиями категорий
    result = {}
    for category in categories:
        result[category] = counter.get(category.lower(), 0)
    return result
