import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.demo import SalonDemo, build_demo_state


class DemoAppTests(unittest.TestCase):
    def test_build_demo_state_includes_business_people_services_and_bookings(self):
        state = build_demo_state()

        self.assertIsNotNone(state.business)
        self.assertGreaterEqual(len(state.locations), 1)
        self.assertGreaterEqual(len(state.services), 1)
        self.assertGreaterEqual(len(state.employees), 1)
        self.assertGreaterEqual(len(state.customers), 1)
        self.assertGreaterEqual(len(state.bookings), 1)

    def test_demo_report_combines_owner_view_chat_and_channel_contracts(self):
        demo = SalonDemo(build_demo_state())
        report = demo.render_report(channel="telegram")

        self.assertIn("Dashboard de", report)
        self.assertIn("Cita confirmada", report)
        self.assertIn("telegram", report)
        self.assertIn("whatsapp", report)


if __name__ == "__main__":
    unittest.main()
