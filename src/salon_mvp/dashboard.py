from __future__ import annotations

from dataclasses import dataclass
from collections import Counter, defaultdict

from .domain import Booking, BookingStatus, Customer, Employee, Feedback, Service, format_euro


@dataclass(slots=True)
class ReputationSummary:
    total_feedbacks: int
    overall_average: float
    local_average: float
    attention_average: float
    employee_average: float
    best_dimension: str


@dataclass(slots=True)
class DashboardSummary:
    business_name: str
    total_completed_bookings: int
    total_revenue_cents: int
    total_time_minutes: int
    top_customer: str
    top_employee: str
    top_service: str
    highest_profit_service: str
    customer_ranking: list[str]
    employee_ranking: list[str]
    service_ranking: list[str]
    reputation: ReputationSummary

    def as_text(self) -> str:
        return "\n".join(
            [
                f"Dashboard de {self.business_name}",
                f"- Reservas completadas: {self.total_completed_bookings}",
                f"- Facturación: {format_euro(self.total_revenue_cents)}",
                f"- Tiempo dedicado: {self.total_time_minutes} min",
                f"- Cliente top: {self.top_customer}",
                f"- Empleado top: {self.top_employee}",
                f"- Servicio top: {self.top_service}",
                f"- Servicio más rentable: {self.highest_profit_service}",
                f"- Reputación global: {self.reputation.overall_average:.1f}/5",
            ]
        )


def summarize_reputation(feedbacks: list[Feedback]) -> ReputationSummary:
    if not feedbacks:
        return ReputationSummary(0, 0.0, 0.0, 0.0, 0.0, "sin datos")

    total_feedbacks = len(feedbacks)
    local_average = round(sum(f.local_rating for f in feedbacks) / total_feedbacks, 2)
    attention_average = round(sum(f.attention_rating for f in feedbacks) / total_feedbacks, 2)
    employee_average = round(sum(f.employee_rating for f in feedbacks) / total_feedbacks, 2)
    overall_average = round((local_average + attention_average + employee_average) / 3, 2)

    averages = {
        "local": local_average,
        "atención": attention_average,
        "empleado": employee_average,
    }
    best_dimension = max(averages, key=averages.get)

    return ReputationSummary(
        total_feedbacks=total_feedbacks,
        overall_average=overall_average,
        local_average=local_average,
        attention_average=attention_average,
        employee_average=employee_average,
        best_dimension=best_dimension,
    )


def build_owner_dashboard(
    business_name: str,
    bookings: list[Booking],
    customers: list[Customer],
    employees: list[Employee],
    services: list[Service],
    feedbacks: list[Feedback],
) -> DashboardSummary:
    completed_bookings = [booking for booking in bookings if booking.status == BookingStatus.COMPLETED]

    customer_lookup = {customer.id: customer for customer in customers}
    employee_lookup = {employee.id: employee for employee in employees}
    service_lookup = {service.id: service for service in services}

    customer_counts: Counter[str] = Counter()
    employee_counts: Counter[str] = Counter()
    service_counts: Counter[str] = Counter()
    service_revenue: defaultdict[str, int] = defaultdict(int)
    total_revenue_cents = 0
    total_time_minutes = 0

    for booking in completed_bookings:
        customer_counts[booking.customer_id] += 1
        employee_counts[booking.employee_id] += 1
        service_counts[booking.service_id] += 1
        service_revenue[booking.service_id] += booking.price_cents
        total_revenue_cents += booking.price_cents

        service = service_lookup.get(booking.service_id)
        if service is not None:
            total_time_minutes += service.duration_minutes

    def ranking_lines(counts: Counter[str], lookup: dict[str, object], label_getter) -> list[str]:
        ranked_ids = sorted(counts.items(), key=lambda item: (-item[1], str(lookup[item[0]]).lower() if item[0] in lookup else item[0]))
        lines: list[str] = []
        for item_id, count in ranked_ids:
            entity = lookup.get(item_id)
            name = label_getter(entity) if entity is not None else item_id
            lines.append(f"{name}: {count}")
        return lines

    customer_ranking = ranking_lines(customer_counts, customer_lookup, lambda entity: entity.display_name)
    employee_ranking = ranking_lines(employee_counts, employee_lookup, lambda entity: entity.name)
    service_ranking = ranking_lines(service_counts, service_lookup, lambda entity: entity.name)

    top_customer = customer_ranking[0].split(":", 1)[0] if customer_ranking else "sin datos"
    top_employee = employee_ranking[0].split(":", 1)[0] if employee_ranking else "sin datos"
    top_service = service_ranking[0].split(":", 1)[0] if service_ranking else "sin datos"

    if service_revenue:
        highest_profit_service_id = max(service_revenue.items(), key=lambda item: (item[1], service_lookup[item[0]].name))[0]
        highest_profit_service = service_lookup[highest_profit_service_id].name
    else:
        highest_profit_service = "sin datos"

    reputation = summarize_reputation(feedbacks)

    return DashboardSummary(
        business_name=business_name,
        total_completed_bookings=len(completed_bookings),
        total_revenue_cents=total_revenue_cents,
        total_time_minutes=total_time_minutes,
        top_customer=top_customer,
        top_employee=top_employee,
        top_service=top_service,
        highest_profit_service=highest_profit_service,
        customer_ranking=customer_ranking,
        employee_ranking=employee_ranking,
        service_ranking=service_ranking,
        reputation=reputation,
    )
