from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .domain import Booking, BusinessLocation, Customer, Employee, Service, format_euro, make_booking_summary


class IntakeStep(str, Enum):
    GREETING = "greeting"
    SERVICE = "service"
    LOCATION = "location"
    DATETIME = "datetime"
    PREFERENCES = "preferences"
    CONFIRMATION = "confirmation"
    DONE = "done"


@dataclass(slots=True)
class BookingChatFlow:
    business_name: str
    customer: Customer
    services: list[Service]
    locations: list[BusinessLocation]
    selected_service_id: str | None = None
    selected_location_id: str | None = None
    requested_start_at: datetime | None = None
    preferred_employee_id: str | None = None
    preferences: str = ""
    wants_express_booking: bool = False
    confirmed: bool = False

    def current_step(self) -> IntakeStep:
        if self.confirmed:
            return IntakeStep.DONE
        if not self.selected_service_id:
            return IntakeStep.SERVICE
        if not self.selected_location_id:
            return IntakeStep.LOCATION
        if self.requested_start_at is None:
            return IntakeStep.DATETIME
        if not self.preferences and self.customer.first_visit:
            return IntakeStep.PREFERENCES
        return IntakeStep.CONFIRMATION

    def available_services_line(self) -> str:
        return ", ".join(service.name for service in self.services)

    def available_locations_line(self) -> str:
        return ", ".join(location.name for location in self.locations)

    def next_prompt(self) -> str:
        step = self.current_step()
        if step == IntakeStep.SERVICE:
            return (
                f"Hola, soy el asistente de {self.business_name}. "
                f"¿Qué servicio necesitas? Opciones: {self.available_services_line()}."
            )
        if step == IntakeStep.LOCATION:
            return (
                "Perfecto. ¿En qué sede te viene mejor? "
                f"Opciones: {self.available_locations_line()}."
            )
        if step == IntakeStep.DATETIME:
            return "¿Qué día y hora te viene bien para la cita?"
        if step == IntakeStep.PREFERENCES:
            return "Es tu primera visita, así que cuéntame cualquier preferencia, alergia o detalle importante."
        if step == IntakeStep.CONFIRMATION:
            return self.confirmation_message()
        return "Tu cita ya está cerrada. Si necesitas cambios, te ayudo a reprogramarla."

    def confirmation_message(self) -> str:
        service = self._selected_service()
        location = self._selected_location()
        details = [
            "He preparado tu solicitud de cita:",
            f"- Servicio: {service.name}",
            f"- Sede: {location.name}",
            f"- Precio estimado: {format_euro(service.base_price_cents)}",
        ]
        if self.requested_start_at is not None:
            details.append(f"- Fecha y hora: {self.requested_start_at.strftime('%Y-%m-%d %H:%M')}")
        if self.preferences:
            details.append(f"- Preferencias: {self.preferences}")
        details.append("¿Confirmas para dejarla reservada?")
        return "\n".join(details)

    def confirm(self) -> None:
        self.confirmed = True

    def _selected_service(self) -> Service:
        for service in self.services:
            if service.id == self.selected_service_id:
                return service
        raise ValueError("No se ha seleccionado un servicio válido")

    def _selected_location(self) -> BusinessLocation:
        for location in self.locations:
            if location.id == self.selected_location_id:
                return location
        raise ValueError("No se ha seleccionado una sede válida")


def build_client_chat_journey() -> list[str]:
    return [
        "1. El cliente escribe al negocio por chat.",
        "2. El asistente pregunta por el servicio.",
        "3. El asistente pregunta por la sede.",
        "4. El asistente pide día y hora.",
        "5. Si es primera visita, recopila preferencias o restricciones.",
        "6. El asistente resume y pide confirmación.",
        "7. Al confirmar, se genera la cita y avisa al empleado.",
    ]


def build_employee_booking_notification(
    booking: Booking,
    customer: Customer,
    service: Service,
    employee: Employee,
    location_name: str,
) -> str:
    lines = [
        f"Nueva cita asignada para {employee.name}.",
        make_booking_summary(booking, customer, service, employee),
        f"Sede: {location_name}",
    ]
    if customer.phone:
        lines.append(f"Contacto del cliente: {customer.phone}")
    if booking.preferences:
        lines.append(f"Preferencias del cliente: {booking.preferences}")
    lines.append("Acción: revisa, confirma y prepárate para la atención.")
    return "\n".join(lines)


def build_chat_handoff_message(
    booking: Booking,
    customer: Customer,
    service: Service,
    employee: Employee,
    location_name: str,
) -> str:
    return (
        f"Cita confirmada para {customer.display_name}. "
        f"Asignada a {employee.name} en {location_name} para {service.name} "
        f"por {format_euro(booking.price_cents)}."
    )
