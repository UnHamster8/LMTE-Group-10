"""Parser interface to be completed by the parser/AST author."""

from typing import Any

from pebble.tokens import Token


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Any:
        # TODO: Define AST nodes and implement recursive-descent parsing.
        raise NotImplementedError("The parser has not been implemented yet.")
