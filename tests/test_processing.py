from src.processing import filter_by_state, sort_by_date

# Тестовые данные
TEST_OPERATIONS = [
    {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
    {"id": 2, "state": "CANCELED", "date": "2024-01-02"},
    {"id": 3, "state": "EXECUTED", "date": "2024-01-03"},
]


def test_filter_by_state_default():
    """Проверяет, что по умолчанию фильтрует по 'EXECUTED'"""
    result = filter_by_state(TEST_OPERATIONS)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 3
    assert all(op["state"] == "EXECUTED" for op in result)


def test_filter_by_state_custom():
    """Проверяет фильтрацию по статусу 'CANCELED'"""
    result = filter_by_state(TEST_OPERATIONS, state="CANCELED")
    assert len(result) == 1
    assert result[0]["id"] == 2
    assert result[0]["state"] == "CANCELED"


def test_filter_by_state_empty():
    """Проверяет, что возвращает пустой список, если нет совпадений"""
    result = filter_by_state(TEST_OPERATIONS, state="PENDING")
    assert result == []


def test_sort_by_date_desc():
    """Проверяет сортировку по дате: от новых к старым (по умолчанию)"""
    result = sort_by_date(TEST_OPERATIONS)
    assert result[0]["id"] == 3  # Самая свежая дата
    assert result[1]["id"] == 2
    assert result[2]["id"] == 1


def test_sort_by_date_asc():
    """Проверяет сортировку по дате: от старых к новым"""
    result = sort_by_date(TEST_OPERATIONS, reverse=False)
    assert result[0]["id"] == 1  # Самая ранняя дата
    assert result[1]["id"] == 2
    assert result[2]["id"] == 3
