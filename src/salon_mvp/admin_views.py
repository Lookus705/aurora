from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .dashboard import DashboardSummary, build_owner_dashboard
from .domain import Booking, Customer, Employee, Feedback, Service


@dataclass(slots=True)
class AdminFilter:
    start_date: datetime | None = None
    end_date: datetime | None = None
    location_id: str | None = None


@dataclass(slots=True)
class OperationalDashboard(DashboardSummary):
    active_filter: AdminFilter | None = None
    location_label: str = "all_locations"

    def as_text(self) -> str:
        lines = [DashboardSummary.as_text(self), f"- Sede: {self.location_label}"]
        if self.active_filter is not None:
            if self.active_filter.start_date is not None:
                lines.append(f"- Desde: {self.active_filter.start_date.strftime('%Y-%m-%d')}")
            if self.active_filter.end_date is not None:
                lines.append(f"- Hasta: {self.active_filter.end_date.strftime('%Y-%m-%d')}")
        return "\n".join(lines)


def _apply_filters(bookings: list[Booking], filters: AdminFilter) -> list[Booking]:
    filtered = list(bookings)
    if filters.start_date is not None:
        filtered = [booking for booking in filtered if booking.start_at >= filters.start_date]
    if filters.end_date is not None:
        filtered = [booking for booking in filtered if booking.start_at <= filters.end_date]
    if filters.location_id is not None:
        filtered = [booking for booking in filtered if booking.location_id == filters.location_id]
    return filtered


def build_operational_dashboard(
    business_name: str,
    bookings: list[Booking],
    customers: list[Customer],
    employees: list[Employee],
    services: list[Service],
    feedbacks: list[Feedback],
    filters: AdminFilter | None = None,
) -> OperationalDashboard:
    active_filter = filters or AdminFilter()
    filtered_bookings = _apply_filters(bookings, active_filter)
    base = build_owner_dashboard(
        business_name=business_name,
        bookings=filtered_bookings,
        customers=customers,
        employees=employees,
        services=services,
        feedbacks=feedbacks,
    )
    return OperationalDashboard(
        business_name=base.business_name,
        total_completed_bookings=base.total_completed_bookings,
        total_revenue_cents=base.total_revenue_cents,
        total_time_minutes=base.total_time_minutes,
        top_customer=base.top_customer,
        top_employee=base.top_employee,
        top_service=base.top_service,
        highest_profit_service=base.highest_profit_service,
        customer_ranking=base.customer_ranking,
        employee_ranking=base.employee_ranking,
        service_ranking=base.service_ranking,
        reputation=base.reputation,
        active_filter=active_filter,
        location_label=active_filter.location_id or "all_locations",
    )
