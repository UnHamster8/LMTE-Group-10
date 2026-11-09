"""Test file reading, token output and errors through the command-line entry point."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def setUp(self) -> None:
        # Each test gets its own folder, which is removed automatically.
        temporary_directory = tempfile.TemporaryDirectory(prefix="pebble-cli-")
        self.addCleanup(temporary_directory.cleanup)
        self.folder = Path(temporary_directory.name)

    def run_cli(self, source_path: Path) -> subprocess.CompletedProcess[str]:
        # Use the same Python interpreter that runs the tests.
        return subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "main.py"), str(source_path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_valid_file_prints_tokens(self) -> None:
        source_path = self.folder / "valid.peb"
        source_path.write_text("let x = 12;", encoding="utf-8")

        result = self.run_cli(source_path)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        kinds = [line.split()[1] for line in result.stdout.splitlines()]
        self.assertEqual(kinds, ["LET", "NAME", "ASSIGN", "INT", "SEMICOLON", "EOF"])
        self.assertIn("value='x'", result.stdout)
        self.assertIn("value=12", result.stdout)

    def test_invalid_character_reports_lexical_error(self) -> None:
        source_path = self.folder / "invalid.peb"
        source_path.write_text("say @;", encoding="utf-8")

        result = self.run_cli(source_path)

        # Errors go to stderr, with no partial token output or traceback.
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn(str(source_path), result.stderr)
        self.assertIn("Lexical error at 1:5", result.stderr)
        self.assertIn("Unexpected character '@'", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_file_reports_read_error(self) -> None:
        source_path = self.folder / "missing.peb"

        result = self.run_cli(source_path)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        # Avoid relying on OS-specific file error messages.
        self.assertIn(f"Cannot read {source_path}:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
