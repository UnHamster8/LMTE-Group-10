"""Regression tests for the lexical rules in the Pebble design plan."""

import unittest

from pebble.errors import LexicalError
from pebble.lexer import Lexer
from pebble.tokens import TokenKind


class LexerTests(unittest.TestCase):
    def kinds(self, source: str) -> list[TokenKind]:
        return [token.kind for token in Lexer(source).tokenize()]

    def test_assignment_from_design_plan(self) -> None:
        tokens = Lexer("let value = 12; // note").tokenize()
        self.assertEqual(
            [token.kind for token in tokens],
            [TokenKind.LET, TokenKind.NAME, TokenKind.ASSIGN,
             TokenKind.INT, TokenKind.SEMICOLON, TokenKind.EOF],
        )
        self.assertEqual(tokens[1].value, "value")
        self.assertEqual(tokens[3].value, 12)

    def test_all_reserved_words(self) -> None:
        self.assertEqual(
            self.kinds("let say if else while do end func return true false"),
            [TokenKind.LET, TokenKind.SAY, TokenKind.IF, TokenKind.ELSE,
             TokenKind.WHILE, TokenKind.DO, TokenKind.END, TokenKind.FUNC,
             TokenKind.RETURN, TokenKind.TRUE, TokenKind.FALSE, TokenKind.EOF],
        )

    def test_keyword_prefixes_and_case_are_names(self) -> None:
        tokens = Lexer("letter say2 true_value Let TRUE").tokenize()
        self.assertTrue(all(token.kind == TokenKind.NAME for token in tokens[:-1]))
        self.assertEqual(
            [token.value for token in tokens[:-1]],
            ["letter", "say2", "true_value", "Let", "TRUE"],
        )

    def test_boolean_values(self) -> None:
        tokens = Lexer("true false").tokenize()
        self.assertIs(tokens[0].value, True)
        self.assertIs(tokens[1].value, False)

    def test_all_operators_and_separators(self) -> None:
        self.assertEqual(
            self.kinds("+ - * / = == != < <= > >= ( ) , ;"),
            [TokenKind.PLUS, TokenKind.MINUS, TokenKind.STAR, TokenKind.SLASH,
             TokenKind.ASSIGN, TokenKind.EQUAL, TokenKind.NOT_EQUAL,
             TokenKind.LESS, TokenKind.LESS_EQUAL, TokenKind.GREATER,
             TokenKind.GREATER_EQUAL, TokenKind.LEFT_PAREN,
             TokenKind.RIGHT_PAREN, TokenKind.COMMA, TokenKind.SEMICOLON,
             TokenKind.EOF],
        )

    def test_adjacent_operators_use_longest_match(self) -> None:
        self.assertEqual(
            self.kinds("a==b!=c<=d>=e=f/g"),
            [TokenKind.NAME, TokenKind.EQUAL, TokenKind.NAME, TokenKind.NOT_EQUAL,
             TokenKind.NAME, TokenKind.LESS_EQUAL, TokenKind.NAME,
             TokenKind.GREATER_EQUAL, TokenKind.NAME, TokenKind.ASSIGN,
             TokenKind.NAME, TokenKind.SLASH, TokenKind.NAME, TokenKind.EOF],
        )

    def test_minus_is_separate_from_integer(self) -> None:
        tokens = Lexer("-12").tokenize()
        self.assertEqual(
            [token.kind for token in tokens],
            [TokenKind.MINUS, TokenKind.INT, TokenKind.EOF],
        )
        self.assertEqual(tokens[1].value, 12)

    def test_integer_preserves_original_spelling(self) -> None:
        token = Lexer("0012").tokenize()[0]
        self.assertEqual(token.lexeme, "0012")
        self.assertEqual(token.value, 12)

    def test_division_and_comment_are_distinct(self) -> None:
        self.assertEqual(
            self.kinds("say 8/2;// @ and != are ignored\nsay 1;"),
            [TokenKind.SAY, TokenKind.INT, TokenKind.SLASH, TokenKind.INT,
             TokenKind.SEMICOLON, TokenKind.SAY, TokenKind.INT,
             TokenKind.SEMICOLON, TokenKind.EOF],
        )

    def test_comment_at_end_of_file(self) -> None:
        token = Lexer("// note").tokenize()[0]
        self.assertEqual(token.kind, TokenKind.EOF)
        self.assertEqual((token.line, token.column), (1, 8))

    def test_empty_source(self) -> None:
        tokens = Lexer("").tokenize()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].kind, TokenKind.EOF)
        self.assertEqual((tokens[0].line, tokens[0].column), (1, 1))

    def test_positions_after_whitespace_and_comment(self) -> None:
        tokens = Lexer("let x = 12;\n// note\n  say x;").tokenize()
        self.assertEqual(
            [(token.line, token.column) for token in tokens],
            [(1, 1), (1, 5), (1, 7), (1, 9), (1, 11),
             (3, 3), (3, 7), (3, 8), (3, 9)],
        )

    def test_line_endings_and_tabs(self) -> None:
        for newline in ("\n", "\r\n", "\r"):
            with self.subTest(newline=repr(newline)):
                tokens = Lexer(f"// comment{newline}\tsay 1;{newline}").tokenize()
                self.assertEqual((tokens[0].line, tokens[0].column), (2, 2))
                self.assertEqual((tokens[-1].line, tokens[-1].column), (3, 1))

    def test_invalid_characters_report_exact_position(self) -> None:
        for character in ("@", "!", "_", '"', ".", "é", "１", "\x00"):
            with self.subTest(character=repr(character)):
                with self.assertRaises(LexicalError) as context:
                    Lexer(f"say 1;\n  {character}").tokenize()
                error = context.exception
                self.assertEqual((error.line, error.column), (2, 3))
                self.assertIn(repr(character), error.message)
                self.assertIn("Lexical error at 2:3", str(error))

    def test_floating_point_literal_is_rejected(self) -> None:
        with self.assertRaises(LexicalError) as context:
            Lexer("say 1.5;").tokenize()
        self.assertEqual((context.exception.line, context.exception.column), (1, 6))

    def test_function_syntax_can_be_tokenized(self) -> None:
        self.assertEqual(
            self.kinds("func twice(x) do return x * 2; end say twice(6);"),
            [TokenKind.FUNC, TokenKind.NAME, TokenKind.LEFT_PAREN, TokenKind.NAME,
             TokenKind.RIGHT_PAREN, TokenKind.DO, TokenKind.RETURN, TokenKind.NAME,
             TokenKind.STAR, TokenKind.INT, TokenKind.SEMICOLON, TokenKind.END,
             TokenKind.SAY, TokenKind.NAME, TokenKind.LEFT_PAREN, TokenKind.INT,
             TokenKind.RIGHT_PAREN, TokenKind.SEMICOLON, TokenKind.EOF],
        )


if __name__ == "__main__":
    unittest.main()
