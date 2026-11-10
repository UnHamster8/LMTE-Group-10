"""Scan Pebble source one character at a time without external packages."""

from pebble.errors import LexicalError
from pebble.tokens import KEYWORDS, Token, TokenKind


SINGLE_CHAR_TOKENS = {
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.STAR,
    "/": TokenKind.SLASH,
    "=": TokenKind.ASSIGN,
    "<": TokenKind.LESS,
    ">": TokenKind.GREATER,
    "(": TokenKind.LEFT_PAREN,
    ")": TokenKind.RIGHT_PAREN,
    ",": TokenKind.COMMA,
    ";": TokenKind.SEMICOLON,
}

TWO_CHAR_TOKENS = {
    "==": TokenKind.EQUAL,
    "!=": TokenKind.NOT_EQUAL,
    "<=": TokenKind.LESS_EQUAL,
    ">=": TokenKind.GREATER_EQUAL,
}


def _is_letter(character: str) -> bool:
    # Pebble names use ASCII letters rather than all Unicode letters.
    return "a" <= character <= "z" or "A" <= character <= "Z"


def _is_digit(character: str) -> bool:
    return "0" <= character <= "9"


class Lexer:
    def __init__(self, source: str) -> None:
        # Normalise line endings so positions work across operating systems.
        self.source = source.replace("\r\n", "\n").replace("\r", "\n")
        self._index = 0
        self._line = 1
        self._column = 1

    def tokenize(self) -> list[Token]:
        """Return the token stream, including a final EOF token."""
        self._index = 0
        self._line = 1
        self._column = 1
        tokens: list[Token] = []

        while self._index < len(self.source):
            character = self._peek()

            if character in (" ", "\t", "\n"):
                self._advance()
                continue

            # Check comments before treating '/' as division.
            if character == "/" and self._peek(1) == "/":
                while self._peek() not in ("", "\n"):
                    self._advance()
                continue

            start = self._index
            line, column = self._line, self._column

            if _is_letter(character):
                self._advance()
                while (
                    _is_letter(self._peek())
                    or _is_digit(self._peek())
                    or self._peek() == "_"
                ):
                    self._advance()
                lexeme = self.source[start:self._index]
                kind = KEYWORDS.get(lexeme, TokenKind.NAME)
                value: int | bool | str | None = None
                if kind == TokenKind.NAME:
                    value = lexeme
                elif kind in (TokenKind.TRUE, TokenKind.FALSE):
                    value = kind == TokenKind.TRUE
                tokens.append(Token(kind, lexeme, value, line, column))
                continue

            if _is_digit(character):
                while _is_digit(self._peek()):
                    self._advance()
                lexeme = self.source[start:self._index]
                tokens.append(Token(TokenKind.INT, lexeme, int(lexeme), line, column))
                continue

            # Prefer the longest operator, e.g. '==' before '='.
            pair = character + self._peek(1)
            if pair in TWO_CHAR_TOKENS:
                self._advance()
                self._advance()
                tokens.append(Token(TWO_CHAR_TOKENS[pair], pair, None, line, column))
                continue

            if character in SINGLE_CHAR_TOKENS:
                self._advance()
                tokens.append(
                    Token(SINGLE_CHAR_TOKENS[character], character, None, line, column)
                )
                continue

            raise LexicalError(f"Unexpected character {character!r}", line, column)

        tokens.append(Token(TokenKind.EOF, "", None, self._line, self._column))
        return tokens

    def _peek(self, offset: int = 0) -> str:
        index = self._index + offset
        return self.source[index] if index < len(self.source) else ""

    def _advance(self) -> None:
        character = self.source[self._index]
        self._index += 1
        if character == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1
