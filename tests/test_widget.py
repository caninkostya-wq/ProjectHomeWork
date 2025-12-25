from pathlib import Path
import sys

import pytest

from src import widget

# Добавляем src в путь, чтобы можно было импортировать widget
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))


@pytest.mark.parametrize(
    "input_data, expected",
    [
        ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
        ("Счет 64686473678894779589", "Счет **9589"),
        ("MasterCard 7158300734726758", "MasterCard 7158 30** **** 6758"),
        ("Счет 35383033474447895560", "Счет **5560"),
        ("Visa Classic 6831982476737658", "Visa Classic 6831 98** **** 7658"),
        ("Visa Platinum 8990922113665229", "Visa Platinum 8990 92** **** 5229"),
        ("Visa Gold 5999414228426353", "Visa Gold 5999 41** **** 6353"),
        ("Счет 73654108430135874305", "Счет **4305"),
    ],
    ids=[
        "Maestro_card",
        "Account_6468",
        "MasterCard",
        "Account_3538",
        "Visa_Classic",
        "Visa_Platinum",
        "Visa_Gold",
        "Account_7365",
    ],
)
def test_mask_account_card_parametrized(input_data, expected):
    """Проверяет корректность маскировки номера карты или счёта"""
    assert widget.mask_account_card(input_data) == expected


def test_get_date():
    """Проверяет форматирование строки даты"""
    assert widget.get_date("2024-03-11T02:26:18.671407") == "11.03.2024"


def test_mask_account_card_empty_string():
    """Тест: пустая строка → ValueError"""
    with pytest.raises(ValueError) as excinfo:
        widget.mask_account_card("")
    assert "Входная строка не должна быть пустой" in str(excinfo.value)


def test_mask_account_card_whitespace_only():
    """Тест: строка из пробелов → ValueError"""
    with pytest.raises(ValueError) as excinfo:
        widget.mask_account_card("   ")
    assert "Входная строка не должна быть пустой" in str(excinfo.value)


def test_mask_account_card_single_word_no_space():
    """Тест: одно слово без пробела (нет разделения на название и номер) → ValueError"""
    with pytest.raises(ValueError) as excinfo:
        widget.mask_account_card("ТолькоНазвание")
    assert "Неверный формат: ожидалось название и номер карты" in str(excinfo.value)


def test_mask_account_card_leading_trailing_spaces():
    """Тест: пробелы в начале/конце не должны мешать разбору"""
    result = widget.mask_account_card("  Visa Classic 6831982476737658  ")
    assert result == "Visa Classic 6831 98** **** 7658!  # Пробелов нет!"


def test_mask_account_card_multiple_spaces_in_name():
    """Тест: название с несколькими словами (American Express)"""
    # Исправлено: номер карты теперь 16-значный
    result = widget.mask_account_card("American Express 6771736525223847")
    assert result == "American Express 6771 73** **** 3847"


def test_mask_account_card_account_with_extra_spaces():
    """Тест: 'Счет ' с лишними пробелами → корректно обрезается"""
    result = widget.mask_account_card("Счет    12345678901234567890")
    assert result == "Счет **7890"


def test_mask_account_card_invalid_account_format():
    """Тест: 'СчетХ' (без пробела) → ValueError"""
    with pytest.raises(ValueError) as excinfo:
        widget.mask_account_card("СчетХ12345")
    assert "Неверный формат: ожидалось название и номер карты" in str(excinfo.value)


def test_get_date_invalid_format():
    """Тест: неверная строка даты → ValueError (если функция проверяет формат)"""
    # Если get_date ожидает строго ISO-формат, добавьте проверку
    with pytest.raises(ValueError):
        widget.get_date("не-дата")
    with pytest.raises(ValueError):
        widget.get_date("")


def test_get_date_edge_cases():
    """Тест: крайние случаи формата даты"""
    # Минимально возможная дата
    assert widget.get_date("0001-01-01T00:00:00") == "01.01.0001"
    # Максимально возможная дата (в рамках разумного)
    assert widget.get_date("9999-12-31T23:59:59") == "31.12.9999"

    def test_mask_account_card_spaces_in_parts():
        """Тест: пробелы внутри названия и номера карты"""
        result = widget.mask_account_card("Visa   Classic   6831982476737658")
        assert result == "Visa Classic 6831 98** **** 7658"

    def test_mask_account_card_only_spaces():
        """Тест: строка из пробелов → ValueError"""
        with pytest.raises(ValueError) as excinfo:
            widget.mask_account_card("   ")
        assert "Входная строка не должна быть пустой" in str(excinfo.value)
