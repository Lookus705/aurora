from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .admin_views import build_operational_dashboard
from .chat_flow import BookingChatFlow, build_chat_handoff_message
from .chat_orchestrator import ChatOrchestrator
from .domain import (
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
from .integrations import build_messaging_adapter
from .reminders import build_booking_reminders
from .storage import AppState


def build_demo_state() -> AppState:
    business = Business(id="biz_1", name="Belleza & Salud", description="MVP local")
    location = BusinessLocation(id="loc_centro", business_id=business.id, name="Centro")
    service = Service(
        id="srv_1",
        business_id=business.id,
        name="Limpieza facial premium",
        base_price_cents=5000,
        duration_minutes=45,
        location_ids=[location.id],
    )
    employee = Employee(
        id="emp_1",
        business_id=business.id,
        name="Ana",
        skills=[EmployeeSkill(name="facial", level=SkillLevel.SENIOR, bonus_percent=10.0)],
    )
    customer = Customer(id="cus_1", business_id=business.id, display_name="Laura", phone="600000000")
    booking = Booking(
        id="boo_1",
        business_id=business.id,
        customer_id=customer.id,
        service_id=service.id,
        location_id=location.id,
        employee_id=employee.id,
        start_at=datetime(2026, 5, 2, 11, 0),
        price_cents=5500,
        status=BookingStatus.COMPLETED,
    )
    feedback = Feedback(booking_id=booking.id, local_rating=5, attention_rating=5, employee_rating=4)
    return AppState(
        business=business,
        locations=[location],
        services=[service],
        employees=[employee],
        customers=[customer],
        bookings=[booking],
        feedbacks=[feedback],
    )


@dataclass(slots=True)
class SalonDemo:
    state: AppState

    def render_report(self, channel: str = "telegram") -> str:
        business = self.state.business
        if business is None:
            return "Sin negocio de demo"

        dashboard = build_operational_dashboard(
            business_name=business.name,
            bookings=self.state.bookings,
            customers=self.state.customers,
            employees=self.state.employees,
            services=self.state.services,
            feedbacks=self.state.feedbacks,
        )

        customer = self.state.customers[0]
        service = self.state.services[0]
        employee = self.state.employees[0]
        location = self.state.locations[0]
        booking = self.state.bookings[0]

        flow = BookingChatFlow(
            business_name=business.name,
            customer=customer,
            services=self.state.services,
            locations=self.state.locations,
            selected_service_id=service.id,
            selected_location_id=location.id,
            requested_start_at=booking.start_at,
            confirmed=True,
        )
        orchestrator = ChatOrchestrator(self.state)
        orchestration = orchestrator.finalize_booking(flow, employee_id=employee.id)

        reminder_lines = []
        for reminder in build_booking_reminders(booking, customer, service, location.name):
            reminder_lines.append(f"{reminder.kind}: {reminder.channel}")

        telegram_message = build_messaging_adapter("telegram").format_message(
            recipient_id=customer.id,
            text=orchestration.user_message,
            subject="booking_confirmation",
        )
        whatsapp_message = build_messaging_adapter("whatsapp").format_message(
            recipient_id=customer.id,
            text=orchestration.user_message,
            subject="booking_confirmation",
        )

        lines = [
            dashboard.as_text(),
            orchestration.user_message,
            build_chat_handoff_message(booking, customer, service, employee, location.name),
            f"Canal de prueba: {telegram_message.channel} ({telegram_message.metadata.get('parse_mode', 'plain')})",
            f"Canal de producción: {whatsapp_message.channel}",
            "Recordatorios:",
            *[f"- {line}" for line in reminder_lines],
        ]
        return "\n".join(lines)
