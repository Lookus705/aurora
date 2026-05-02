import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.domain import Customer, Service
from salon_mvp.business_rules import PromotionRule, build_recommendations


class BusinessRulesTests(unittest.TestCase):
    def setUp(self):
        self.cut = Service(
            id="srv_cut",
            business_id="biz_1",
            name="Corte de pelo",
            base_price_cents=2000,
            duration_minutes=30,
        )
        self.color = Service(
            id="srv_color",
            business_id="biz_1",
            name="Coloración premium",
            base_price_cents=4500,
            duration_minutes=60,
        )
        self.treatment = Service(
            id="srv_treatment",
            business_id="biz_1",
            name="Tratamiento hidratante",
            base_price_cents=3500,
            duration_minutes=45,
        )
        self.customer = Customer(id="cus_1", business_id="biz_1", display_name="Marta", first_visit=True)

    def test_build_recommendations_returns_active_matches_in_order(self):
        rules = [
            PromotionRule(
                trigger_service_id=self.cut.id,
                suggested_service_id=self.treatment.id,
                kind="cross_sell",
                message="Te puede venir bien tras el corte.",
            ),
            PromotionRule(
                trigger_service_id=self.cut.id,
                suggested_service_id=self.color.id,
                kind="upsell",
                message="Si quieres un cambio más completo, prueba coloración.",
            ),
        ]

        recommendations = build_recommendations(
            selected_service=self.cut,
            customer=self.customer,
            available_services=[self.cut, self.color, self.treatment],
            rules=rules,
        )

        self.assertEqual([item.kind for item in recommendations], ["upsell", "cross_sell"])
        self.assertEqual([item.service_name for item in recommendations], ["Coloración premium", "Tratamiento hidratante"])
        self.assertIn("cambio más completo", recommendations[0].message)

    def test_build_recommendations_skips_first_visit_only_rules_for_returning_customers(self):
        self.customer.first_visit = False
        rules = [
            PromotionRule(
                trigger_service_id=self.cut.id,
                suggested_service_id=self.color.id,
                kind="upsell",
                message="Oferta para primera visita.",
                first_visit_only=True,
            )
        ]

        recommendations = build_recommendations(
            selected_service=self.cut,
            customer=self.customer,
            available_services=[self.cut, self.color],
            rules=rules,
        )

        self.assertEqual(recommendations, [])

    def test_build_recommendations_ignores_rules_without_catalog_match(self):
        rules = [
            PromotionRule(
                trigger_service_id=self.cut.id,
                suggested_service_id="srv_missing",
                kind="cross_sell",
                message="Servicio no disponible.",
            )
        ]

        recommendations = build_recommendations(
            selected_service=self.cut,
            customer=self.customer,
            available_services=[self.cut, self.color],
            rules=rules,
        )

        self.assertEqual(recommendations, [])


if __name__ == "__main__":
    unittest.main()
