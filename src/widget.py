from datetime import datetime

from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(info: str) -> str:
    info = info.strip()
    if not info:
        raise ValueError("Входная строка не должна быть пустой")

    if info.startswith("Счет "):
        account_number = info[5:].strip()
        if not account_number.isdigit():
            raise ValueError("Номер счёта должен содержать только цифры")
        masked_number = get_mask_account(account_number)
        return f"Счет {masked_number}"
    else:
        parts = info.rsplit(maxsplit=1)
        if len(parts) != 2:
            raise ValueError("Неверный формат: ожидалось название и номер карты")

        name_parts = [part for part in parts[0].strip().split() if part]
        name = " ".join(name_parts)
        card_number = parts[1].strip()

        if not name or not card_number:
            raise ValueError("Неверный формат: ожидалось название и номер карты")

        if not card_number.isdigit():
            raise ValueError("Номер карты должен содержать только цифры")

        masked_number = get_mask_card_number(card_number)
        return f"{name} {masked_number}"  # Ровно один пробел между частями


def get_date(date_string: str) -> str:
    """Преобразует ISO-дату в формат ДД.ММ.ГГГГ"""
    try:
        dt = datetime.fromisoformat(date_string.strip())
        return dt.strftime("%d.%m.%Y")
    except ValueError as e:
        raise ValueError(f"Неверный формат даты: {date_string}. Требуется ISO-формат (ГГГГ-ММ-ДДTHH:MM:SS)") from e
