from src.processing import filter_by_state, sort_by_date

# Тестовые данные
operations = [
    {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
    {"id": 2, "state": "CANCELED", "date": "2024-01-02"},
    {"id": 3, "state": "EXECUTED", "date": "2024-01-03"},
]

# Пример 1: фильтрация по статусу (по умолчанию 'EXECUTED')
print("1. Операции со статусом 'EXECUTED':")
executed = filter_by_state(operations)
print(executed)
print()  # Пустая строка для красоты

# Пример 2: фильтрация по 'CANCELED'
print("2. Операции со статусом 'CANCELED':")
canceled = filter_by_state(operations, state="CANCELED")
print(canceled)
print()

# Пример 3: сортировка по дате — от новых к старым (по умолчанию)
print("3. Сортировка по дате (от новых к старым):")
sorted_desc = sort_by_date(operations)
print(sorted_desc)
print()

# Пример 4: сортировка по дате — от старых к новым
print("4. Сортировка по дате (от старых к новым):")
sorted_asc = sort_by_date(operations, reverse=False)
print(sorted_asc)
