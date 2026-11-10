"""Test Pebble validation and execution through the lexer and parser."""

from contextlib import redirect_stdout
from io import StringIO
import unittest

from pebble.errors import EvaluationError, ValidationError
from pebble.evaluator import Evaluator
from pebble.lexer import Lexer
from pebble.parser import Parser


def run_program(source: str, output: StringIO) -> None:
    program = Parser(Lexer(source).tokenize()).parse()
    with redirect_stdout(output):
        Evaluator().evaluate(program)


class EvaluatorTests(unittest.TestCase):
    def test_arithmetic_and_booleans(self) -> None:
        output = StringIO()
        run_program(
            "say 2 + 3 * 4; say (2 + 3) * 4; say -5 / 2; say 5 / -2; "
            "say 5 > 2; say true != false; say 3 == 4;",
            output,
        )
        self.assertEqual(output.getvalue(), "14\n20\n-2\n-2\ntrue\ntrue\nfalse\n")

    def test_loop_and_branches(self) -> None:
        output = StringIO()
        run_program(
            """
            let n = 3;
            while n > 0 do
                if n == 2 do say 20; else say n; end
                let n = n - 1;
            end
            while false do say 99; end
            """,
            output,
        )
        self.assertEqual(output.getvalue(), "3\n20\n1\n")

    def test_function_scope_and_nested_return(self) -> None:
        output = StringIO()
        run_program(
            """
            let x = 10;
            func adjust(amount) do
                let x = x + amount;
                while true do
                    if x > 10 do return x; end
                    say 99;
                    return 0;
                end
            end
            say adjust(2);
            say adjust(3);
            say x;
            """,
            output,
        )
        # Each call starts with a fresh scope, and the global x stays at 10.
        self.assertEqual(output.getvalue(), "12\n13\n10\n")

    def test_validation_errors_before_execution(self) -> None:
        cases = [
            ("say 1;\nif false do return 2; end", "2:13", "inside a function"),
            ("say 1;\nfunc f(x, x) do return x; end", "2:11", "Duplicate parameter"),
        ]
        for source, position, message in cases:
            with self.subTest(source=source):
                output = StringIO()
                with self.assertRaises(ValidationError) as caught:
                    run_program(source, output)
                self.assertIn(f"Validation error at {position}", str(caught.exception))
                self.assertIn(message, str(caught.exception))
                self.assertEqual(output.getvalue(), "")

    def test_runtime_errors(self) -> None:
        cases = [
            ("say unknown;", "1:5", "Undefined variable"),
            ("say 1 / 0;", "1:7", "Division by zero"),
            ("say true + 1;", "1:10", "integer operands"),
            ("say -false;", "1:5", "integer operand"),
            ("say true == 1;", "1:10", "matching types"),
            ("if 1 do say 1; end", "1:4", "must be Boolean"),
            ("while 0 do say 1; end", "1:7", "must be Boolean"),
            ("say f(); func f() do return 1; end", "1:5", "Undefined function"),
            ("func f(x) do return x; end\nsay f();", "2:5", "expects 1 argument"),
            ("func f() do end\nsay f();", "2:5", "without returning"),
        ]
        for source, position, message in cases:
            with self.subTest(source=source):
                with self.assertRaises(EvaluationError) as caught:
                    run_program(source, StringIO())
                self.assertIn(f"Runtime error at {position}", str(caught.exception))
                self.assertIn(message, str(caught.exception))


if __name__ == "__main__":
    unittest.main()