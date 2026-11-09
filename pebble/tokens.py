"""The shared token interface used by the lexer and parser."""

from dataclasses import dataclass
from enum import Enum, auto


class TokenKind(Enum):
    # Literals and names.
    NAME = auto()
    INT = auto()

    # Reserved words.
    LET = auto()
    SAY = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    END = auto()
    FUNC = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()

    # Operators and separators.
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    COMMA = auto()
    SEMICOLON = auto()
    EOF = auto()


KEYWORDS = {
    "let": TokenKind.LET,
    "say": TokenKind.SAY,
    "if": TokenKind.IF,
    "else": TokenKind.ELSE,
    "while": TokenKind.WHILE,
    "do": TokenKind.DO,
    "end": TokenKind.END,
    "func": TokenKind.FUNC,
    "return": TokenKind.RETURN,
    "true": TokenKind.TRUE,
    "false": TokenKind.FALSE,
}


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    lexeme: str
    value: int | bool | str | None
    line: int
    column: int

    def __str__(self) -> str:
        value_text = f" value={self.value!r}" if self.value is not None else ""
        return (
            f"{self.line}:{self.column} {self.kind.name} "
            f"{self.lexeme!r}{value_text}"
        )
