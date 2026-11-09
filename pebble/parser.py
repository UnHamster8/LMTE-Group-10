"""Recursive-descent parser for the Pebble grammar."""

from collections.abc import Callable
from typing import cast

from pebble import ast_nodes as ast
from pebble.errors import ParseError
from pebble.tokens import Token, TokenKind


_ORDERING_OPERATORS = (
    TokenKind.LESS,
    TokenKind.LESS_EQUAL,
    TokenKind.GREATER,
    TokenKind.GREATER_EQUAL,
)


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        # This points to the next token we need to read.
        self.current = 0

    def parse(self) -> ast.Program:
        """Parse all tokens from the lexer and return the program AST."""
        self.current = 0
        items: list[ast.Statement] = []
        # The lexer adds EOF so we know when the source ends.
        while self._peek().kind != TokenKind.EOF:
            items.append(self._statement())
        return ast.Program(tuple(items))

    def _peek(self) -> Token:
        # Looking at a token leaves it there for the next step.
        return self.tokens[self.current]

    def _match(self, *kinds: TokenKind) -> Token | None:
        # Move forward only if the current token matches.
        token = self._peek()
        if token.kind in kinds:
            self.current += 1
            return token
        return None

    def _expect(self, kind: TokenKind, description: str) -> Token:
        # Use this for a required token, like the ';' after a statement.
        token = self._match(kind)
        if token is None:
            raise self._expected(description)
        return token

    def _expected(self, description: str) -> ParseError:
        token = self._peek()
        # Report the token we found where the missing piece should be.
        found = "end of input" if token.kind == TokenKind.EOF else repr(token.lexeme)
        return ParseError(
            f"Expected {description}, found {found}", token.line, token.column
        )

    def _name(self, description: str) -> ast.Name:
        token = self._expect(TokenKind.NAME, description)
        return ast.Name(token.lexeme, token.line, token.column)

    def _statement(self) -> ast.Statement:
        # Save the keyword's position for the statement node.
        start = self._peek()
        if self._match(TokenKind.LET):
            name = self._name("a variable name")
            self._expect(TokenKind.ASSIGN, "'=' after variable name")
            expression = self._expression()
            self._expect(TokenKind.SEMICOLON, "';' after assignment")
            return ast.LetStatement(name, expression, start.line, start.column)

        if self._match(TokenKind.SAY):
            expression = self._expression()
            self._expect(TokenKind.SEMICOLON, "';' after 'say' expression")
            return ast.SayStatement(expression, start.line, start.column)

        raise self._expected("a statement")

    def _expression(self) -> ast.Expression:
        # Group comparisons before checking == or !=.
        return self._binary(self._comparison, TokenKind.EQUAL, TokenKind.NOT_EQUAL)

    def _comparison(self) -> ast.Expression:
        left = self._sum()
        operator = self._match(*_ORDERING_OPERATORS)
        if operator is None:
            return left

        right = self._sum()
        following = self._peek()
        # Pebble allows a < b, but reports an error at the second < in a < b < c.
        if following.kind in _ORDERING_OPERATORS:
            raise ParseError(
                "Chained ordering comparisons are not allowed",
                following.line,
                following.column,
            )
        return ast.BinaryExpression(
            left, operator.kind, right, operator.line, operator.column
        )

    def _sum(self) -> ast.Expression:
        # Read products first so 2 * 3 stays together in 1 + 2 * 3.
        return self._binary(self._product, TokenKind.PLUS, TokenKind.MINUS)

    def _product(self) -> ast.Expression:
        return self._binary(self._unary, TokenKind.STAR, TokenKind.SLASH)

    def _binary(
        self, operand: Callable[[], ast.Expression], *operators: TokenKind
    ) -> ast.Expression:
        """Fold repeated operators at the same precedence level from the left."""
        left = operand()
        while (operator := self._match(*operators)) is not None:
            right = operand()
            # Use the tree so far as the left side, so 10 - 3 - 2 groups as (10 - 3) - 2.
            left = ast.BinaryExpression(
                left, operator.kind, right, operator.line, operator.column
            )
        return left

    def _unary(self) -> ast.Expression:
        # A minus here goes with one value, like the first minus in -3 - 2.
        operator = self._match(TokenKind.MINUS)
        if operator is not None:
            return ast.UnaryExpression(
                operator.kind, self._unary(), operator.line, operator.column
            )
        return self._primary()

    def _primary(self) -> ast.Expression:
        if (token := self._match(TokenKind.INT)) is not None:
            # The lexer attaches an integer value to every INT token.
            return ast.IntegerLiteral(cast(int, token.value), token.line, token.column)

        if (token := self._match(TokenKind.TRUE, TokenKind.FALSE)) is not None:
            return ast.BooleanLiteral(
                token.kind == TokenKind.TRUE, token.line, token.column
            )

        if self._match(TokenKind.LEFT_PAREN):
            # Start a new expression inside the parentheses.
            expression = self._expression()
            self._expect(TokenKind.RIGHT_PAREN, "')' after expression")
            return expression

        if (token := self._match(TokenKind.NAME)) is not None:
            return ast.Name(token.lexeme, token.line, token.column)

        raise self._expected("an expression")
