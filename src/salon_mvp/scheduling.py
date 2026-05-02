from __future__ import annotations

from datetime import datetime, timedelta

from .domain import Booking, BookingStatus, Service


ACTIVE_BOOKING_STATUSES = {
    BookingStatus.REQUESTED,
    BookingStatus.CONFIRMED,
    BookingStatus.RESCHEDULED,
    BookingStatus.PENDING_FEEDBACK,
}


def slot_is_available(
    service: Service,
    bookings: list[Booking],
    start_at: datetime,
    employee_id: str,
    location_id: str,
) -> bool:
    proposed_end = start_at + timedelta(minutes=service.duration_minutes)
    for booking in bookings:
        if booking.status not in ACTIVE_BOOKING_STATUSES:
            continue
        if booking.employee_id != employee_id and booking.location_id != location_id:
            continue

        booking_end = booking.start_at + timedelta(minutes=service.duration_minutes)
        overlaps = start_at < booking_end and proposed_end > booking.start_at
        if overlaps:
            return False
    return True


def next_available_slot(
    service: Service,
    bookings: list[Booking],
    window_start: datetime,
    window_end: datetime,
    employee_id: str,
    location_id: str,
    step_minutes: int = 15,
) -> datetime | None:
    candidate = window_start
    step = timedelta(minutes=step_minutes)
    while candidate + timedelta(minutes=service.duration_minutes) <= window_end:
        if slot_is_available(
            service=service,
            bookings=bookings,
            start_at=candidate,
            employee_id=employee_id,
            location_id=location_id,
        ):
            return candidate
        candidate += step
    return None
