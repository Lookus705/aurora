from __future__ import annotations

from dataclasses import dataclass

from .booking_service import BookingService
from .chat_flow import BookingChatFlow, build_chat_handoff_message, build_employee_booking_notification
from .domain import Booking, Employee, Service
from .scheduling import next_available_slot, slot_is_available
from .storage import AppState


@dataclass(slots=True)
class ChatOrchestrationResult:
    confirmed: bool
    booking: Booking | None
    user_message: str
    employee_message: str = ""


class ChatOrchestrator:
    def __init__(self, state: AppState):
        self.state = state
        self.booking_service = BookingService(state)

    def finalize_booking(self, flow: BookingChatFlow, employee_id: str) -> ChatOrchestrationResult:
        service = self._selected_service(flow)
        employee = self._get_employee(employee_id)
        if flow.requested_start_at is None or flow.selected_location_id is None:
            return ChatOrchestrationResult(
                confirmed=False,
                booking=None,
                user_message="Faltan datos para cerrar la reserva.",
            )

        if not slot_is_available(
            service=service,
            bookings=self.state.bookings,
            start_at=flow.requested_start_at,
            employee_id=employee.id,
            location_id=flow.selected_location_id,
        ):
            alternative = next_available_slot(
                service=service,
                bookings=self.state.bookings,
                window_start=flow.requested_start_at,
                window_end=flow.requested_start_at.replace(hour=23, minute=59),
                employee_id=employee.id,
                location_id=flow.selected_location_id,
            )
            if alternative is None:
                message = "No hay huecos disponibles para ese día."
            else:
                message = f"Ese hueco está ocupado. Te propongo el siguiente hueco: {alternative.strftime('%H:%M')}."
            return ChatOrchestrationResult(confirmed=False, booking=None, user_message=message)

        booking = self.booking_service.create_booking(
            customer_id=flow.customer.id,
            service_id=service.id,
            location_id=flow.selected_location_id,
            employee_id=employee.id,
            start_at=flow.requested_start_at,
            preferences=flow.preferences,
        )
        booking = self.booking_service.confirm_booking(booking.id)
        location_name = self._location_name(flow.selected_location_id)
        user_message = build_chat_handoff_message(booking, flow.customer, service, employee, location_name)
        employee_message = build_employee_booking_notification(booking, flow.customer, service, employee, location_name)
        return ChatOrchestrationResult(
            confirmed=True,
            booking=booking,
            user_message=user_message,
            employee_message=employee_message,
        )

    def _selected_service(self, flow: BookingChatFlow) -> Service:
        if flow.selected_service_id is None:
            raise ValueError("El flujo no tiene un servicio seleccionado")
        for service in flow.services:
            if service.id == flow.selected_service_id:
                return service
        raise ValueError("Servicio no encontrado en el flujo")

    def _get_employee(self, employee_id: str) -> Employee:
        for employee in self.state.employees:
            if employee.id == employee_id:
                return employee
        raise ValueError("Empleado no encontrado")

    def _location_name(self, location_id: str) -> str:
        for location in self.state.locations:
            if location.id == location_id:
                return location.name
        raise ValueError("Sede no encontrada")
