import logging
from pathlib import Path

# Создаём папку logs в корне проекта, если её нет
logs_dir = Path(__file__).parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Настраиваем логгер для модуля masks
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создаём обработчик для записи в файл (перезаписывает файл при каждом запуске)
log_file = logs_dir / "masks.log"
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Форматируем вывод: время, модуль, уровень, сообщение
formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)


def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты: XXXX XX** **** XXXX
    """
    try:
        cleaned_number = "".join(filter(str.isdigit, card_number))

        if len(cleaned_number) != 16:
            logger.error("Номер карты содержит %d цифр (ожидается 16)", len(cleaned_number))
            raise ValueError("Номер карты должен содержать 16 цифр")

        masked = f"{cleaned_number[:4]} {cleaned_number[4:6]}** **** {cleaned_number[-4:]}"
        logger.info("Карта замаскирована: %s → %s", card_number, masked)
        return masked

    except Exception as e:
        logger.exception("Ошибка при маскировке карты: %s", e)
        raise


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер счёта: **XXXX
    """
    try:
        cleaned_number = "".join(filter(str.isdigit, account_number))

        if len(cleaned_number) < 4:
            logger.error("Номер счёта содержит %d цифр (минимум 4)", len(cleaned_number))
            raise ValueError("Номер счёта должен содержать как минимум 4 цифры")

        result = f"**{cleaned_number[-4:]}"
        logger.info("Счёт замаскирован: %s → %s", account_number, result)
        return result

    except Exception as e:
        logger.exception("Ошибка при маскировке счёта: %s", e)
        raise
