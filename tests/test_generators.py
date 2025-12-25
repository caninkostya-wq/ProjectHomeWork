from typing import Any, Dict, List

import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions

# --- Фикстуры ---


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура: тестовые транзакции с разными валютами."""
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702",
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {"amount": "79114.93", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188",
        },
        {
            "id": 873105513,
            "state": "EXECUTED",
            "date": "2019-11-13T01:03:33.409181",
            "operationAmount": {"amount": "48223.05", "currency": {"name": "EUR", "code": "EUR"}},
            "description": "Перевод с карты на карту",
            "from": "Карта 3569141096704816",
            "to": "Карта 5211291757571595",
        },
        {
            "id": 594234712,
            "state": "CANCELED",
            "date": "2020-01-02T12:34:56.789012",
            "operationAmount": {"amount": "1000.00", "currency": {"name": "RUB", "code": "RUB"}},
            "description": "Снятие наличных",
            "from": "Карта 1234567890123456",
            "to": None,
        },
    ]


@pytest.fixture
def empty_transaction_list() -> List[Dict[str, Any]]:
    """Фикстура: пустой список транзакций."""
    return []


# --- Тесты для filter_by_currency ---


def test_filter_by_currency_usd(sample_transactions):
    """Тест: фильтрация по USD → 2 транзакции."""
    usd_gen = filter_by_currency(sample_transactions, "USD")
    result = list(usd_gen)
    assert len(result) == 2
    assert all(t["operationAmount"]["currency"]["code"] == "USD" for t in result)


def test_filter_by_currency_eur(sample_transactions):
    """Тест: фильтрация по EUR → 1 транзакция."""
    eur_gen = filter_by_currency(sample_transactions, "EUR")
    result = list(eur_gen)
    assert len(result) == 1
    assert result[0]["operationAmount"]["currency"]["code"] == "EUR"


def test_filter_by_currency_rub(sample_transactions):
    """Тест: фильтрация по RUB → 1 транзакция."""
    rub_gen = filter_by_currency(sample_transactions, "RUB")
    result = list(rub_gen)
    assert len(result) == 1
    assert result[0]["operationAmount"]["currency"]["code"] == "RUB"


def test_filter_by_currency_no_matches(sample_transactions):
    """Тест: валюта не найдена → пустой генератор."""
    none_gen = filter_by_currency(sample_transactions, "JPY")
    result = list(none_gen)
    assert result == []


def test_filter_by_currency_empty_list(empty_transaction_list):
    """Тест: пустой список транзакций → пустой генератор."""
    gen = filter_by_currency(empty_transaction_list, "USD")
    result = list(gen)
    assert result == []


def test_filter_by_currency_malformed_transaction(sample_transactions):
    """Тест: транзакция без operationAmount/currency → пропускается."""
    malformed = sample_transactions + [{"id": 999, "description": "Без суммы"}]  # Нет operationAmount
    gen = filter_by_currency(malformed, "USD")
    result = list(gen)
    assert len(result) == 2  # USD-транзакции остались, битая пропущена


# --- Тесты для transaction_descriptions ---


def test_transaction_descriptions_normal(sample_transactions):
    """Тест: корректные описания для всех транзакций."""
    desc_gen = transaction_descriptions(sample_transactions)
    descriptions = list(desc_gen)
    expected = ["Перевод организации", "Перевод со счета на счет", "Перевод с карты на карту", "Снятие наличных"]
    assert descriptions == expected


def test_transaction_descriptions_empty_list(empty_transaction_list):
    """Тест: пустой список → пустой генератор."""
    gen = transaction_descriptions(empty_transaction_list)
    result = list(gen)
    assert result == []


def test_transaction_descriptions_single_transaction():
    """Тест: одна транзакция → одно описание."""
    single = [{"description": "Оплата интернета"}]
    gen = transaction_descriptions(single)
    result = list(gen)
    assert result == ["Оплата интернета"]


def test_transaction_descriptions_missing_description(sample_transactions):
    """Тест: транзакция без description → пропускается."""
    with_missing = sample_transactions + [{"id": 999}]  # Нет description
    gen = transaction_descriptions(with_missing)
    result = list(gen)
    # Должно быть 4 описания (из sample_transactions) + пропущенная
    assert len(result) == 4


def test_transaction_descriptions_non_string_description():
    """Тест: description не строка → пропускается."""
    mixed = [
        {"description": "OK"},
        {"description": 123},  # не строка
        {"description": None},  # не строка
        {"description": ""},  # пустая строка (всё равно строка)
    ]
    gen = transaction_descriptions(mixed)
    result = list(gen)
    assert result == ["OK", ""]  # 123 и None пропущены


def test_transaction_descriptions_invalid_input_type():
    """Тест: input не список → TypeError."""
    with pytest.raises(TypeError):
        list(transaction_descriptions("not a list"))


# --- Тесты для card_number_generator ---


@pytest.mark.parametrize(
    "start,end,expected",
    [
        (1, 1, ["0000 0000 0000 0001"]),
        (2, 3, ["0000 0000 0000 0002", "0000 0000 0000 0003"]),
        (9999999999999998, 9999999999999999, ["9999 9999 9999 9998", "9999 9999 9999 9999"]),
        (1000, 1000, ["0000 0000 0000 1000"]),
    ],
)
def test_card_number_generator_basic(start, end, expected):
    """Тест: базовый функционал с разными диапазонами."""
    gen = card_number_generator(start, end)
    result = list(gen)
    assert result == expected


def test_card_number_generator_single_number():
    """Тест: генерация одного номера."""
    gen = card_number_generator(42, 42)
    result = list(gen)
    assert result == ["0000 0000 0000 0042"]


def test_card_number_generator_empty_range():
    """Тест: пустой диапазон (start > end) → пустой генератор."""
    # Явные граничные случаи
    gen1 = card_number_generator(5, 4)
    assert list(gen1) == []

    gen2 = card_number_generator(100, 99)
    assert list(gen2) == []

    # start == end + 1
    gen3 = card_number_generator(2, 1)
    assert list(gen3) == []


def test_card_number_generator_min_value():
    """Тест: минимальное допустимое значение (1)."""
    gen = card_number_generator(1, 1)
    result = list(gen)
    assert result == ["0000 0000 0000 0001"]


def test_card_number_generator_max_value():
    """Тест: максимальное допустимое значение."""
    gen = card_number_generator(9999999999999999, 9999999999999999)
    result = list(gen)
    assert result == ["9999 9999 9999 9999"]


def test_card_number_generator_invalid_start_type():
    """Тест: start не int → TypeError."""
    with pytest.raises(TypeError):
        list(card_number_generator("1", 5))


def test_card_number_generator_invalid_end_type():
    """Тест: end не int → TypeError."""
    with pytest.raises(TypeError):
        list(card_number_generator(1, "5"))


def test_card_number_generator_bool_as_input():
    """Тест: bool вместо int → TypeError (по условию, bool запрещён)."""
    with pytest.raises(TypeError):
        list(card_number_generator(True, 5))
    with pytest.raises(TypeError):
        list(card_number_generator(1, False))


def test_card_number_generator_start_less_than_1():
    """Тест: start < 1 → ValueError."""
    with pytest.raises(ValueError):
        list(card_number_generator(0, 5))
    with pytest.raises(ValueError):
        list(card_number_generator(-1, 5))


def test_card_number_generator_end_greater_than_max():
    """Тест: end > 9999999999999999 → ValueError."""
    with pytest.raises(ValueError):
        list(card_number_generator(1, 10**16))

    with pytest.raises(ValueError):
        list(card_number_generator(9999999999999999 + 1, 9999999999999999 + 2))


def test_card_number_generator_formatting():
    """Тест: проверка формата номера карты (4 группы по 4 цифры)."""
    gen = card_number_generator(1234567890123456, 1234567890123456)
    result = next(gen)  # берём первый (и единственный) элемент
    # Проверяем структуру: 4 группы, разделённые пробелами
    parts = result.split()
    assert len(parts) == 4
    assert all(len(part) == 4 and part.isdigit() for part in parts)


def test_card_number_generator_large_range():
    """Тест: большой диапазон (проверка производительности/корректности)."""
    gen = card_number_generator(9999999999999990, 9999999999999995)
    result = list(gen)
    assert len(result) == 6
    assert result[0] == "9999 9999 9999 9990"
    assert result[-1] == "9999 9999 9999 9995"


def test_card_number_generator_edge_cases():
    """Тест: пограничные случаи (близко к min/max)."""
    # Близко к минимуму
    gen1 = card_number_generator(2, 2)
    assert next(gen1) == "0000 0000 0000 0002"

    # Близко к максимуму
    gen2 = card_number_generator(9999999999999997, 9999999999999997)
    assert next(gen2) == "9999 9999 9999 9997"


def test_filter_by_currency_invalid_transactions_type():
    """Тест: transactions не список → TypeError."""
    with pytest.raises(TypeError):
        list(filter_by_currency("not a list", "USD"))
    with pytest.raises(TypeError):
        list(filter_by_currency(123, "USD"))
    with pytest.raises(TypeError):
        list(filter_by_currency({"key": "value"}, "USD"))


def test_filter_by_currency_invalid_currency_type():
    """Тест: currency не строка → TypeError."""
    transactions = [{"operationAmount": {"currency": {"code": "USD"}}}]
    with pytest.raises(TypeError):
        list(filter_by_currency(transactions, 123))
    with pytest.raises(TypeError):
        list(filter_by_currency(transactions, None))
    with pytest.raises(TypeError):
        list(filter_by_currency(transactions, ["USD"]))


def test_filter_by_currency_invalid_transaction_structure():
    """Тест: транзакция без operationAmount."""
    transactions = [{"id": 1, "description": "Без суммы"}]  # Нет operationAmount
    result = list(filter_by_currency(transactions, "USD"))
    assert result == []  # Должен пропустить некорректную транзакцию
