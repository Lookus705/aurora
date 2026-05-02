from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .domain import Booking, Customer, Service


@dataclass(slots=True)
class ReminderTask:
    kind: str
    send_at: datetime
    channel: str
    message: str


def build_booking_reminders(
    booking: Booking,
    customer: Customer,
    service: Service,
    location_name: str,
) -> list[ReminderTask]:
    channel = "whatsapp" if customer.phone else "chat"
    reminders = [
        ReminderTask(
            kind="pre_visit_24h",
            send_at=booking.start_at - timedelta(hours=24),
            channel=channel,
            message=(
                f"Hola {customer.display_name}, te recordamos tu cita de {service.name} en {location_name} "
                f"para el {booking.start_at.strftime('%Y-%m-%d %H:%M')}."
            ),
        ),
        ReminderTask(
            kind="pre_visit_2h",
            send_at=booking.start_at - timedelta(hours=2),
            channel=channel,
            message=(
                f"Tu cita de {service.name} está cerca, {customer.display_name}. "
                f"Te esperamos en {location_name} a las {booking.start_at.strftime('%H:%M')}."
            ),
        ),
        ReminderTask(
            kind="feedback_request",
            send_at=booking.start_at + timedelta(hours=2),
            channel=channel,
            message=(
                f"Gracias por venir, {customer.display_name}. ¿Nos dejas tu valoración de {service.name} en {location_name}?"
            ),
        ),
    ]
    return sorted(reminders, key=lambda reminder: reminder.send_at)
