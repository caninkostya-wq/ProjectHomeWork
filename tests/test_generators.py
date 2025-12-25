import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions


def test_filter_by_currency_basic():
    """Базовый сценарий: фильтрация USD"""
    transactions = [
        {"operationAmount": {"currency": {"code": "USD"}}},
        {"operationAmount": {"currency": {"code": "EUR"}}},
        {"operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 2
    assert all(t["operationAmount"]["currency"]["code"] == "USD" for t in result)


def test_filter_by_currency_no_matches():
    """Нет транзакций в заданной валюте"""
    transactions = [{"operationAmount": {"currency": {"code": "EUR"}}}]
    result = list(filter_by_currency(transactions, "USD"))
    assert result == []


def test_filter_by_currency_missing_operationAmount():
    """Транзакция без operationAmount пропускается"""
    transactions = [{}, {"operationAmount": {"currency": {"code": "USD"}}}]  # нет operationAmount
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1


def test_filter_by_currency_missing_currency():
    """Транзакция без currency пропускается"""
    transactions = [{"operationAmount": {}}, {"operationAmount": {"currency": {"code": "USD"}}}]  # нет currency
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1


def test_filter_by_currency_empty_list():
    """Пустой список транзакций"""
    result = list(filter_by_currency([], "USD"))
    assert result == []


def test_transaction_descriptions_basic():
    """Возвращает описания всех транзакций"""
    transactions = [
        {"description": "Перевод 1"},
        {"description": "Перевод 2"},
        {"description": "Перевод 3"},
    ]
    result = list(transaction_descriptions(transactions))
    assert result == ["Перевод 1", "Перевод 2", "Перевод 3"]


def test_transaction_descriptions_empty_list():
    """Пустой список — возвращает пустой итератор"""
    result = list(transaction_descriptions([]))
    assert result == []


def test_transaction_descriptions_missing_description():
    """Транзакции без description пропускаются"""
    transactions = [
        {"description": "Есть описание"},
        {},  # нет description
        {"description": "Ещё описание"},
        {"desc": "не то поле"},  # не description
    ]
    result = list(transaction_descriptions(transactions))
    assert result == ["Есть описание", "Ещё описание"]


def test_transaction_descriptions_all_missing():
    """Все транзакции без description — возвращается пустой список"""
    transactions = [{}, {"foo": "bar"}]
    result = list(transaction_descriptions(transactions))
    assert result == []


def test_card_number_generator_basic():
    """Базовая генерация: 1–3"""
    result = list(card_number_generator(1, 3))
    assert result == ["0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003"]


def test_card_number_generator_single():
    """Один номер"""
    result = list(card_number_generator(42, 42))
    assert result == ["0000 0000 0000 0042"]


def test_card_number_generator_large_numbers():
    """Большие числа: корректное форматирование"""
    result = list(card_number_generator(9999999999999997, 9999999999999999))
    assert result == ["9999 9999 9999 9997", "9999 9999 9999 9998", "9999 9999 9999 9999"]


def test_card_number_generator_invalid_start():
    """start < 1 → ValueError"""
    with pytest.raises(ValueError):
        list(card_number_generator(0, 5))


def test_card_number_generator_invalid_end():
    """end > 9999999999999999 → ValueError"""
    with pytest.raises(ValueError):
        list(card_number_generator(1, 10000000000000000))


def test_card_number_generator_start_greater_than_end():
    """start > end → ValueError"""
    with pytest.raises(ValueError):
        list(card_number_generator(10, 5))


def test_card_number_generator_edge_case():
    """Крайний случай: максимальное число"""
    result = list(card_number_generator(9999999999999999, 9999999999999999))
    assert result == ["9999 9999 9999 9999"]


def test_filter_by_currency_case_sensitive():
    """Проверка чувствительности к регистру кода валюты"""
    transactions = [
        {"operationAmount": {"currency": {"code": "usd"}}},
        {"operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1  # Только верхний регистр совпадает
    assert result[0]["operationAmount"]["currency"]["code"] == "USD"


def test_filter_by_currency_nested_missing_code():
    """Транзакция с operationAmount и currency, но без code"""
    transactions = [
        {"operationAmount": {"currency": {}}},
        {"operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["operationAmount"]["currency"]["code"] == "USD"


def test_transaction_descriptions_none_description():
    """Транзакция с description=None пропускается"""
    transactions = [
        {"description": "Есть описание"},
        {"description": None},
        {"description": "Другое описание"},
    ]
    result = list(transaction_descriptions(transactions))
    assert result == ["Есть описание", "Другое описание"]


def test_transaction_descriptions_non_string_description():
    """Описание нестрокового типа (число, список и т.п.) пропускается"""
    transactions = [
        {"description": "Строка"},
        {"description": 123},
        {"description": ["список"]},
        {"description": {"ключ": "значение"}},
    ]
    result = list(transaction_descriptions(transactions))
    assert result == ["Строка"]


def test_card_number_generator_min_value():
    """Генерация минимального допустимого значения"""
    result = list(card_number_generator(1, 1))
    assert result == ["0000 0000 0000 0001"]


def test_card_number_generator_max_value():
    """Генерация максимального допустимого значения"""
    result = list(card_number_generator(9999999999999999, 9999999999999999))
    assert result == ["9999 9999 9999 9999"]


def test_card_number_generator_large_range_performance():
    """Генератор с start > end не выдаёт значений"""
    gen = card_number_generator(1000, 101)
    result = list(gen)
    assert result == []
