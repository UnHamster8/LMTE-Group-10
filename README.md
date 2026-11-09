# Pebble — Group 10

A Python 3 interpreter project for the Pebble language. The lexer and parser
are implemented.

**Current status:** the lexer and parser can build an AST for all three example
programs, including control flow and functions. The command-line entry point
prints tokens. Semantic validation and execution are planned.

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
    errors.py             Shared error format, lexical errors and syntax errors
    ast_nodes.py          AST nodes for expressions, statements and functions
    parser.py             Recursive-descent parser
    evaluator.py          Evaluation interface for a later stage (placeholder)
examples/                 Sample Pebble source files
tests/test_lexer.py       Lexical rules, source positions and error tests
tests/test_parser.py      Example programs, AST structure and syntax errors
tests/test_cli.py         Command-line token output and error tests
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

`Parser(tokens).parse()` returns an `ast_nodes.Program`. Its `items` hold
statements and top-level function definitions in source order. The parser
handles `if` with an optional `else`, `while`, function definitions, calls
and `return`. A syntax error raises `ParseError` with a reason, line and
column. The semantic stage checks where `return` can appear.

Expressions follow calls and parentheses, unary minus, multiplication and
division, addition and subtraction, ordering comparisons, then equality.
Binary operators associate left. Ordering comparisons cannot be chained.

## AST handoff

Start a Python session from the project directory and run this code to
inspect the tree for a sample program.

```python
from pathlib import Path

from pebble.lexer import Lexer
from pebble.parser import Parser

source = Path("examples/functions.peb").read_text(encoding="utf-8")
program = Parser(Lexer(source).tokenize()).parse()
print(program)
```

The printed program starts with a `FunctionDefinition` for `twice`, followed by a
`SayStatement` whose expression is a `Call`. The main fields for validation and
evaluation are:

| AST node | Fields to read |
| --- | --- |
| `Program` | `items` contains statements and function definitions in source order. |
| `IntegerLiteral`, `BooleanLiteral`, `Name` | `value` is an integer, Boolean, or name string. |
| `UnaryExpression`, `BinaryExpression` | `operator` is a `TokenKind`. The child expressions are `operand` or `left` and `right`. |
| `LetStatement` | `name.value` is the variable name. `expression` is the right side of the assignment. |
| `SayStatement`, `ReturnStatement` | `expression` is the value to evaluate. |
| `IfStatement` | `condition`, `then_body`, and `else_body`. An omitted `else` is `None`. An empty `else` is `()`. |
| `WhileStatement` | `condition` and `body`. |
| `FunctionDefinition` | `name.value`, `parameters` as `Name` nodes, and `body`. |
| `Call` | `callee.value` is the function name. `arguments` holds the expression nodes in call order. |

Bodies, parameters, arguments and top-level items are tuples. Each statement,
expression and function definition has a one-based `line` and `column`. For an
operation these point to the operator. Parameter and call names also have
their own positions.

The parser checks the shape of the program. For example, it rejects a
function definition inside a block. The AST still includes a top-level
`return` or duplicate parameter names so the validator can report those errors
at the right locations.

Run just the parser tests with `python3 -m unittest discover -s tests -p test_parser.py -v`.
They cover all three example files, AST structure and error positions.

## Planned execution rules

The following rules describe planned validation and evaluation:

- `let` creates or reassigns a variable; reading an unassigned name is an error.
- Arithmetic and ordering need integers; equality needs matching types. Integer
  division truncates towards zero. Conditions need Booleans.
- `say` prints one value per line, with Booleans written as `true` or `false`.
- `if` optionally has `else`; `while` may execute zero times.
- Functions are defined before use. Calls read locals before globals, and local
  assignments do not modify globals. Validation rejects duplicate parameter
  names and `return` outside functions.
- Undefined names/functions, division by zero, wrong argument counts, invalid
  types and functions finishing without returning a value produce errors.

The parser tests use all three example programs. Comments in the examples show
the expected output after execution is implemented.
