import sys
from pathlib import Path
import unittest
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.admin_views import AdminFilter, build_operational_dashboard
from salon_mvp.domain import Booking, BookingStatus, Customer, Employee, Feedback, Service


class AdminViewsTests(unittest.TestCase):
    def setUp(self):
        self.customers = [
            Customer(id="cus_1", business_id="biz_1", display_name="Laura"),
            Customer(id="cus_2", business_id="biz_1", display_name="Marta"),
        ]
        self.employees = [
            Employee(id="emp_1", business_id="biz_1", name="Ana"),
            Employee(id="emp_2", business_id="biz_1", name="Sofía"),
        ]
        self.services = [
            Service(id="srv_1", business_id="biz_1", name="Limpieza facial", base_price_cents=5000, duration_minutes=45),
            Service(id="srv_2", business_id="biz_1", name="Masaje relajante", base_price_cents=6500, duration_minutes=60),
        ]
        self.bookings = [
            Booking(
                id="boo_1",
                business_id="biz_1",
                customer_id="cus_1",
                service_id="srv_1",
                location_id="loc_centro",
                employee_id="emp_1",
                start_at=datetime(2026, 5, 2, 10, 0),
                price_cents=5000,
                status=BookingStatus.COMPLETED,
            ),
            Booking(
                id="boo_2",
                business_id="biz_1",
                customer_id="cus_1",
                service_id="srv_2",
                location_id="loc_centro",
                employee_id="emp_1",
                start_at=datetime(2026, 5, 3, 12, 0),
                price_cents=6500,
                status=BookingStatus.COMPLETED,
            ),
            Booking(
                id="boo_3",
                business_id="biz_1",
                customer_id="cus_2",
                service_id="srv_1",
                location_id="loc_norte",
                employee_id="emp_2",
                start_at=datetime(2026, 5, 3, 15, 0),
                price_cents=5000,
                status=BookingStatus.COMPLETED,
            ),
        ]
        self.feedbacks = [
            Feedback(booking_id="boo_1", local_rating=5, attention_rating=5, employee_rating=4),
            Feedback(booking_id="boo_2", local_rating=4, attention_rating=5, employee_rating=5),
            Feedback(booking_id="boo_3", local_rating=4, attention_rating=4, employee_rating=4),
        ]

    def test_build_operational_dashboard_filters_by_date_and_location(self):
        dashboard = build_operational_dashboard(
            business_name="Belleza & Salud",
            bookings=self.bookings,
            customers=self.customers,
            employees=self.employees,
            services=self.services,
            feedbacks=self.feedbacks,
            filters=AdminFilter(start_date=datetime(2026, 5, 3), end_date=datetime(2026, 5, 3, 23, 59), location_id="loc_centro"),
        )

        self.assertEqual(dashboard.total_completed_bookings, 1)
        self.assertEqual(dashboard.top_customer, "Laura")
        self.assertEqual(dashboard.top_employee, "Ana")
        self.assertEqual(dashboard.top_service, "Masaje relajante")
        self.assertEqual(dashboard.location_label, "loc_centro")
        self.assertIn("2026-05-03", dashboard.as_text())

    def test_build_operational_dashboard_uses_all_data_when_no_filters_applied(self):
        dashboard = build_operational_dashboard(
            business_name="Belleza & Salud",
            bookings=self.bookings,
            customers=self.customers,
            employees=self.employees,
            services=self.services,
            feedbacks=self.feedbacks,
            filters=AdminFilter(),
        )

        self.assertEqual(dashboard.total_completed_bookings, 3)
        self.assertEqual(dashboard.total_revenue_cents, 16500)
        self.assertIn("Laura", dashboard.customer_ranking[0])
        self.assertIn("Ana", dashboard.employee_ranking[0])
        self.assertIn("Limpieza facial", dashboard.service_ranking[0])
        self.assertIn("Belleza & Salud", dashboard.as_text())


if __name__ == "__main__":
    unittest.main()
