from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
import json

from .domain import (
    Booking,
    BookingStatus,
    Business,
    BusinessLocation,
    Customer,
    Employee,
    EmployeeSkill,
    Feedback,
    Role,
    Service,
    SkillLevel,
)


@dataclass(slots=True)
class AppState:
    business: Business | None = None
    locations: list[BusinessLocation] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    employees: list[Employee] = field(default_factory=list)
    customers: list[Customer] = field(default_factory=list)
    bookings: list[Booking] = field(default_factory=list)
    feedbacks: list[Feedback] = field(default_factory=list)


def _skill_to_dict(skill: EmployeeSkill) -> dict:
    return {
        "name": skill.name,
        "level": skill.level.value,
        "bonus_percent": skill.bonus_percent,
        "bonus_amount_cents": skill.bonus_amount_cents,
    }


def _skill_from_dict(data: dict) -> EmployeeSkill:
    return EmployeeSkill(
        name=data["name"],
        level=SkillLevel(data["level"]),
        bonus_percent=data.get("bonus_percent", 0.0),
        bonus_amount_cents=data.get("bonus_amount_cents", 0),
    )


def _booking_to_dict(booking: Booking) -> dict:
    payload = asdict(booking)
    payload["start_at"] = booking.start_at.isoformat()
    payload["status"] = booking.status.value
    return payload


def _booking_from_dict(data: dict) -> Booking:
    return Booking(
        id=data["id"],
        business_id=data["business_id"],
        customer_id=data["customer_id"],
        service_id=data["service_id"],
        location_id=data["location_id"],
        employee_id=data["employee_id"],
        start_at=datetime.fromisoformat(data["start_at"]),
        price_cents=data["price_cents"],
        status=BookingStatus(data.get("status", BookingStatus.REQUESTED.value)),
        source_channel=data.get("source_channel", "chat"),
        preferences=data.get("preferences", ""),
    )


def _employee_to_dict(employee: Employee) -> dict:
    payload = asdict(employee)
    payload["skills"] = [_skill_to_dict(skill) for skill in employee.skills]
    return payload


def _employee_from_dict(data: dict) -> Employee:
    return Employee(
        id=data["id"],
        business_id=data["business_id"],
        name=data["name"],
        active=data.get("active", True),
        skills=[_skill_from_dict(skill) for skill in data.get("skills", [])],
    )


def _business_to_dict(business: Business | None) -> dict | None:
    return asdict(business) if business is not None else None


def _business_from_dict(data: dict | None) -> Business | None:
    if data is None:
        return None
    return Business(**data)


class JsonStateStore:
    def __init__(self, path: Path | str):
        self.path = Path(path)

    def save(self, state: AppState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "business": _business_to_dict(state.business),
            "locations": [asdict(location) for location in state.locations],
            "services": [asdict(service) for service in state.services],
            "employees": [_employee_to_dict(employee) for employee in state.employees],
            "customers": [asdict(customer) for customer in state.customers],
            "bookings": [_booking_to_dict(booking) for booking in state.bookings],
            "feedbacks": [asdict(feedback) for feedback in state.feedbacks],
        }

        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        tmp_path.replace(self.path)

    def load(self) -> AppState:
        if not self.path.exists():
            return AppState()

        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return AppState(
            business=_business_from_dict(payload.get("business")),
            locations=[BusinessLocation(**location) for location in payload.get("locations", [])],
            services=[Service(**service) for service in payload.get("services", [])],
            employees=[_employee_from_dict(employee) for employee in payload.get("employees", [])],
            customers=[Customer(**customer) for customer in payload.get("customers", [])],
            bookings=[_booking_from_dict(booking) for booking in payload.get("bookings", [])],
            feedbacks=[Feedback(**feedback) for feedback in payload.get("feedbacks", [])],
        )
