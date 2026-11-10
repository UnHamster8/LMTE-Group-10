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


@dataclass(frozen=True)
class Call:
    callee: Name
    arguments: tuple[Expression, ...]
    line: int
    column: int


# Any of these nodes can be used where an expression is expected.
Expression: TypeAlias = (
    IntegerLiteral
    | BooleanLiteral
    | Name
    | UnaryExpression
    | BinaryExpression
    | Call
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


@dataclass(frozen=True)
class ReturnStatement:
    expression: Expression
    line: int
    column: int


@dataclass(frozen=True)
class IfStatement:
    condition: Expression
    then_body: tuple[Statement, ...]
    # None means the source did not have an 'else' block.
    else_body: tuple[Statement, ...] | None
    line: int
    column: int


@dataclass(frozen=True)
class WhileStatement:
    condition: Expression
    body: tuple[Statement, ...]
    line: int
    column: int


Statement: TypeAlias = (
    LetStatement | SayStatement | ReturnStatement | IfStatement | WhileStatement
)


@dataclass(frozen=True)
class FunctionDefinition:
    name: Name
    parameters: tuple[Name, ...]
    body: tuple[Statement, ...]
    line: int
    column: int


@dataclass(frozen=True)
class Program:
    # Keep statements and function definitions in source order.
    items: tuple[Statement | FunctionDefinition, ...]
