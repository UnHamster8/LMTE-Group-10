
# Group 10 — Testing and Validation

## 1. Test Environment and Execution

Pebble is implemented in Python 3.10+ using only the Python standard library. No third-party dependencies are required.

Run the complete automated test suite from the project root:

```sh
python -m unittest discover -s tests -v
```

The example programs can be executed using:

```sh
python main.py examples/basic.peb
python main.py examples/control_flow.peb
python main.py examples/functions.peb
```

## 2. Test Results

The integrated Pebble project was tested locally on 10 November 2026. **All 45 automated tests passed, with 0 failures and 0 errors.**

The test suite covers lexical analysis, parsing, AST construction, evaluation, command-line integration and regression testing.

| Area | What was tested |
| --- | --- |
| Lexical analysis | Keywords, identifiers, integers, operators, comments, token positions and invalid characters |
| Parsing and AST | Statements, grammar rules, operator precedence, function definitions, valid and invalid syntax |
| Evaluation | Arithmetic, comparisons, variables, control flow, functions, return values and variable scope |
| CLI integration | Executing source files through `main.py`, verifying output, error messages and exit status |
| Regression | Language specification examples, edge cases and existing language behaviour |

## 3. End-to-End Testing

End-to-end tests verify the complete execution process, from reading source code to producing output or reporting errors.

The following table summarises representative test cases and their expected results.

| Program / Input | Expected Result |
| --- | --- |
| `examples/basic.peb` | Prints `15`, `14`, `20`, `true`, `-2` on separate lines |
| `examples/control_flow.peb` | Prints `3`, `20`, `1` |
| `examples/functions.peb` | Prints `12` |
| `say 1 + 2 * 3;` | Prints `7`, verifying operator precedence |
| `while false do say 99; end` | Terminates without output |
| `say 1 / 0;` | Reports a division-by-zero runtime error |
| `let x = ;` | Reports a syntax error |
| `say @;` | Reports a lexical error |

Error-handling tests verify that invalid programs produce a nonzero exit status, informative error messages with source locations, and no unhandled Python traceback.

## 4. Regression Testing and Coverage

Regression tests verify that existing language features continue to behave correctly after integration.

The test suite covers:

- Variable declaration and reassignment
- Arithmetic operations and operator precedence
- Boolean values and comparison operations
- `if/else` statements and `while` loops
- Integer division with truncation toward zero
- Function definitions, calls and return values
- Local and global variable scope
- Duplicate function parameters
- Undefined variables and functions
- Incorrect function argument counts
- Invalid operand types and non-Boolean conditions
- Invalid `return` statements and missing function returns
- Lexical, syntax and runtime error handling

These tests verify both normal program execution and representative invalid inputs.

## 5. Implementation Limitations

Pebble follows the interpreter architecture defined in the Group 10 design.

The interpreter directly evaluates the Abstract Syntax Tree (AST). It does not generate three-address code (TAC), native machine code or optimised executable files.

The language supports integers, Booleans, variables, conditional statements, loops and functions. Advanced features such as strings, floating-point numbers, lists, objects and closures are outside the implemented scope.

The automated test suite provides evidence of correctness for the tested functionality but does not guarantee correctness for every possible program.

## 6. Conclusion

The Group 10 Pebble interpreter has been integrated and tested.

The automated test suite completed with **45 tests passed, 0 failures and 0 errors**.

Testing covered lexical analysis, parsing, AST construction, evaluation, command-line execution, error handling and regression behaviour.

The recorded results demonstrate that the tested features operate as expected and that the integrated interpreter provides the functionality described in the project documentation.
