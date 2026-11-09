"""Validate and execute Pebble programs using the parser's AST."""

from operator import add, ge, gt, le, lt, mul, sub

from pebble import ast_nodes as ast
from pebble.errors import EvaluationError, ValidationError
from pebble.tokens import TokenKind


_INTEGER_OPERATORS = {
    TokenKind.PLUS: add,
    TokenKind.MINUS: sub,
    TokenKind.STAR: mul,
    TokenKind.LESS: lt,
    TokenKind.LESS_EQUAL: le,
    TokenKind.GREATER: gt,
    TokenKind.GREATER_EQUAL: ge,
}


class _ReturnValue(Exception):
    """Carry a return value out of nested blocks to the current call."""

    def __init__(self, value: int | bool) -> None:
        self.value = value


def _validate_top_level(statement: ast.Statement) -> None:
    # Check every top-level branch, even when its condition is false.
    if isinstance(statement, ast.ReturnStatement):
        raise ValidationError(
            "'return' is only allowed inside a function",
            statement.line,
            statement.column,
        )
    if isinstance(statement, ast.IfStatement):
        for child in (*statement.then_body, *(statement.else_body or ())):
            _validate_top_level(child)
    elif isinstance(statement, ast.WhileStatement):
        for child in statement.body:
            _validate_top_level(child)


def _validate(program: ast.Program) -> None:
    for item in program.items:
        if isinstance(item, ast.FunctionDefinition):
            seen: set[str] = set()
            for parameter in item.parameters:
                if parameter.value in seen:
                    raise ValidationError(
                        f"Duplicate parameter '{parameter.value}'",
                        parameter.line,
                        parameter.column,
                    )
                seen.add(parameter.value)
        else:
            _validate_top_level(item)


class Evaluator:
    def evaluate(self, program: ast.Program) -> None:
        """Validate the entire AST before running any statements."""
        _validate(program)
        self._globals: dict[str, int | bool] = {}
        self._functions: dict[str, ast.FunctionDefinition] = {}

        # Register each definition when execution reaches it.
        for item in program.items:
            if isinstance(item, ast.FunctionDefinition):
                self._functions[item.name.value] = item
            else:
                self._execute(item, self._globals)

    def _block(
        self, statements: tuple[ast.Statement, ...], scope: dict[str, int | bool]
    ) -> None:
        for statement in statements:
            self._execute(statement, scope)

    def _execute(self, statement: ast.Statement, scope: dict[str, int | bool]) -> None:
        if isinstance(statement, ast.LetStatement):
            # Evaluate the right side before assigning or reassigning the name.
            scope[statement.name.value] = self._value(statement.expression, scope)
        elif isinstance(statement, ast.SayStatement):
            value = self._value(statement.expression, scope)
            print(str(value).lower())
        elif isinstance(statement, ast.IfStatement):
            if self._condition(statement.condition, scope):
                self._block(statement.then_body, scope)
            elif statement.else_body is not None:
                self._block(statement.else_body, scope)
        elif isinstance(statement, ast.WhileStatement):
            # Re-evaluate the condition after every iteration.
            while self._condition(statement.condition, scope):
                self._block(statement.body, scope)
        elif isinstance(statement, ast.ReturnStatement):
            raise _ReturnValue(self._value(statement.expression, scope))

    def _condition(self, expression: ast.Expression, scope: dict[str, int | bool]) -> bool:
        value = self._value(expression, scope)
        if not isinstance(value, bool):
            raise EvaluationError(
                "Condition must be Boolean", expression.line, expression.column
            )
        return value

    def _value(self, expression: ast.Expression, scope: dict[str, int | bool]) -> int | bool:
        if isinstance(expression, (ast.IntegerLiteral, ast.BooleanLiteral)):
            return expression.value
        if isinstance(expression, ast.Name):
            if expression.value in scope:
                return scope[expression.value]
            if expression.value in self._globals:
                return self._globals[expression.value]
            raise EvaluationError(
                f"Undefined variable '{expression.value}'",
                expression.line,
                expression.column,
            )
        if isinstance(expression, ast.UnaryExpression):
            operand = self._value(expression.operand, scope)
            if type(operand) is not int:
                raise EvaluationError(
                    "Unary '-' requires an integer operand",
                    expression.line,
                    expression.column,
                )
            return -operand
        if isinstance(expression, ast.BinaryExpression):
            return self._binary(expression, scope)
        return self._call(expression, scope)

    def _binary(
        self, expression: ast.BinaryExpression, scope: dict[str, int | bool]
    ) -> int | bool:
        left = self._value(expression.left, scope)
        right = self._value(expression.right, scope)
        kind = expression.operator
        line, column = expression.line, expression.column

        if kind in (TokenKind.EQUAL, TokenKind.NOT_EQUAL):
            if type(left) is not type(right):
                raise EvaluationError("Equality requires matching types", line, column)
            return left == right if kind == TokenKind.EQUAL else left != right

        # Python treats bool as a subclass of int, so check the exact types.
        if type(left) is not int or type(right) is not int:
            raise EvaluationError("Operator requires integer operands", line, column)
        if kind == TokenKind.SLASH:
            if right == 0:
                raise EvaluationError("Division by zero", line, column)
            # Use integer arithmetic to truncate towards zero without rounding.
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        return _INTEGER_OPERATORS[kind](left, right)

    def _call(self, call: ast.Call, scope: dict[str, int | bool]) -> int | bool:
        name = call.callee.value
        function = self._functions.get(name)
        if function is None:
            raise EvaluationError(f"Undefined function '{name}'", call.line, call.column)

        expected = len(function.parameters)
        actual = len(call.arguments)
        if expected != actual:
            raise EvaluationError(
                f"Function '{name}' expects {expected} argument(s), got {actual}",
                call.line,
                call.column,
            )

        # Evaluate arguments in the caller, then bind them in a fresh local scope.
        arguments = [self._value(argument, scope) for argument in call.arguments]
        local = {
            parameter.value: value
            for parameter, value in zip(function.parameters, arguments)
        }
        try:
            self._block(function.body, local)
        except _ReturnValue as result:
            return result.value

        raise EvaluationError(
            f"Function '{name}' finished without returning a value",
            call.line,
            call.column,
        )