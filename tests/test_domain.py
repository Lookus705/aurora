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
    Customer,
    Employee,
    EmployeeSkill,
    Feedback,
    Role,
    Service,
    SkillLevel,
    apply_employee_pricing,
    can_employee_handle_service,
    format_euro,
    make_booking_summary,
)


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.business = Business(id="biz_1", name="Belleza & Salud")
        self.service = Service(
            id="srv_1",
            business_id=self.business.id,
            name="Limpieza facial premium",
            base_price_cents=5000,
            duration_minutes=45,
            location_ids=["loc_1"],
        )
        self.employee = Employee(
            id="emp_1",
            business_id=self.business.id,
            name="Ana",
            skills=[EmployeeSkill(name="facial", level=SkillLevel.SENIOR, bonus_percent=10)],
        )
        self.customer = Customer(id="cus_1", business_id=self.business.id, display_name="Laura", phone="600000000")

    def test_apply_employee_pricing_adds_skill_bonus(self):
        price = apply_employee_pricing(self.service, self.employee)
        self.assertEqual(price, 5500)

    def test_can_employee_handle_service_active_employee(self):
        self.assertTrue(can_employee_handle_service(self.employee, self.service))

    def test_can_employee_handle_service_inactive_employee(self):
        employee = Employee(id="emp_2", business_id=self.business.id, name="Noel", active=False)
        self.assertFalse(can_employee_handle_service(employee, self.service))

    def test_feedback_average_rating(self):
        feedback = Feedback(booking_id="b1", local_rating=5, attention_rating=4, employee_rating=3)
        self.assertEqual(feedback.average_rating(), 4.0)

    def test_booking_summary(self):
        booking = Booking(
            id="boo_1",
            business_id=self.business.id,
            customer_id=self.customer.id,
            service_id=self.service.id,
            location_id="loc_1",
            employee_id=self.employee.id,
            start_at=datetime(2026, 5, 1, 10, 30),
            price_cents=5500,
            status=BookingStatus.CONFIRMED,
        )
        summary = make_booking_summary(booking, self.customer, self.service, self.employee)
        self.assertIn("Laura tiene cita", summary)
        self.assertIn("Limpieza facial premium", summary)
        self.assertIn("Ana", summary)
        self.assertIn("55.00€", summary)

    def test_format_euro(self):
        self.assertEqual(format_euro(12345), "123.45€")


if __name__ == "__main__":
    unittest.main()
