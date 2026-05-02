import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from salon_mvp.integrations import (
    IntegrationMessage,
    TelegramAdapter,
    WhatsAppAdapter,
    build_messaging_adapter,
)


class IntegrationContractsTests(unittest.TestCase):
    def test_build_messaging_adapter_returns_expected_channel_adapter(self):
        whatsapp = build_messaging_adapter("whatsapp")
        telegram = build_messaging_adapter("telegram")

        self.assertIsInstance(whatsapp, WhatsAppAdapter)
        self.assertIsInstance(telegram, TelegramAdapter)
        self.assertEqual(whatsapp.channel_name, "whatsapp")
        self.assertEqual(telegram.channel_name, "telegram")

    def test_telegram_adapter_formats_message_with_test_friendly_metadata(self):
        adapter = build_messaging_adapter("telegram")

        message = adapter.format_message(
            recipient_id="cus_1",
            text="*Cita confirmada* para Laura",
            subject="booking_confirmation",
        )

        self.assertIsInstance(message, IntegrationMessage)
        self.assertEqual(message.channel, "telegram")
        self.assertEqual(message.recipient_id, "cus_1")
        self.assertEqual(message.subject, "booking_confirmation")
        self.assertEqual(message.text, "*Cita confirmada* para Laura")
        self.assertEqual(message.metadata.get("parse_mode"), "Markdown")

    def test_whatsapp_adapter_formats_message_without_telegram_metadata(self):
        adapter = build_messaging_adapter("whatsapp")

        message = adapter.format_message(
            recipient_id="cus_1",
            text="Cita confirmada para Laura",
            subject="booking_confirmation",
        )

        self.assertEqual(message.channel, "whatsapp")
        self.assertEqual(message.metadata, {})
        self.assertEqual(message.text, "Cita confirmada para Laura")

    def test_build_messaging_adapter_rejects_unknown_channel(self):
        with self.assertRaises(ValueError):
            build_messaging_adapter("sms")


if __name__ == "__main__":
    unittest.main()
