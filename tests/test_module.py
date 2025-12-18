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

# изменение
