import sys
from pathlib import Path
import unittest
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.domain import (
    Booking,
    BookingStatus,
    Business,
    BusinessLocation,
    Customer,
    Employee,
    EmployeeSkill,
    Feedback,
    Service,
    SkillLevel,
)
from salon_mvp.storage import AppState, JsonStateStore


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = ROOT / ".tmp_test_storage"
        self.tmp_dir.mkdir(exist_ok=True)
        self.path = self.tmp_dir / "state.json"
        self.store = JsonStateStore(self.path)

        self.state = AppState(
            business=Business(id="biz_1", name="Belleza & Salud", description="Centro de estética"),
            locations=[BusinessLocation(id="loc_1", business_id="biz_1", name="Centro", address="Calle 1")],
            services=[Service(id="srv_1", business_id="biz_1", name="Limpieza facial", base_price_cents=5000, duration_minutes=45, location_ids=["loc_1"])],
            employees=[
                Employee(
                    id="emp_1",
                    business_id="biz_1",
                    name="Ana",
                    skills=[EmployeeSkill(name="facial", level=SkillLevel.SENIOR, bonus_percent=10)],
                )
            ],
            customers=[Customer(id="cus_1", business_id="biz_1", display_name="Laura", phone="600000000")],
            bookings=[
                Booking(
                    id="boo_1",
                    business_id="biz_1",
                    customer_id="cus_1",
                    service_id="srv_1",
                    location_id="loc_1",
                    employee_id="emp_1",
                    start_at=datetime(2026, 5, 1, 10, 0),
                    price_cents=5500,
                    status=BookingStatus.CONFIRMED,
                    preferences="Evitar aromas fuertes",
                )
            ],
            feedbacks=[Feedback(booking_id="boo_1", local_rating=5, attention_rating=4, employee_rating=5)],
        )

    def tearDown(self):
        if self.path.exists():
            self.path.unlink()
        if self.tmp_dir.exists():
            try:
                self.tmp_dir.rmdir()
            except OSError:
                pass

    def test_save_creates_json_file_with_expected_top_level_keys(self):
        self.store.save(self.state)

        self.assertTrue(self.path.exists())
        payload = self.path.read_text(encoding="utf-8")
        self.assertIn('"business"', payload)
        self.assertIn('"bookings"', payload)
        self.assertIn('"feedbacks"', payload)

    def test_load_restores_complete_state(self):
        self.store.save(self.state)
        loaded = self.store.load()

        self.assertIsInstance(loaded, AppState)
        self.assertEqual(loaded.business.name, "Belleza & Salud")
        self.assertEqual(loaded.locations[0].address, "Calle 1")
        self.assertEqual(loaded.services[0].duration_minutes, 45)
        self.assertEqual(loaded.employees[0].skills[0].bonus_percent, 10)
        self.assertEqual(loaded.customers[0].phone, "600000000")
        self.assertEqual(loaded.bookings[0].status, BookingStatus.CONFIRMED)
        self.assertEqual(loaded.bookings[0].start_at, datetime(2026, 5, 1, 10, 0))
        self.assertEqual(loaded.bookings[0].preferences, "Evitar aromas fuertes")
        self.assertEqual(loaded.feedbacks[0].employee_rating, 5)

    def test_load_missing_file_returns_empty_state(self):
        if self.path.exists():
            self.path.unlink()

        loaded = self.store.load()

        self.assertIsInstance(loaded, AppState)
        self.assertIsNone(loaded.business)
        self.assertEqual(loaded.locations, [])
        self.assertEqual(loaded.services, [])
        self.assertEqual(loaded.bookings, [])
        self.assertEqual(loaded.feedbacks, [])


if __name__ == "__main__":
    unittest.main()
