from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterable
from uuid import uuid4


class Role(str, Enum):
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class SkillLevel(str, Enum):
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    EXPERT = "expert"


class BookingStatus(str, Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"
    PENDING_FEEDBACK = "pending_feedback"


@dataclass(slots=True)
class Business:
    id: str
    name: str
    description: str = ""


@dataclass(slots=True)
class BusinessLocation:
    id: str
    business_id: str
    name: str
    address: str = ""


@dataclass(slots=True)
class Service:
    id: str
    business_id: str
    name: str
    base_price_cents: int
    duration_minutes: int
    location_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EmployeeSkill:
    name: str
    level: SkillLevel
    bonus_percent: float = 0.0
    bonus_amount_cents: int = 0

    def describe_bonus(self) -> str:
        parts: list[str] = []
        if self.bonus_percent:
            parts.append(f"+{self.bonus_percent:.1f}%")
        if self.bonus_amount_cents:
            parts.append(f"+{self.bonus_amount_cents / 100:.2f}€")
        return " ".join(parts) if parts else "sin recargo"


@dataclass(slots=True)
class Employee:
    id: str
    business_id: str
    name: str
    active: bool = True
    skills: list[EmployeeSkill] = field(default_factory=list)

    def has_skill(self, service_name: str) -> bool:
        service_name_lower = service_name.lower()
        return any(
            skill.name.lower() in service_name_lower or service_name_lower in skill.name.lower()
            for skill in self.skills
        )


@dataclass(slots=True)
class Customer:
    id: str
    business_id: str
    display_name: str
    phone: str | None = None
    first_visit: bool = True
    notes: str = ""


@dataclass(slots=True)
class Booking:
    id: str
    business_id: str
    customer_id: str
    service_id: str
    location_id: str
    employee_id: str
    start_at: datetime
    price_cents: int
    status: BookingStatus = BookingStatus.REQUESTED
    source_channel: str = "chat"
    preferences: str = ""

    def summary(self) -> str:
        return (
            f"booking={self.id} customer={self.customer_id} service={self.service_id} "
            f"employee={self.employee_id} start_at={self.start_at.isoformat()} "
            f"price={self.price_cents / 100:.2f}€ status={self.status.value}"
        )


@dataclass(slots=True)
class Feedback:
    booking_id: str
    local_rating: int
    attention_rating: int
    employee_rating: int
    comment: str = ""

    def average_rating(self) -> float:
        return (self.local_rating + self.attention_rating + self.employee_rating) / 3


def apply_employee_pricing(service: Service, employee: Employee | None) -> int:
    price = service.base_price_cents
    if employee is None:
        return price

    bonus_percent = 0.0
    bonus_amount = 0
    for skill in employee.skills:
        bonus_percent += skill.bonus_percent
        bonus_amount += skill.bonus_amount_cents

    price = int(round(price * (1 + bonus_percent / 100))) + bonus_amount
    return max(price, 0)


def can_employee_handle_service(employee: Employee, service: Service) -> bool:
    if not employee.active:
        return False
    if not employee.skills:
        return True
    return employee.has_skill(service.name)


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def format_euro(cents: int) -> str:
    return f"{cents / 100:.2f}€"


def make_booking_summary(booking: Booking, customer: Customer, service: Service, employee: Employee) -> str:
    return (
        f"{customer.display_name} tiene cita para {service.name} con {employee.name} "
        f"el {booking.start_at.strftime('%Y-%m-%d %H:%M')} por {format_euro(booking.price_cents)}"
    )


def any_skill_matches(employee: Employee, candidates: Iterable[str]) -> bool:
    candidate_set = {candidate.lower() for candidate in candidates}
    return any(skill.name.lower() in candidate_set for skill in employee.skills)
