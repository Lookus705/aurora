import sys
from pathlib import Path
import unittest
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.domain import (
    BookingStatus,
    Business,
    BusinessLocation,
    Customer,
    Employee,
    EmployeeSkill,
    Service,
    SkillLevel,
)
from salon_mvp.storage import AppState
from salon_mvp.booking_service import BookingService


class BookingServiceTests(unittest.TestCase):
    def setUp(self):
        self.business = Business(id="biz_1", name="Belleza & Salud")
        self.location = BusinessLocation(id="loc_1", business_id=self.business.id, name="Centro")
        self.service = Service(
            id="srv_1",
            business_id=self.business.id,
            name="Limpieza facial premium",
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
        self.customer = Customer(id="cus_1", business_id=self.business.id, display_name="Laura", phone="600000000")
        self.state = AppState(
            business=self.business,
            locations=[self.location],
            services=[self.service],
            employees=[self.employee],
            customers=[self.customer],
        )
        self.service_layer = BookingService(self.state)

    def test_create_booking_applies_employee_pricing_and_sets_requested_status(self):
        booking = self.service_layer.create_booking(
            customer_id=self.customer.id,
            service_id=self.service.id,
            location_id=self.location.id,
            employee_id=self.employee.id,
            start_at=datetime(2026, 5, 1, 10, 0),
            preferences="Evitar aromas fuertes",
        )

        self.assertEqual(booking.price_cents, 5500)
        self.assertEqual(booking.status, BookingStatus.REQUESTED)
        self.assertEqual(booking.preferences, "Evitar aromas fuertes")
        self.assertEqual(len(self.state.bookings), 1)

    def test_confirm_booking_changes_status_to_confirmed(self):
        booking = self.service_layer.create_booking(
            customer_id=self.customer.id,
            service_id=self.service.id,
            location_id=self.location.id,
            employee_id=self.employee.id,
            start_at=datetime(2026, 5, 1, 10, 0),
        )

        confirmed = self.service_layer.confirm_booking(booking.id)

        self.assertEqual(confirmed.status, BookingStatus.CONFIRMED)
        self.assertEqual(self.state.bookings[0].status, BookingStatus.CONFIRMED)

    def test_cancel_booking_changes_status_to_cancelled(self):
        booking = self.service_layer.create_booking(
            customer_id=self.customer.id,
            service_id=self.service.id,
            location_id=self.location.id,
            employee_id=self.employee.id,
            start_at=datetime(2026, 5, 1, 10, 0),
        )

        cancelled = self.service_layer.cancel_booking(booking.id)

        self.assertEqual(cancelled.status, BookingStatus.CANCELLED)
        self.assertEqual(self.state.bookings[0].status, BookingStatus.CANCELLED)

    def test_reschedule_booking_updates_datetime_and_status(self):
        booking = self.service_layer.create_booking(
            customer_id=self.customer.id,
            service_id=self.service.id,
            location_id=self.location.id,
            employee_id=self.employee.id,
            start_at=datetime(2026, 5, 1, 10, 0),
        )

        rescheduled = self.service_layer.reschedule_booking(booking.id, datetime(2026, 5, 2, 12, 30))

        self.assertEqual(rescheduled.start_at, datetime(2026, 5, 2, 12, 30))
        self.assertEqual(rescheduled.status, BookingStatus.RESCHEDULED)

    def test_create_booking_rejects_unknown_employee(self):
        with self.assertRaises(ValueError):
            self.service_layer.create_booking(
                customer_id=self.customer.id,
                service_id=self.service.id,
                location_id=self.location.id,
                employee_id="emp_missing",
                start_at=datetime(2026, 5, 1, 10, 0),
            )


if __name__ == "__main__":
    unittest.main()
