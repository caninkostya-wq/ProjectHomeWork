# tests/test_module.py

import sys
from pathlib import Path

# Добавляем папку src в путь, чтобы можно было импортировать widget
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

import widget


# Список тестовых данных
test_cases = [
    "Maestro 1596837868705199",
    "Счет 64686473678894779589",
    "MasterCard 7158300734726758",
    "Счет 35383033474447895560",
    "Visa Classic 6831982476737658",
    "Visa Platinum 8990922113665229",
    "Visa Gold 5999414228426353",
    "Счет 73654108430135874305"
]

print("🔍 Тестирование mask_account_card на нескольких строках:\n")

for case in test_cases:
    try:
        result = widget.mask_account_card(case)
        print(f"{case} → {result}")
    except Exception as e:
        print(f"{case} → ОШИБКА: {e}")