# tests/conftest.py
import pytest

# --- Фикстуры для карты ---


@pytest.fixture
def valid_card_number():
    """Валидный 16-значный номер карты"""
    return "1234567812345678"


@pytest.fixture
def card_with_spaces():
    """Номер карты с пробелами"""
    return "1234 5678 9012 3456"


@pytest.fixture
def card_with_dashes():
    """Номер карты с дефисами"""
    return "1234-5678-9012-3456"


@pytest.fixture
def card_with_letters():
    """Номер карты с текстом (например, название карты)"""
    return "Visa 1234-5678-9012-3456"


@pytest.fixture
def invalid_card_short():
    """Короткий номер — 15 цифр"""
    return "123456789012345"


@pytest.fixture
def invalid_card_long():
    """Длинный номер — 17 цифр"""
    return "12345678901234567"


@pytest.fixture
def no_digits():
    """Строка без цифр"""
    return "abcdef"


# --- Фикстуры для счёта ---


@pytest.fixture
def valid_account_number():
    """Валидный номер счёта (20 цифр)"""
    return "73654108430135874305"


@pytest.fixture
def account_with_spaces():
    """Номер счёта с пробелами"""
    return "7365 4108 4301 3587 4305"


@pytest.fixture
def account_with_letters():
    """Номер счёта с текстом"""
    return "Счёт: 73654108430135874305"


@pytest.fixture
def min_account():
    """Минимальная длина — 4 цифры"""
    return "1234"


@pytest.fixture
def account_less_than_4():
    """Меньше 4 цифр"""
    return "123"
