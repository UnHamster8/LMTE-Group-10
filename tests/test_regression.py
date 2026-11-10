"""Member D: regression scenarios based on Group 10's language specification."""
from contextlib import redirect_stdout
from io import StringIO
import unittest
from pebble.lexer import Lexer
from pebble.parser import Parser
from pebble.evaluator import Evaluator
from pebble.errors import PebbleError

def run_program(source):
    output = StringIO()
    with redirect_stdout(output):
        Evaluator().evaluate(Parser(Lexer(source).tokenize()).parse())
    return output.getvalue()

class RegressionTests(unittest.TestCase):
    def test_language_design_success_cases(self):
        cases = [
            ("say 1 + 2 * 3; say (1 + 2) * 3;", "7\n9\n"),
            ("let a = 4; let a = a + 1; say a;", "5\n"),
            ("if true do say 1; else say 2; end if false do say 3; else say 4; end", "1\n4\n"),
            ("let n = 3; while n > 0 do say n; let n = n - 1; end", "3\n2\n1\n"),
            ("while false do say 99; end", ""),
            ("func twice(x) do return x * 2; end say twice(6);", "12\n"),
            ("say 5 / 2; say -5 / 2;", "2\n-2\n"),
            ("say true; say false; say 4 >= 4; say 3 != 3;", "true\nfalse\ntrue\nfalse\n"),
            ("let x = 100; func f(x) do let x = x + 1; return x; end say f(5); say x;", "6\n100\n"),
            ("say 10 / -3; say -10 / 3; say -10 / -3;", "-3\n-3\n3\n"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(run_program(source), expected)

    def test_language_design_error_cases(self):
        cases = [
            ("say @;", "Lexical error"),
            ("let x = ;", "Syntax error"),
            ("say missing;", "Undefined variable"),
            ("say 1 / 0;", "Division by zero"),
            ("say true + 1;", "integer operands"),
            ("func f(x) do return x; end say f();", "expects 1 argument"),
            ("return 1;", "only allowed inside"),
            ("func f(a,a) do return a; end", "Duplicate parameter"),
            ("if 1 do say 1; end", "Condition must be Boolean"),
            ("func f() do say 1; end say f();", "without returning"),
        ]
        for source, fragment in cases:
            with self.subTest(source=source):
                with self.assertRaises(PebbleError) as caught:
                    run_program(source)
                self.assertIn(fragment, str(caught.exception))

    def test_prevalidation_prevents_earlier_output(self):
        with self.assertRaises(PebbleError):
            run_program("say 100; if false do return 1; end")

if __name__ == "__main__":
    unittest.main()
