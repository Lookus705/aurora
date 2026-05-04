"""Aurora: MVP local para salones y clínicas."""

from .booking_service import BookingService
from .business_rules import PromotionRule, Recommendation, build_recommendations
from .chat_flow import (
    BookingChatFlow,
    IntakeStep,
    build_chat_handoff_message,
    build_client_chat_journey,
    build_employee_booking_notification,
)
from .chat_orchestrator import ChatOrchestrationResult, ChatOrchestrator
from .admin_views import AdminFilter, OperationalDashboard, build_operational_dashboard
from .demo import SalonDemo, build_demo_state
from .dashboard import DashboardSummary, ReputationSummary, build_owner_dashboard, summarize_reputation
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
    apply_employee_pricing,
    can_employee_handle_service,
    format_euro,
    make_booking_summary,
)
from .integrations import IntegrationMessage, MessagingAdapter, TelegramAdapter, WhatsAppAdapter, build_messaging_adapter
from .reminders import ReminderTask, build_booking_reminders
from .scheduling import next_available_slot, slot_is_available
from .storage import AppState, JsonStateStore

__all__ = [
    "AppState",
    "Booking",
    "BookingChatFlow",
    "BookingService",
    "BookingStatus",
    "Business",
    "BusinessLocation",
    "ChatOrchestrationResult",
    "ChatOrchestrator",
    "AdminFilter",
    "OperationalDashboard",
    "build_operational_dashboard",
    "SalonDemo",
    "build_demo_state",
    "Customer",
    "DashboardSummary",
    "Employee",
    "EmployeeSkill",
    "Feedback",
    "IntakeStep",
    "JsonStateStore",
    "MessagingAdapter",
    "PromotionRule",
    "Recommendation",
    "ReputationSummary",
    "Role",
    "ReminderTask",
    "Service",
    "SkillLevel",
    "TelegramAdapter",
    "WhatsAppAdapter",
    "IntegrationMessage",
    "apply_employee_pricing",
    "build_chat_handoff_message",
    "build_client_chat_journey",
    "build_employee_booking_notification",
    "build_owner_dashboard",
    "build_recommendations",
    "build_booking_reminders",
    "build_messaging_adapter",
    "can_employee_handle_service",
    "format_euro",
    "make_booking_summary",
    "next_available_slot",
    "slot_is_available",
    "summarize_reputation",
]
