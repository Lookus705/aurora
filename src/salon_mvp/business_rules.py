from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .domain import Customer, Service


@dataclass(slots=True)
class PromotionRule:
    trigger_service_id: str
    suggested_service_id: str
    kind: str
    message: str
    first_visit_only: bool = False
    active: bool = True


@dataclass(slots=True)
class Recommendation:
    kind: str
    service_id: str
    service_name: str
    message: str


def build_recommendations(
    selected_service: Service,
    customer: Customer,
    available_services: Iterable[Service],
    rules: Iterable[PromotionRule],
) -> list[Recommendation]:
    catalog = {service.id: service for service in available_services}
    priority = {"upsell": 0, "cross_sell": 1}
    ordered: list[tuple[int, int, Recommendation]] = []

    for index, rule in enumerate(rules):
        if not rule.active:
            continue
        if rule.trigger_service_id != selected_service.id:
            continue
        if rule.first_visit_only and not customer.first_visit:
            continue

        suggested_service = catalog.get(rule.suggested_service_id)
        if suggested_service is None:
            continue

        recommendation = Recommendation(
            kind=rule.kind,
            service_id=suggested_service.id,
            service_name=suggested_service.name,
            message=rule.message,
        )
        ordered.append((priority.get(rule.kind, 99), index, recommendation))

    ordered.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in ordered]
