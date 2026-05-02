import sys
from pathlib import Path
import unittest
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.chat_flow import BookingChatFlow
from salon_mvp.domain import Booking, BookingStatus, Business, BusinessLocation, Customer, Employee, EmployeeSkill, Service, SkillLevel
from salon_mvp.storage import AppState
from salon_mvp.chat_orchestrator import ChatOrchestrator


class ChatOrchestratorTests(unittest.TestCase):
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
        self.orchestrator = ChatOrchestrator(self.state)

    def test_finalize_booking_creates_confirmed_booking_and_messages(self):
        flow = BookingChatFlow(
            business_name=self.business.name,
            customer=self.customer,
            services=[self.service],
            locations=[self.location],
            selected_service_id=self.service.id,
            selected_location_id=self.location.id,
            requested_start_at=datetime(2026, 5, 1, 10, 0),
            preferences="Evitar aromas fuertes",
            confirmed=True,
        )

        result = self.orchestrator.finalize_booking(flow, employee_id=self.employee.id)

        self.assertTrue(result.confirmed)
        self.assertIsNotNone(result.booking)
        self.assertEqual(result.booking.status, BookingStatus.CONFIRMED)
        self.assertIn("Cita confirmada", result.user_message)
        self.assertIn("Nueva cita asignada", result.employee_message)
        self.assertEqual(len(self.state.bookings), 1)

    def test_finalize_booking_suggests_alternative_when_slot_is_busy(self):
        self.state.bookings.append(
            Booking(
                id="boo_1",
                business_id=self.business.id,
                customer_id=self.customer.id,
                service_id=self.service.id,
                location_id=self.location.id,
                employee_id=self.employee.id,
                start_at=datetime(2026, 5, 1, 10, 0),
                price_cents=5500,
                status=BookingStatus.CONFIRMED,
            )
        )
        flow = BookingChatFlow(
            business_name=self.business.name,
            customer=self.customer,
            services=[self.service],
            locations=[self.location],
            selected_service_id=self.service.id,
            selected_location_id=self.location.id,
            requested_start_at=datetime(2026, 5, 1, 10, 30),
            confirmed=True,
        )

        result = self.orchestrator.finalize_booking(flow, employee_id=self.employee.id)

        self.assertFalse(result.confirmed)
        self.assertIsNone(result.booking)
        self.assertIn("siguiente hueco", result.user_message)
        self.assertIn("10:45", result.user_message)


if __name__ == "__main__":
    unittest.main()
