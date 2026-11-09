# Pebble — Group 10

A Python 3 interpreter project for the Pebble language. This starter implements
the lexical analysis stage from the group design plan.

**Current status:** source files can be converted into tokens. Parsing, semantic
validation and execution are still to be implemented, so `say` does not print
program results yet.

## Requirements and running

Use Python 3.10 or later on Windows, macOS or Linux. No third-party packages or
compilation steps are required. Run these commands from the project directory:

```sh
python3 main.py examples/basic.peb
python3 main.py examples/control_flow.peb
python3 main.py examples/functions.peb
python3 -m unittest discover -s tests -v
```

On Windows, use `py -3` instead of `python3` if needed. Source files use UTF-8.
The command prints each token's line, column, kind, original text and optional
value. An invalid character prints a lexical error to stderr and exits with
status 1. File-reading failures also exit with status 1.

## Project structure

```text
main.py                   Read a file and display its tokens
pebble/
    tokens.py             Token kinds, keyword lookup and Token data class
    lexer.py              Hand-written finite-state scanner
    errors.py             Shared error format and lexical errors
    parser.py             Parser interface for the next stage (placeholder)
    evaluator.py          Evaluation interface for a later stage (placeholder)
examples/                 Sample Pebble source files
tests/test_lexer.py       Lexical rules, source positions and error tests
```

## Lexical specification

- Keywords are case-sensitive and lowercase: `let`, `say`, `if`, `else`, `while`,
  `do`, `end`, `func`, `return`, `true`, `false`.
- Names match `[A-Za-z][A-Za-z0-9_]*`. For example, `score_2` is a name, while
  `_score` is invalid. `Let` is a name rather than the keyword `let`.
- Integer literals contain ASCII decimal digits only. A negative number is a
  `MINUS` token followed by an `INT` token; unary minus belongs to the parser.
- Operators are `+ - * / = == != < <= > >=`. Two-character operators take
  priority over one-character operators.
- Separators are `(`, `)`, `,`, and `;`. Simple statements end in `;`, while
  compound blocks use `do` and `end`.
- `//` starts a comment extending to the end of the line. Whitespace and comments
  do not produce tokens. `/` by itself is the division operator.
- Strings, floating-point literals and non-ASCII names are not supported.
- Positions start at line 1, column 1 and refer to the beginning of a token.
  Tabs count as one column. LF, CRLF and CR line endings are accepted.
- Every successful scan ends with one `EOF` token at the end-of-input position.
  Unexpected characters stop scanning and report their line and column.

## Interface for the parser

```python
from pebble.lexer import Lexer
from pebble.tokens import TokenKind

tokens = Lexer("let value = 12; // note").tokenize()
assert [token.kind for token in tokens] == [
    TokenKind.LET, TokenKind.NAME, TokenKind.ASSIGN,
    TokenKind.INT, TokenKind.SEMICOLON, TokenKind.EOF,
]
```

`Token` is immutable and contains `kind`, `lexeme`, `value`, `line`, and `column`.
`lexeme` preserves the token's original spelling. `value` is a Python `int` for
integer literals, a `bool` for `true`/`false`, a `str` for names, and `None` for
other tokens. The lexer only checks lexical rules: undefined names, missing
semicolons, operand types and `return` placement belong to later stages.

The remaining pipeline is:

```text
source → Lexer → tokens → Parser → AST → validation → Evaluator → output
```

`Parser(tokens).parse()` and `Evaluator().evaluate(program)` deliberately raise
`NotImplementedError` until those components are written. The parser author
should define the AST node classes and replace the temporary `Any` annotations
in these interfaces. Add semantic validation before connecting evaluation to
`main.py`.

## Planned execution rules

The following rules come from the design plan and are **not implemented yet**:

- `let` creates or reassigns a variable; reading an unassigned name is an error.
- Expressions follow call/parentheses, unary minus, multiplication/division,
  addition/subtraction, ordering, then equality precedence. Binary operators
  associate left; chained ordering expressions are rejected.
- Arithmetic and ordering need integers; equality needs matching types. Integer
  division truncates towards zero. Conditions need Booleans.
- `say` prints one value per line, with Booleans written as `true` or `false`.
- `if` optionally has `else`; `while` may execute zero times.
- Functions are top-level definitions preceding their use. Calls read locals
  before globals, and local assignments do not modify globals. Nested functions,
  duplicate parameter names and `return` outside functions are rejected.
- Undefined names/functions, division by zero, wrong argument counts, invalid
  types and functions finishing without returning a value produce errors.

The examples are input for lexical inspection now and future parser/evaluator
integration. Their comments describe the output expected after execution is
implemented.
