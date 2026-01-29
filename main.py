from datetime import datetime
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, cast

import pandas as pd

# Импорт openpyxl для чтения xlsx
try:
    import openpyxl

    HAVE_OPENPYXL = True
except Exception:
    HAVE_OPENPYXL = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_json(path: str) -> List[Dict[str, Any]]:
    logging.info(f"Начало загрузки транзакций из файла: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON должен содержать список операций")
    logging.info(f"Загружено {len(data)} транзакций из файла {path}")
    return data


def load_csv(path: str) -> List[Dict[str, Any]]:
    logging.info(f"Начало загрузки транзакций из файла: {path}")
    try:
        # Читаем через pandas, он автоматически пробует разные разделители или мы указываем ;
        # utf-8-sig убирает невидимый символ BOM в начале файла
        df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")

        # Превращаем в список словарей
        rows = cast(List[Dict[str, Any]], df.to_dict(orient="records"))

        logging.info(f"Загружено {len(rows)} транзакций из файла {path}")
        return rows
    except Exception as e:
        logging.error(f"Ошибка при чтении CSV: {e}")
        return []


def load_xlsx(path: str) -> List[Dict[str, Any]]:
    if not HAVE_OPENPYXL:
        raise RuntimeError("Для чтения XLSX требуется пакет openpyxl (pip install openpyxl)")
    logging.info(f"Начало загрузки транзакций из файла: {path}")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = wb.active
    rows = list(sheet.rows)
    if not rows:
        return []
    headers = [str(cell.value).strip() if cell.value is not None else "" for cell in rows[0]]
    result = []
    for r in rows[1:]:
        obj = {}
        for h, cell in zip(headers, r):
            obj[h] = cell.value
        result.append(obj)
    logging.info(f"Загружено {len(result)} транзакций из файла {path}")
    return result


def _get_status_from_op(op: Dict[str, Any]) -> Optional[str]:
    """Извлекает значение статуса, проверяя разные варианты написания ключей."""
    # Создаем временный словарь с ключами в нижнем регистре для удобного поиска
    norm_op = {str(k).lower().strip(): v for k, v in op.items()}

    # Список возможных имен колонок
    possible_keys = ("state", "status", "operationstate")

    for k in possible_keys:
        v = norm_op.get(k)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return None


def filter_by_status(data: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """Фильтрует список транзакций по заданному статусу."""
    target = status.strip().upper()
    filtered: List[Dict[str, Any]] = []
    for op in data:
        s = _get_status_from_op(op)  # ожидается, что эта функция возвращает str или None
        if s is None:
            continue
        if str(s).strip().upper() == target:
            filtered.append(op)
    return filtered


def _parse_date(d: Any) -> Optional[datetime]:
    if d is None:
        return None
    if isinstance(d, datetime):
        return d
    s = str(d)
    # Попытки наиболее частых форматов
    formats = ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d", "%d.%m.%Y", "%Y-%m-%d %H:%M:%S")
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    # Последний шанс: попытка извлечь дату через регулярку (yyyy-mm-dd)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", s)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d")
        except Exception:
            pass
    return None


def sort_by_date(data: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
    def key(op: Dict[str, Any]) -> Any:
        d = op.get("date") or op.get("operationDate") or op.get("createdAt")
        parsed = _parse_date(d)
        # если не парсится — вернем минимальную дату, чтобы такие записи шли в конец/начало
        return parsed or (datetime.min if reverse else datetime.max)

    return sorted(data, key=key, reverse=reverse)


def _get_amount_and_currency(op: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    # Обычная структура: operationAmount: { "amount": "...", "currency": {"name": "руб."} }
    oa = op.get("operationAmount")
    if isinstance(oa, dict):
        amount = oa.get("amount") or oa.get("value") or oa.get("sum")
        cur = None
        cur_field = oa.get("currency")
        if isinstance(cur_field, dict):
            cur = cur_field.get("name") or cur_field.get("code")
        elif cur_field:
            cur = str(cur_field)
        else:
            # может быть ключи amountCurrency, currency_code, etc.
            cur = op.get("currency") or op.get("amountCurrency")
        return (str(amount) if amount is not None else None, str(cur) if cur is not None else None)
    # fallback
    amount = op.get("amount") or op.get("sum")
    cur = op.get("currency")
    return (str(amount) if amount is not None else None, str(cur) if cur is not None else None)


def _get_currency_name(op: Dict[str, Any]) -> Optional[str]:
    _, cur = _get_amount_and_currency(op)
    if not cur:
        # попробовать найти в тексте поля, содержащем "руб" и т.п.
        for v in op.values():
            if isinstance(v, str) and ("руб" in v.lower() or "rub" in v.lower()):
                return "RUB"
        return None
    return cur


def filter_only_rubles(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    res = []
    for op in data:
        cur = _get_currency_name(op)
        if not cur:
            continue
        if any(x in str(cur).upper() for x in ("RUB", "РУБ", "RUR", "R.")):
            res.append(op)
    return res


def _collect_text_from_op(op: Dict[str, Any]) -> str:
    parts = []
    keys = (
        "description",
        "operationDescription",
        "descriptionText",
        "payee",
        "reason",
        "comment",
        "notes",
        "details",
        "from",
        "to",
    )
    for k in keys:
        v = op.get(k)
        if v is None:
            continue
        if isinstance(v, dict):
            for sub in v.values():
                if sub is None:
                    continue
                parts.append(str(sub))
        else:
            parts.append(str(v))
    # добавить все строковые поля на всякий случай
    for k, v in op.items():
        if k in keys:
            continue
        if isinstance(v, str):
            parts.append(v)
    return " ".join(parts)


def process_bank_search(data: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    if not query:
        return data
    try:
        pattern = re.compile(query, flags=re.IGNORECASE)
    except re.error:
        pattern = re.compile(re.escape(query), flags=re.IGNORECASE)
    res = []
    for op in data:
        try:
            text = _collect_text_from_op(op)
        except Exception:
            continue
        if pattern.search(text):
            res.append(op)
    return res


def mask_account(acc: str) -> str:
    if not acc:
        return ""
    s = str(acc)
    # простая маскировка: цифры оставляем последние 4, остальные заменяем на '*'
    digits = re.sub(r"\D", "", s)
    if len(digits) >= 4:
        shown = digits[-4:]
        masked_digits = "*" * (len(digits) - 4) + shown
        # теперь вставим masked_digits в исходную строк, заменив цифры по порядку
        res = []
        di = 0
        for ch in s:
            if ch.isdigit():
                res.append(masked_digits[di])
                di += 1
            else:
                res.append(ch)
        return "".join(res)
    else:
        return s


def format_operation(op: Dict[str, Any]) -> str:
    # Дата
    d = op.get("date") or op.get("operationDate") or op.get("createdAt")
    dt = _parse_date(d)
    date_str = dt.strftime("%d.%m.%Y") if dt else (str(d) if d is not None else "")
    # Описание
    desc = op.get("description") or op.get("operationDescription") or ""
    # from/to
    frm = op.get("from") or op.get("sender") or op.get("accountFrom")
    to = op.get("to") or op.get("recipient") or op.get("accountTo")
    # amount & currency
    amount, currency = _get_amount_and_currency(op)
    currency = currency or ""
    lines = []
    header = f"{date_str} {desc}".strip()
    lines.append(header)
    if frm:
        lines.append(f"{mask_account(str(frm))} -> {mask_account(str(to))}" if to else f"{mask_account(str(frm))}")
    elif to:
        lines.append(mask_account(str(to)))
    # Сумма
    if amount:
        lines.append(f"Сумма: {amount} {currency}".strip())
    else:
        # возможная структура: amount как вложенный словарь
        lines.append("Сумма: -")
    return "\n".join(lines)


def prompt_yes_no(prompt: str) -> bool:
    while True:
        a = input(prompt + "\nПользователь: ").strip().lower()
        if a in ("да", "д", "yes", "y"):
            return True
        if a in ("нет", "н", "no", "n"):
            return False
        print('Программа: Пожалуйста, введите "Да" или "Нет".')


def main() -> None:
    print("Программа: Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Программа: Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    loaders = {
        "1": ("JSON", load_json),
        "2": ("CSV", load_csv),
        "3": ("XLSX", load_xlsx),
    }

    while True:
        choice = input("Пользователь: ").strip()
        if choice in loaders:
            filetype, loader = loaders[choice]
            print(f"Программа: Для обработки выбран {filetype}-файл.")
            break
        else:
            print("Программа: Неверный выбор. Введите 1, 2 или 3.")

    # Ввод пути к файлу и загрузка (с повтором при ошибке)
    data: List[Dict[str, Any]] = []
    while True:
        path = input("Программа: Введите путь к файлу:\nПользователь: ").strip()
        try:
            data = loader(path)
            break
        except FileNotFoundError:
            logging.error(f"Файл не найден: {path}")
            print("Программа: Не удалось загрузить данные из указанного файла. Попробуйте ещё раз.")
        except Exception as e:
            logging.error(f"Ошибка при загрузке: {e}")
            print("Программа: Не удалось загрузить данные из указанного файла. Попробуйте ещё раз.")

    # Ввод статуса
    valid_statuses = ("EXECUTED", "CANCELED", "PENDING")
    while True:
        print("Программа: Введите статус, по которому необходимо выполнить фильтрацию.")
        print(f"Доступные для фильтровки статусы: {', '.join(valid_statuses)}")
        st = input("Пользователь: ").strip()
        if not st:
            print("Программа: Пожалуйста, введите статус.")
            continue
        st_up = st.upper()
        if st_up not in valid_statuses:
            print(f'Программа: Статус операции "{st}" недоступен.')
            continue
        data = filter_by_status(data, st_up)
        print(f'Программа: Операции отфильтрованы по статусу "{st_up}"')
        break

    # Сортировать по дате?
    if prompt_yes_no("Программа: Отсортировать операции по дате? Да/Нет"):
        # спросить направление
        while True:
            print("Программа: Отсортировать по возрастанию или по убыванию?")
            direction = input("Пользователь: ").strip().lower()
            if "воз" in direction or "asc" in direction:
                data = sort_by_date(data, reverse=False)
                break
            if "уб" in direction or "desc" in direction:
                data = sort_by_date(data, reverse=True)
                break
            print("Программа: Пожалуйста, введите 'по возрастанию' или 'по убыванию'.")

    # Только рублевые?
    if prompt_yes_no("Программа: Выводить только рублевые транзакции? Да/Нет"):
        data = filter_only_rubles(data)

    # Поиск по описанию
    if prompt_yes_no("Программа: Отфильтровать список транзакций по определенному слову в описании? Да/Нет"):
        print("Программа: Введите слово или регулярное выражение для поиска в описании")
        query = input("Пользователь: ")
        # Если пользователь ввёл пустую строку — не фильтруем
        if query.strip():
            data = process_bank_search(data, query.strip())

    # Вывод результата
    print("Программа: Распечатываю итоговый список транзакций...")
    print()

    if not data:
        print("Программа: Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    print(f"Программа: \nВсего банковских операций в выборке: {len(data)}")
    for op in data:
        print()
        print(format_operation(op))
        print()


if __name__ == "__main__":
    main()
