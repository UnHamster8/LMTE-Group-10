"""Read a Pebble source file and display the lexer output."""

import argparse
from pathlib import Path
import sys

from pebble.errors import PebbleError
from pebble.lexer import Lexer


def main() -> int:
    parser = argparse.ArgumentParser(description="Display tokens from a Pebble file.")
    parser.add_argument("source", type=Path, help="Path to a UTF-8 Pebble source file")
    args = parser.parse_args()

    try:
        source = args.source.read_text(encoding="utf-8")
        tokens = Lexer(source).tokenize()
    except (OSError, UnicodeError) as error:
        print(f"Cannot read {args.source}: {error}", file=sys.stderr)
        return 1
    except PebbleError as error:
        print(f"{args.source}: {error}", file=sys.stderr)
        return 1

    # Later, pass these tokens to the parser and evaluate the resulting AST.
    for token in tokens:
        print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
