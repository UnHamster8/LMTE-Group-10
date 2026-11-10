"""Errors include a category and a one-based source position."""


class PebbleError(Exception):
    category = "Pebble error"

    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"{self.category} at {self.line}:{self.column}: {self.message}"


class LexicalError(PebbleError):
    category = "Lexical error"


class ParseError(PebbleError):
    category = "Syntax error"


class ValidationError(PebbleError):
    category = "Validation error"


class EvaluationError(PebbleError):
    category = "Runtime error"