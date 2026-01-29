def process_bank_operations(data: list[dict], categories: list) -> dict:
    """
    Подсчитывает количество операций для каждой указанной категории.
    Категория определяется по наличию подстроки в 'description'.

    Args:
        data: список словарей с данными о банковских операциях.
        categories: список строк-категорий (подстрок для поиска в description).

    Returns:
        Словарь: ключи — названия категорий, значения — количество операций.
    """
    if not data or not categories:
        return {category: 0 for category in categories}

    result = {category: 0 for category in categories}

    for operation in data:
        description = operation.get("description", "").lower()
        for category in categories:
            if category.lower() in description:
                result[category] += 1

    return result
