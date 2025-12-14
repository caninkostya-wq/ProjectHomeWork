from src.masks import get_mask_card_number, get_mask_account


def mask_account_card(info: str) -> str:
    """
    Маскирует номер карты или счёта в зависимости от типа.
    Использует готовые функции get_mask_card_number и get_mask_account.

    Args:
        info (str): Строка с типом и номером. Пример: 'Visa Platinum 7000792289606361' или 'Счет 73654108430135874305'

    Returns:
        str: Строка с замаскированным номером.
    """
    if not info.strip():
        raise ValueError("Входная строка не должна быть пустой")

    if info.startswith("Счет "):
        account_number = info[5:]  # вырезаем номер после "Счет "
        masked_number = get_mask_account(account_number)
        return f"Счет {masked_number}"
    else:
        # Для карт: разделяем по последнему пробелу (на случай, если в названии несколько слов)
        parts = info.rsplit(maxsplit=1)
        if len(parts) != 2:
            raise ValueError("Неверный формат: ожидалось название и номер карты")

        name = parts[0]
        card_number = parts[1]
        masked_number = get_mask_card_number(card_number)
        return f"{name} {masked_number}"
