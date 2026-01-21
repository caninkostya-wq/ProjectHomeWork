# from src.utils import get_transaction_rubles, load_financial_transactions
#
#  Путь к файлу с транзакциями
# file_path = "data/operations.json"
#
#  Загружаем транзакции
# transactions = load_financial_transactions(file_path)
#
# print("Транзакции и их суммы в рублях:")
# for transaction in transactions:
#    # Проверяем наличие 'id' в транзакции
#    if "id" not in transaction:
#        print("Ошибка: Транзакция без поля 'id', пропускаем")
#        continue  # пропускаем дальнейшую обработку
#
#    rubles = get_transaction_rubles(transaction)
#
#    if rubles is not None:
#        print(f"ID: {transaction['id']} | " f"Сумма: {rubles:.2f} RUB | " f"Дата: {transaction['date']}")
#    else:
#        print(f"ID: {transaction['id']} | Ошибка конвертации")


"""
Точка входа в приложение.
Импортирует модули masks и utils, вызывает их функции для генерации логов.
"""

# Импортируем функции из ваших модулей
from src.masks import get_mask_account, get_mask_card_number
from src.utils import get_transaction_rubles, load_financial_transactions


def main() -> None:
    print("Запуск тестов для генерации логов...")

    # 1. Тестируем модуль masks
    print("\n1. Тестирование masks:")
    try:
        # Маска карты
        card = get_mask_card_number("1234 5678 9012 3456")
        print(f"Маска карты: {card}")

        # Маска счёта
        account = get_mask_account("7890123456")
        print(f"Маска счёта: {account}")

    except Exception as e:
        print(f"Ошибка в masks: {e}")

    # 2. Тестируем модуль utils
    print("\n2. Тестирование utils:")
    try:
        # Загрузка транзакций (укажите путь к вашему JSON-файлу)
        transactions = load_financial_transactions("data/operations.json")
        print(f"Загружено транзакций: {len(transactions)}")

        # Если есть транзакции, попробуем конвертировать первую
        if transactions:
            rubles = get_transaction_rubles(transactions[0])
            print(f"Сумма в рублях: {rubles}")

    except Exception as e:
        print(f"Ошибка в utils: {e}")

    print("\nЛоги сгенерированы. Проверьте папку logs/")


if __name__ == "__main__":
    main()
