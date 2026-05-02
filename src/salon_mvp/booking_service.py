from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from .domain import (
    Booking,
    BookingStatus,
    Customer,
    Employee,
    Service,
    apply_employee_pricing,
    can_employee_handle_service,
    make_id,
)
from .storage import AppState


class BookingService:
    def __init__(self, state: AppState):
        self.state = state

    def create_booking(
        self,
        customer_id: str,
        service_id: str,
        location_id: str,
        employee_id: str,
        start_at: datetime,
        preferences: str = "",
        source_channel: str = "chat",
    ) -> Booking:
        customer = self._get_customer(customer_id)
        service = self._get_service(service_id)
        employee = self._get_employee(employee_id)

        if location_id not in service.location_ids:
            raise ValueError("La sede no admite este servicio")
        if not can_employee_handle_service(employee, service):
            raise ValueError("El empleado no puede atender este servicio")

        booking = Booking(
            id=make_id("boo"),
            business_id=self._business_id,
            customer_id=customer.id,
            service_id=service.id,
            location_id=location_id,
            employee_id=employee.id,
            start_at=start_at,
            price_cents=apply_employee_pricing(service, employee),
            status=BookingStatus.REQUESTED,
            source_channel=source_channel,
            preferences=preferences,
        )
        self.state.bookings.append(booking)
        return booking

    def confirm_booking(self, booking_id: str) -> Booking:
        return self._update_status(booking_id, BookingStatus.CONFIRMED)

    def cancel_booking(self, booking_id: str) -> Booking:
        return self._update_status(booking_id, BookingStatus.CANCELLED)

    def reschedule_booking(self, booking_id: str, new_start_at: datetime) -> Booking:
        booking = self._get_booking(booking_id)
        updated = replace(booking, start_at=new_start_at, status=BookingStatus.RESCHEDULED)
        index = self.state.bookings.index(booking)
        self.state.bookings[index] = updated
        return updated

    @property
    def _business_id(self) -> str:
        if self.state.business is None:
            raise ValueError("No hay negocio cargado en el estado")
        return self.state.business.id

    def _get_booking(self, booking_id: str) -> Booking:
        for booking in self.state.bookings:
            if booking.id == booking_id:
                return booking
        raise ValueError("Reserva no encontrada")

    def _get_customer(self, customer_id: str) -> Customer:
        for customer in self.state.customers:
            if customer.id == customer_id:
                return customer
        raise ValueError("Cliente no encontrado")

    def _get_service(self, service_id: str) -> Service:
        for service in self.state.services:
            if service.id == service_id:
                return service
        raise ValueError("Servicio no encontrado")

    def _get_employee(self, employee_id: str) -> Employee:
        for employee in self.state.employees:
            if employee.id == employee_id:
                return employee
        raise ValueError("Empleado no encontrado")

    def _update_status(self, booking_id: str, status: BookingStatus) -> Booking:
        booking = self._get_booking(booking_id)
        updated = replace(booking, status=status)
        index = self.state.bookings.index(booking)
        self.state.bookings[index] = updated
        return updated
