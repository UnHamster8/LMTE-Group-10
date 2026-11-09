"""Run a Pebble source file or display its tokens."""

import argparse
from pathlib import Path
import sys

from pebble.errors import PebbleError
from pebble.evaluator import Evaluator
from pebble.lexer import Lexer
from pebble.parser import Parser


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Pebble source file.")
    parser.add_argument("source", type=Path, help="Path to a UTF-8 Pebble source file")
    parser.add_argument("--tokens", action="store_true", help="Only display lexer output")
    args = parser.parse_args()

    try:
        source = args.source.read_text(encoding="utf-8")
        tokens = Lexer(source).tokenize()
        if args.tokens:
            for token in tokens:
                print(token)
        else:
            # Execute the AST produced by the existing lexer and parser.
            Evaluator().evaluate(Parser(tokens).parse())
    except (OSError, UnicodeError) as error:
        print(f"Cannot read {args.source}: {error}", file=sys.stderr)
        return 1
    except PebbleError as error:
        print(f"{args.source}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())