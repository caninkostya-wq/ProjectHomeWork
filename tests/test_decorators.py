import pytest

from src.decorators import log


class TestLogDecorator:
    """Тестирование декоратора log."""

    def test_log_console_success(self, capsys):
        """Тест: успешный вызов → вывод в консоль."""

        @log()
        def add(a, b):
            return a + b

        result = add(2, 3)
        assert result == 5

        captured = capsys.readouterr()
        assert "add ok" in captured.out

    def test_log_console_exception(self, capsys):
        """Тест: исключение → лог в консоль + проброс исключения."""

        @log()
        def divide(x, y):
            return x / y

        with pytest.raises(ZeroDivisionError):
            divide(1, 0)

        captured = capsys.readouterr()
        assert "divide error: ZeroDivisionError. Inputs: (1, 0), {}" in captured.out

    def test_log_file_success(self, tmp_path):
        """Тест: успешный вызов → запись в файл."""
        log_file = tmp_path / "test.log"

        @log(str(log_file))
        def multiply(a, b):
            return a * b

        multiply(4, 5)

        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "multiply ok" in content

    def test_log_file_exception(self, tmp_path):
        """Тест: исключение → запись в файл + проброс."""
        log_file = tmp_path / "error.log"

        @log(str(log_file))
        def bad_func():
            raise ValueError("Invalid value")

        with pytest.raises(ValueError, match="Invalid value"):
            bad_func()

        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "bad_func error: ValueError. Inputs: (), {}" in content

    def test_log_no_args(self, capsys):
        """Тест: функция без аргументов."""

        @log()
        def say_hi():
            return "Hi!"

        say_hi()
        captured = capsys.readouterr()
        assert "say_hi ok" in captured.out

    def test_log_with_kwargs(self, capsys):
        """Тест: вызов с именованными аргументами."""

        @log()
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        greet("Alice", greeting="Hi")
        captured = capsys.readouterr()
        # Проверяем, что kwargs попали в лог при ошибке (в успехе они не выводятся)
        # Для проверки передадим неверный аргумент, чтобы сработала ветка с ошибкой
        with pytest.raises(TypeError):
            greet("Bob", unknown="X")  # вызовет TypeError

        captured = capsys.readouterr()
        assert "greet error: TypeError. Inputs: ('Bob',), {'unknown': 'X'}" in captured.out

    def test_log_multiple_calls(self, capsys):
        """Тест: несколько вызовов → несколько записей в лог."""

        @log()
        def counter():
            return 42

        counter()
        counter()

        captured = capsys.readouterr()
        lines = [line.strip() for line in captured.out.splitlines() if line.strip()]
        assert len(lines) == 2
        assert all("counter ok" in line for line in lines)

    def test_log_filename_none(self, capsys):
        """Тест: filename=None → вывод в консоль (эквивалентно log())."""

        @log(None)
        def dummy():
            pass

        dummy()
        captured = capsys.readouterr()
        assert "dummy ok" in captured.out

    def test_log_empty_filename_string(self, capsys):
        """Тест: filename='' → вывод в консоль (как None)."""

        @log("")
        def empty_name():
            pass

        empty_name()
        captured = capsys.readouterr()
        assert "empty_name ok" in captured.out

    def test_log_preserve_function_metadata(self):
        """Тест: functools.wraps сохраняет метаданные функции."""

        @log()
        def original():
            """Docstring оригинальной функции."""
            pass

        assert original.__name__ == "original"
        assert original.__doc__ == "Docstring оригинальной функции."
        assert original.__module__ == "tests.test_decorators"
