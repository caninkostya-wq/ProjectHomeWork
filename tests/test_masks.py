# tests/test_masks.py
import pytest

from src.masks import get_mask_account, get_mask_card_number

# --- Тесты для get_mask_card_number ---


def test_get_mask_card_number_valid(valid_card_number):
    assert get_mask_card_number(valid_card_number) == "1234 56** **** 5678"


def test_get_mask_card_number_with_spaces(card_with_spaces):
    assert get_mask_card_number(card_with_spaces) == "1234 56** **** 3456"


def test_get_mask_card_number_with_dashes(card_with_dashes):
    assert get_mask_card_number(card_with_dashes) == "1234 56** **** 3456"


def test_get_mask_card_number_with_letters(card_with_letters):
    assert get_mask_card_number(card_with_letters) == "1234 56** **** 3456"


def test_get_mask_card_number_invalid_length_short(invalid_card_short):
    with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
        get_mask_card_number(invalid_card_short)


def test_get_mask_card_number_invalid_length_long(invalid_card_long):
    with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
        get_mask_card_number(invalid_card_long)


def test_get_mask_card_number_no_digits(no_digits):
    with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
        get_mask_card_number(no_digits)


def test_get_mask_card_number_empty():
    with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
        get_mask_card_number("")


# --- Тесты для get_mask_account ---


def test_get_mask_account_valid(valid_account_number):
    assert get_mask_account(valid_account_number) == "**4305"


def test_get_mask_account_with_spaces(account_with_spaces):
    assert get_mask_account(account_with_spaces) == "**4305"


def test_get_mask_account_with_letters(account_with_letters):
    assert get_mask_account(account_with_letters) == "**4305"


def test_get_mask_account_min_length(min_account):
    assert get_mask_account(min_account) == "**1234"


def test_get_mask_account_less_than_4(account_less_than_4):
    with pytest.raises(ValueError, match="Номер счёта должен содержать как минимум 4 цифры"):
        get_mask_account(account_less_than_4)


def test_get_mask_account_empty():
    with pytest.raises(ValueError, match="Номер счёта должен содержать как минимум 4 цифры"):
        get_mask_account("")


def test_get_mask_account_only_letters(no_digits):
    with pytest.raises(ValueError, match="Номер счёта должен содержать как минимум 4 цифры"):
        get_mask_account("abcdef")
