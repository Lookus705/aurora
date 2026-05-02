import sys
from pathlib import Path
import unittest
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.domain import Booking, BookingStatus, Business, BusinessLocation, Employee, EmployeeSkill, Service, SkillLevel
from salon_mvp.scheduling import next_available_slot, slot_is_available


class SchedulingTests(unittest.TestCase):
    def setUp(self):
        self.business = Business(id="biz_1", name="Belleza & Salud")
        self.location = BusinessLocation(id="loc_1", business_id=self.business.id, name="Centro")
        self.service = Service(
            id="srv_1",
            business_id=self.business.id,
            name="Limpieza facial",
            base_price_cents=5000,
            duration_minutes=45,
            location_ids=[self.location.id],
        )
        self.employee = Employee(
            id="emp_1",
            business_id=self.business.id,
            name="Ana",
            skills=[EmployeeSkill(name="facial", level=SkillLevel.SENIOR, bonus_percent=10)],
        )
        self.other_employee = Employee(id="emp_2", business_id=self.business.id, name="Sara")
        self.bookings = [
            Booking(
                id="boo_1",
                business_id=self.business.id,
                customer_id="cus_1",
                service_id=self.service.id,
                location_id=self.location.id,
                employee_id=self.employee.id,
                start_at=datetime(2026, 5, 1, 10, 0),
                price_cents=5500,
                status=BookingStatus.CONFIRMED,
            )
        ]

    def test_slot_is_not_available_when_employee_is_busy(self):
        self.assertFalse(
            slot_is_available(
                service=self.service,
                bookings=self.bookings,
                start_at=datetime(2026, 5, 1, 10, 30),
                employee_id=self.employee.id,
                location_id=self.location.id,
            )
        )

    def test_slot_is_available_for_different_employee_and_location(self):
        other_location = BusinessLocation(id="loc_2", business_id=self.business.id, name="Sucursal")
        self.assertTrue(
            slot_is_available(
                service=self.service,
                bookings=self.bookings,
                start_at=datetime(2026, 5, 1, 10, 30),
                employee_id=self.other_employee.id,
                location_id=other_location.id,
            )
        )

    def test_next_available_slot_returns_first_free_slot(self):
        proposed = next_available_slot(
            service=self.service,
            bookings=self.bookings,
            window_start=datetime(2026, 5, 1, 10, 0),
            window_end=datetime(2026, 5, 1, 12, 0),
            employee_id=self.employee.id,
            location_id=self.location.id,
            step_minutes=15,
        )

        self.assertEqual(proposed, datetime(2026, 5, 1, 10, 45))


if __name__ == "__main__":
    unittest.main()
