import pytest

from src.masks import get_mask_account, get_mask_card_number

# --- Тесты для get_mask_card_number ---


def test_get_mask_card_number_valid():
    """Проверка корректного маскирования 16-значного номера карты"""
    result = get_mask_card_number("1234567812345678")
    assert result == "1234 56** **** 5678"


def test_get_mask_card_number_with_spaces():
    """Проверка, что функция корректно обрабатывает номер с пробелами"""
    result = get_mask_card_number("1234 5678 9012 3456")
    assert result == "1234 56** **** 3456"


def test_get_mask_card_number_with_dashes():
    """Проверка, что функция корректно обрабатывает номер с дефисами"""
    result = get_mask_card_number("1234-5678-9012-3456")
    assert result == "1234 56** **** 3456"


def test_get_mask_card_number_with_letters():
    """Проверка, что функция удаляет буквы и оставляет только цифры"""
    result = get_mask_card_number("Visa 1234-5678-9012-3456")
    assert result == "1234 56** **** 3456"


def test_get_mask_card_number_invalid_length_short():
    """Проверка, что функция выбрасывает ошибку при номере <16 цифр"""
    with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
        get_mask_card_number("123456789012345")


def test_get_mask_card_number_invalid_length_long():
    """Проверка, что функция выбрасывает ошибку при номере >16 цифр"""
    with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
        get_mask_card_number("12345678901234567")


def test_get_mask_card_number_no_digits():
    """Проверка, что функция выбрасывает ошибку, если цифр нет"""
    with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
        get_mask_card_number("abcdef")


def test_get_mask_card_number_empty():
    """Проверка пустой строки"""
    with pytest.raises(ValueError, match="Номер карты должен содержать 16 цифр"):
        get_mask_card_number("")


# --- Тесты для get_mask_account ---


def test_get_mask_account_valid():
    """Проверка корректного маскирования номера счёта"""
    result = get_mask_account("73654108430135874305")
    assert result == "**4305"


def test_get_mask_account_with_spaces():
    """Проверка, что функция корректно обрабатывает номер счёта с пробелами"""
    result = get_mask_account("7365 4108 4301 3587 4305")
    assert result == "**4305"


def test_get_mask_account_with_letters():
    """Проверка, что функция удаляет буквы из номера счёта"""
    result = get_mask_account("Счёт: 73654108430135874305")
    assert result == "**4305"


def test_get_mask_account_min_length():
    """Проверка маскирования при минимальной длине (4 цифры)"""
    result = get_mask_account("1234")
    assert result == "**1234"


def test_get_mask_account_less_than_4():
    """Проверка, что функция выбрасывает ошибку при менее чем 4 цифрах"""
    with pytest.raises(ValueError, match="Номер счёта должен содержать как минимум 4 цифры"):
        get_mask_account("123")


def test_get_mask_account_empty():
    """Проверка пустой строки"""
    with pytest.raises(ValueError, match="Номер счёта должен содержать как минимум 4 цифры"):
        get_mask_account("")


def test_get_mask_account_only_letters():
    """Проверка, что функция выбрасывает ошибку, если цифр нет"""
    with pytest.raises(ValueError, match="Номер счёта должен содержать как минимум 4 цифры"):
        get_mask_account("abcdef")
