def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты: XXXX XX** **** XXXX
    """
    cleaned_number = "".join(filter(str.isdigit, card_number))

    if len(cleaned_number) != 16:
        raise ValueError("Номер карты должен содержать 16 цифр")

    masked = f"{cleaned_number[:4]} {cleaned_number[4:6]}** **** {cleaned_number[-4:]}"
    return masked


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер счёта: **XXXX
    """
    cleaned_number = "".join(filter(str.isdigit, account_number))

    if len(cleaned_number) < 4:
        raise ValueError("Номер счёта должен содержать как минимум 4 цифры")

    return f"**{cleaned_number[-4:]}"
