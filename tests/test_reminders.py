import sys
from pathlib import Path
import unittest
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.domain import Booking, Customer, Service
from salon_mvp.reminders import build_booking_reminders


class ReminderPlannerTests(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(
            id="cus_1",
            business_id="biz_1",
            display_name="Laura",
            phone="600000000",
        )
        self.service = Service(
            id="srv_1",
            business_id="biz_1",
            name="Limpieza facial premium",
            base_price_cents=5000,
            duration_minutes=45,
        )
        self.booking = Booking(
            id="boo_1",
            business_id="biz_1",
            customer_id=self.customer.id,
            service_id=self.service.id,
            location_id="loc_1",
            employee_id="emp_1",
            start_at=datetime(2026, 5, 2, 11, 0),
            price_cents=5000,
        )

    def test_build_booking_reminders_creates_pre_visit_and_feedback_messages(self):
        reminders = build_booking_reminders(
            booking=self.booking,
            customer=self.customer,
            service=self.service,
            location_name="Centro",
        )

        self.assertEqual([item.kind for item in reminders], ["pre_visit_24h", "pre_visit_2h", "feedback_request"])
        self.assertEqual(reminders[0].send_at, datetime(2026, 5, 1, 11, 0))
        self.assertEqual(reminders[1].send_at, datetime(2026, 5, 2, 9, 0))
        self.assertEqual(reminders[2].send_at, datetime(2026, 5, 2, 13, 0))
        self.assertIn("Laura", reminders[0].message)
        self.assertIn("Limpieza facial premium", reminders[1].message)
        self.assertIn("Centro", reminders[2].message)

    def test_build_booking_reminders_uses_chat_channel_when_customer_has_no_phone(self):
        customer = Customer(id="cus_2", business_id="biz_1", display_name="Sofía")

        reminders = build_booking_reminders(
            booking=self.booking,
            customer=customer,
            service=self.service,
            location_name="Centro",
        )

        self.assertTrue(all(item.channel == "chat" for item in reminders))


if __name__ == "__main__":
    unittest.main()
