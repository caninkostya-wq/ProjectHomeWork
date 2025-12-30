import functools
from typing import Callable, ParamSpec, TypeVar, overload

# Типы для типизации декораторов
P = ParamSpec("P")
R = TypeVar("R")


@overload  # noqa: E704
def log(filename: str) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


@overload  # noqa: E704
def log() -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def log(filename: str | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Декоратор для логирования выполнения функции.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            args_repr = str(args)
            kwargs_repr = str(kwargs)
            msg: str

            try:
                result: R = func(*args, **kwargs)
                msg = f"{func.__name__} ok\n"
            except Exception as e:
                # Формируем сообщение об ошибке
                msg = f"{func.__name__} error: {type(e).__name__}. " f"Inputs: {args_repr}, {kwargs_repr}\n"
                # ЗАПИСЫВАЕМ ЛОГ ПЕРЕД ПРОБРОСОМ ИСКЛЮЧЕНИЯ
                if filename:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(msg)
                else:
                    print(msg.rstrip())
                raise  # Пробрасываем исключение после лога

            # Запись для успешного выполнения
            if filename:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(msg)
            else:
                print(msg.rstrip())

            return result

        return wrapper

    return decorator
