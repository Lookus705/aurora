from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class IntegrationMessage:
    channel: str
    recipient_id: str
    subject: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


class MessagingAdapter:
    channel_name: str = ""

    def format_message(self, recipient_id: str, text: str, subject: str) -> IntegrationMessage:
        raise NotImplementedError


class TelegramAdapter(MessagingAdapter):
    channel_name = "telegram"

    def format_message(self, recipient_id: str, text: str, subject: str) -> IntegrationMessage:
        return IntegrationMessage(
            channel=self.channel_name,
            recipient_id=recipient_id,
            subject=subject,
            text=text,
            metadata={"parse_mode": "Markdown"},
        )


class WhatsAppAdapter(MessagingAdapter):
    channel_name = "whatsapp"

    def format_message(self, recipient_id: str, text: str, subject: str) -> IntegrationMessage:
        return IntegrationMessage(
            channel=self.channel_name,
            recipient_id=recipient_id,
            subject=subject,
            text=text,
            metadata={},
        )


def build_messaging_adapter(channel: str) -> MessagingAdapter:
    normalized = channel.strip().lower()
    if normalized == "telegram":
        return TelegramAdapter()
    if normalized == "whatsapp":
        return WhatsAppAdapter()
    raise ValueError(f"Canal no soportado: {channel}")
