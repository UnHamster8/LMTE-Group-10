"""Member D: black-box integration tests for the complete Pebble CLI."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def run_source(source: str, *options: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "program.peb"
        path.write_text(source, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(ROOT / "main.py"), *options, str(path)],
            cwd=ROOT, text=True, capture_output=True, timeout=8,
        )

class IntegrationTests(unittest.TestCase):
    def test_all_supplied_examples(self):
        expected = {
            "basic.peb": "15\n14\n20\ntrue\n-2\n",
            "control_flow.peb": "3\n20\n1\n",
            "functions.peb": "12\n",
        }
        for filename, output in expected.items():
            with self.subTest(example=filename):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "main.py"), str(ROOT / "examples" / filename)],
                    cwd=ROOT, text=True, capture_output=True, timeout=8,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, output)
                self.assertEqual(result.stderr, "")

    def test_pipeline_all_features_together(self):
        result = run_source("""
            // comments + expressions + loop + branch + calls + local scope
            let total = 0;
            func doubled(x) do
                let local = x * 2;
                return local;
            end
            let n = 1;
            while n <= 3 do
                if n == 2 do
                    let total = total + doubled(n);
                else
                    let total = total + n;
                end
                let n = n + 1;
            end
            say total;
            say n;
            say true != false;
        """)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "8\n4\ntrue\n")

    def test_lexical_syntax_validation_and_runtime_failures(self):
        cases = [
            ("say @;", "Lexical error", "1:5"),
            ("let x = ;", "Syntax error", "1:"),
            ("return 1;", "Validation error", "1:1"),
            ("say 1 / 0;", "Runtime error", "1:7"),
        ]
        for source, category, location in cases:
            with self.subTest(category=category):
                result = run_source(source)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn(category, result.stderr)
                self.assertIn(location, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_tokens_option_uses_lexer_without_execution(self):
        result = run_source("say 1 / 0;", "--tokens")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SAY", result.stdout)
        self.assertIn("EOF", result.stdout)
        self.assertNotIn("Runtime error", result.stderr)

if __name__ == "__main__":
    unittest.main()
