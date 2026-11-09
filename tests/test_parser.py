"""Test syntax and AST structure using real Pebble lexer output."""

from pathlib import Path
import unittest

from pebble import ast_nodes as ast
from pebble.errors import ParseError
from pebble.lexer import Lexer
from pebble.parser import Parser
from pebble.tokens import TokenKind


def parse(source: str) -> ast.Program:
    # Run the source through the lexer before testing the parser.
    return Parser(Lexer(source).tokenize()).parse()


class ParserTests(unittest.TestCase):
    def test_empty_source(self):
        self.assertEqual(parse("// just a comment"), ast.Program(()))

    def test_let_records_name_value_and_source_positions(self):
        # The comment takes up the first line, so 'let' starts on line 2.
        self.assertEqual(
            parse("// note\nlet score = 10;"),
            ast.Program(
                (
                    ast.LetStatement(
                        ast.Name("score", 2, 5), ast.IntegerLiteral(10, 2, 13), 2, 1
                    ),
                )
            ),
        )

    def test_operator_precedence(self):
        statement, = parse("say 1 + 2 * 3 < 8 == true;").items
        # Start at '==' and check how the other operators fit inside it.
        equality = statement.expression
        self.assertEqual(equality.operator, TokenKind.EQUAL)
        self.assertEqual(equality.right, ast.BooleanLiteral(True, 1, 22))
        comparison = equality.left
        self.assertEqual(comparison.operator, TokenKind.LESS)
        addition = comparison.left
        self.assertEqual(addition.operator, TokenKind.PLUS)
        self.assertEqual(addition.right.operator, TokenKind.STAR)

    def test_parentheses_and_unary_minus(self):
        statement, = parse("say -(2 + 3) * --4;").items
        product = statement.expression
        self.assertEqual(product.operator, TokenKind.STAR)
        self.assertEqual(product.left.operator, TokenKind.MINUS)
        self.assertEqual(product.left.operand.operator, TokenKind.PLUS)
        self.assertEqual(product.right.operator, TokenKind.MINUS)
        self.assertEqual(product.right.operand.operator, TokenKind.MINUS)

    def test_repeated_binary_operators_associate_left(self):
        for source, kind in (
            ("say 10 - 3 - 2;", TokenKind.MINUS),
            ("say 8 / 4 / 2;", TokenKind.SLASH),
            ("say true == false != true;", TokenKind.EQUAL),
        ):
            with self.subTest(source=source):
                statement, = parse(source).items
                expression = statement.expression
                # The first operation should be on the left side of the next one.
                self.assertIsInstance(expression.left, ast.BinaryExpression)
                self.assertEqual(expression.left.operator, kind)
                self.assertNotIsInstance(expression.right, ast.BinaryExpression)

    def test_basic_example_parses(self):
        example = Path(__file__).resolve().parents[1] / "examples" / "basic.peb"
        program = parse(example.read_text(encoding="utf-8"))
        self.assertEqual(len(program.items), 7)
        self.assertIsInstance(program.items[0], ast.LetStatement)
        self.assertIsInstance(program.items[-1], ast.SayStatement)

    def test_syntax_errors_have_reason_and_location(self):
        # Each case gives the source, part of the error message, and its location.
        cases = (
            ("let x = ;", "an expression", 1, 9),
            ("say 1", "';' after 'say' expression", 1, 6),
            ("say (1 + 2;", "')' after expression", 1, 11),
            ("say 1 < 2 < 3;", "Chained ordering comparisons", 1, 11),
            ("say 1; end", "a statement", 1, 8),
        )
        for source, message, line, column in cases:
            with self.subTest(source=source):
                with self.assertRaises(ParseError) as raised:
                    parse(source)
                self.assertIn(message, raised.exception.message)
                self.assertEqual(
                    (raised.exception.line, raised.exception.column), (line, column)
                )
                self.assertTrue(
                    str(raised.exception).startswith(f"Syntax error at {line}:{column}: ")
                )
