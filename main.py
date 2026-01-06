from utils.financial import get_transaction_rubles, load_financial_transactions

# Путь к файлу с транзакциями
file_path = "data/operations.json"

# Загружаем транзакции
transactions = load_financial_transactions(file_path)

print("Транзакции и их суммы в рублях:")
for transaction in transactions:
    # Проверяем наличие 'id' в транзакции
    if "id" not in transaction:
        print("Ошибка: Транзакция без поля 'id', пропускаем")
        continue  # пропускаем дальнейшую обработку

    rubles = get_transaction_rubles(transaction)

    if rubles is not None:
        print(f"ID: {transaction['id']} | " f"Сумма: {rubles:.2f} RUB | " f"Дата: {transaction['date']}")
    else:
        print(f"ID: {transaction['id']} | Ошибка конвертации")
