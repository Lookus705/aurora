import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.demo import build_demo_state  # noqa: E402
from salon_mvp.cli import build_cli_report, main  # noqa: E402
from salon_mvp.__main__ import main as module_main  # noqa: E402


class CliTests(unittest.TestCase):
    def test_build_cli_report_includes_demo_sections(self) -> None:
        report = build_cli_report(build_demo_state())

        self.assertIn("Belleza & Salud", report)
        self.assertIn("Canal de prueba: telegram", report)
        self.assertIn("Canal de producción: whatsapp", report)

    def test_main_prints_report_for_demo_command(self) -> None:
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            exit_code = main(["report"])

        output = buffer.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("Belleza & Salud", output)
        self.assertIn("Canal de producción: whatsapp", output)

    def test_module_main_prints_report_for_demo_command(self) -> None:
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            exit_code = module_main(["report"])

        output = buffer.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("Belleza & Salud", output)
        self.assertIn("Canal de prueba: telegram", output)


if __name__ == "__main__":
    unittest.main()
