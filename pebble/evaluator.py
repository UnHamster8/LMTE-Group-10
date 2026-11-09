"""Evaluation interface to be completed by the evaluator author."""

from typing import Any


class Evaluator:
    def evaluate(self, program: Any) -> None:
        # TODO: Walk the validated AST and execute Pebble statements.
        raise NotImplementedError("The evaluator has not been implemented yet.")
