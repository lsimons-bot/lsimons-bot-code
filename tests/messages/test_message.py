import pytest

from lsimons_bot.messages.message import message


class TestMessage:
    @pytest.mark.asyncio
    async def test_message_happy_path(self) -> None:
        """Test that message handles regular user message."""
        body = {
            "event": {
                "type": "message",
                "text": "hello world",
                "user": "U123",
            }
        }
        await message(body)

    @pytest.mark.asyncio
    async def test_message_ignores_bot_messages(self) -> None:
        """Test that message ignores messages from bots."""
        body = {
            "event": {
                "type": "message",
                "text": "bot message",
                "bot_id": "B123",
            }
        }
        await message(body)

    @pytest.mark.asyncio
    async def test_message_handles_empty_event(self) -> None:
        """Test that message handles missing event field."""
        body = {}
        await message(body)

    @pytest.mark.asyncio
    async def test_message_handles_missing_text(self) -> None:
        """Test that message handles missing text field."""
        body = {"event": {"type": "message", "user": "U123"}}
        await message(body)
