import sys
from pathlib import Path
import unittest
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.domain import Booking, BookingStatus, Customer, Employee, Feedback, Service
from salon_mvp.dashboard import build_owner_dashboard, summarize_reputation, DashboardSummary


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.customers = [
            Customer(id="cus_1", business_id="biz_1", display_name="Laura"),
            Customer(id="cus_2", business_id="biz_1", display_name="Marta"),
        ]
        self.employees = [
            Employee(id="emp_1", business_id="biz_1", name="Ana"),
            Employee(id="emp_2", business_id="biz_1", name="Sara"),
        ]
        self.services = [
            Service(id="srv_1", business_id="biz_1", name="Limpieza facial", base_price_cents=5000, duration_minutes=45),
            Service(id="srv_2", business_id="biz_1", name="Masaje relajante", base_price_cents=7000, duration_minutes=60),
        ]
        self.bookings = [
            Booking(
                id="boo_1",
                business_id="biz_1",
                customer_id="cus_1",
                service_id="srv_1",
                location_id="loc_1",
                employee_id="emp_1",
                start_at=datetime(2026, 5, 1, 10, 0),
                price_cents=5500,
                status=BookingStatus.COMPLETED,
            ),
            Booking(
                id="boo_2",
                business_id="biz_1",
                customer_id="cus_1",
                service_id="srv_2",
                location_id="loc_1",
                employee_id="emp_1",
                start_at=datetime(2026, 5, 1, 11, 0),
                price_cents=7000,
                status=BookingStatus.COMPLETED,
            ),
            Booking(
                id="boo_3",
                business_id="biz_1",
                customer_id="cus_2",
                service_id="srv_2",
                location_id="loc_1",
                employee_id="emp_2",
                start_at=datetime(2026, 5, 1, 12, 0),
                price_cents=7000,
                status=BookingStatus.COMPLETED,
            ),
            Booking(
                id="boo_4",
                business_id="biz_1",
                customer_id="cus_2",
                service_id="srv_2",
                location_id="loc_1",
                employee_id="emp_2",
                start_at=datetime(2026, 5, 1, 13, 0),
                price_cents=7000,
                status=BookingStatus.CANCELLED,
            ),
        ]
        self.feedbacks = [
            Feedback(booking_id="boo_1", local_rating=5, attention_rating=4, employee_rating=5),
            Feedback(booking_id="boo_2", local_rating=4, attention_rating=5, employee_rating=5),
            Feedback(booking_id="boo_3", local_rating=3, attention_rating=4, employee_rating=4),
        ]

    def test_build_owner_dashboard_prioritizes_metrics_for_owner_view(self):
        summary = build_owner_dashboard(
            business_name="Belleza & Salud",
            bookings=self.bookings,
            customers=self.customers,
            employees=self.employees,
            services=self.services,
            feedbacks=self.feedbacks,
        )

        self.assertIsInstance(summary, DashboardSummary)
        self.assertEqual(summary.business_name, "Belleza & Salud")
        self.assertEqual(summary.total_completed_bookings, 3)
        self.assertEqual(summary.total_revenue_cents, 19500)
        self.assertEqual(summary.total_time_minutes, 165)
        self.assertEqual(summary.top_customer, "Laura")
        self.assertEqual(summary.top_employee, "Ana")
        self.assertEqual(summary.top_service, "Masaje relajante")
        self.assertEqual(summary.highest_profit_service, "Masaje relajante")
        self.assertIn("Laura", summary.customer_ranking[0])
        self.assertIn("Ana", summary.employee_ranking[0])
        self.assertIn("Masaje relajante", summary.service_ranking[0])
        self.assertIn("195.00€", summary.as_text())
        self.assertIn("4.3/5", summary.as_text())

    def test_summarize_reputation_uses_feedback_breakdown(self):
        reputation = summarize_reputation(self.feedbacks)

        self.assertEqual(reputation.total_feedbacks, 3)
        self.assertAlmostEqual(reputation.overall_average, 4.33, places=2)
        self.assertEqual(reputation.local_average, 4.0)
        self.assertAlmostEqual(reputation.attention_average, 4.33, places=2)
        self.assertAlmostEqual(reputation.employee_average, 4.67, places=2)
        self.assertEqual(reputation.best_dimension, "empleado")


if __name__ == "__main__":
    unittest.main()
