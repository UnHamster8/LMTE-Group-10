"""Pebble syntax nodes shared by parsing, validation and evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from pebble.tokens import TokenKind


@dataclass(frozen=True)
class IntegerLiteral:
    value: int
    line: int
    column: int


@dataclass(frozen=True)
class BooleanLiteral:
    value: bool
    line: int
    column: int


@dataclass(frozen=True)
class Name:
    value: str
    line: int
    column: int


@dataclass(frozen=True)
class UnaryExpression:
    # A unary operator has one input, like the 3 in -3.
    operator: TokenKind
    operand: Expression
    line: int
    column: int


@dataclass(frozen=True)
class BinaryExpression:
    left: Expression
    operator: TokenKind
    right: Expression
    # Keep the operator's position so errors can point to it.
    line: int
    column: int


# Any of these nodes can be used where an expression is expected.
Expression: TypeAlias = (
    IntegerLiteral | BooleanLiteral | Name | UnaryExpression | BinaryExpression
)


@dataclass(frozen=True)
class LetStatement:
    # Keep the variable name and the expression after '=' separately.
    name: Name
    expression: Expression
    line: int
    column: int


@dataclass(frozen=True)
class SayStatement:
    expression: Expression
    line: int
    column: int


Statement: TypeAlias = LetStatement | SayStatement


@dataclass(frozen=True)
class Program:
    # Keep the statements in the order they appear in the source.
    items: tuple[Statement, ...]
