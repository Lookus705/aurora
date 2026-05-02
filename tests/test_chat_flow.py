import sys
from pathlib import Path
import unittest
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp import (
    Booking,
    BookingChatFlow,
    BusinessLocation,
    Customer,
    Employee,
    IntakeStep,
    Service,
    build_chat_handoff_message,
    build_client_chat_journey,
    build_employee_booking_notification,
)


class ChatFlowTests(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(id="cus_1", business_id="biz_1", display_name="Laura", phone="600000000")
        self.service = Service(
            id="srv_1",
            business_id="biz_1",
            name="Limpieza facial premium",
            base_price_cents=5000,
            duration_minutes=45,
            location_ids=["loc_1"],
        )
        self.location = BusinessLocation(id="loc_1", business_id="biz_1", name="Centro")
        self.employee = Employee(id="emp_1", business_id="biz_1", name="Ana")

    def test_flow_starts_by_asking_for_service(self):
        flow = BookingChatFlow(
            business_name="Belleza & Salud",
            customer=self.customer,
            services=[self.service],
            locations=[self.location],
        )

        self.assertEqual(flow.current_step(), IntakeStep.SERVICE)
        self.assertIn("¿Qué servicio necesitas?", flow.next_prompt())

    def test_flow_progresses_through_confirmation(self):
        flow = BookingChatFlow(
            business_name="Belleza & Salud",
            customer=self.customer,
            services=[self.service],
            locations=[self.location],
            selected_service_id=self.service.id,
            selected_location_id=self.location.id,
            requested_start_at=datetime(2026, 5, 2, 11, 0),
            preferences="Evitar aromas fuertes",
        )

        self.assertEqual(flow.current_step(), IntakeStep.CONFIRMATION)
        confirmation = flow.next_prompt()
        self.assertIn("Limpieza facial premium", confirmation)
        self.assertIn("Centro", confirmation)
        self.assertIn("Evitar aromas fuertes", confirmation)

    def test_flow_marks_done_after_confirm(self):
        flow = BookingChatFlow(
            business_name="Belleza & Salud",
            customer=self.customer,
            services=[self.service],
            locations=[self.location],
            confirmed=True,
        )

        self.assertEqual(flow.current_step(), IntakeStep.DONE)
        self.assertIn("cita ya está cerrada", flow.next_prompt())

    def test_client_journey_is_documented(self):
        steps = build_client_chat_journey()
        self.assertEqual(len(steps), 7)
        self.assertTrue(steps[0].startswith("1."))
        self.assertIn("avisa al empleado", steps[-1])

    def test_employee_notification_includes_actionable_details(self):
        booking = Booking(
            id="boo_1",
            business_id="biz_1",
            customer_id=self.customer.id,
            service_id=self.service.id,
            location_id=self.location.id,
            employee_id=self.employee.id,
            start_at=datetime(2026, 5, 2, 11, 0),
            price_cents=5000,
            preferences="Evitar aromas fuertes",
        )

        notification = build_employee_booking_notification(
            booking=booking,
            customer=self.customer,
            service=self.service,
            employee=self.employee,
            location_name=self.location.name,
        )

        self.assertIn("Nueva cita asignada", notification)
        self.assertIn("Laura", notification)
        self.assertIn("Centro", notification)
        self.assertIn("Evitar aromas fuertes", notification)

    def test_chat_handoff_message_summarizes_confirmation(self):
        booking = Booking(
            id="boo_2",
            business_id="biz_1",
            customer_id=self.customer.id,
            service_id=self.service.id,
            location_id=self.location.id,
            employee_id=self.employee.id,
            start_at=datetime(2026, 5, 2, 11, 0),
            price_cents=5000,
        )

        message = build_chat_handoff_message(
            booking=booking,
            customer=self.customer,
            service=self.service,
            employee=self.employee,
            location_name=self.location.name,
        )

        self.assertIn("Cita confirmada", message)
        self.assertIn("Ana", message)
        self.assertIn("50.00€", message)


if __name__ == "__main__":
    unittest.main()