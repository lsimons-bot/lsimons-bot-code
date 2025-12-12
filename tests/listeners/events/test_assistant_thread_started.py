"""Tests for assistant_thread_started event handler."""

import logging
from unittest.mock import MagicMock

import pytest
from slack_sdk.errors import SlackApiError

from listeners.events.assistant_thread_started import (
    _generate_suggested_prompts,
    assistant_thread_started_handler,
)


class TestAssistantThreadStartedHandler:
    """Tests for assistant_thread_started_handler function."""

    @pytest.mark.asyncio
    async def test_handler_success(self) -> None:
        """Test successful thread started handler execution."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "assistant_thread_id": "thread-123",
            "channel_id": "C123",
            "user_id": "U123",
        }

        client.conversations_info.return_value = {
            "channel": {
                "name": "general",
                "topic": {"value": "General discussion"},
            }
        }

        await assistant_thread_started_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        client.conversations_info.assert_called_once_with(channel="C123")
        client.assistant.threads.set_status.assert_called_once_with(
            channel_id="C123",
            thread_id="thread-123",
            status="running",
        )
        client.assistant.threads.set_suggested_prompts.assert_called_once()

    @pytest.mark.asyncio
    async def test_handler_missing_thread_id(self) -> None:
        """Test handler with missing assistant_thread_id."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "channel_id": "C123",
            "user_id": "U123",
        }

        await assistant_thread_started_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.warning.assert_called()
        client.conversations_info.assert_not_called()

    @pytest.mark.asyncio
    async def test_handler_missing_channel_id(self) -> None:
        """Test handler with missing channel_id."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "assistant_thread_id": "thread-123",
            "user_id": "U123",
        }

        await assistant_thread_started_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.warning.assert_called()
        client.conversations_info.assert_not_called()

    @pytest.mark.asyncio
    async def test_handler_channel_info_api_error(self) -> None:
        """Test handler when channel info retrieval fails."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "assistant_thread_id": "thread-123",
            "channel_id": "C123",
            "user_id": "U123",
        }

        client.conversations_info.side_effect = SlackApiError(
            message="channel_not_found",
            response={"error": "channel_not_found"},
        )

        await assistant_thread_started_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.warning.assert_called()
        # Should still try to set status and prompts
        client.assistant.threads.set_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_handler_set_status_api_error(self) -> None:
        """Test handler when setting status fails."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "assistant_thread_id": "thread-123",
            "channel_id": "C123",
            "user_id": "U123",
        }

        client.conversations_info.return_value = {
            "channel": {
                "name": "general",
                "topic": {"value": "General discussion"},
            }
        }
        client.assistant.threads.set_status.side_effect = SlackApiError(
            message="invalid_argument",
            response={"error": "invalid_argument"},
        )

        await assistant_thread_started_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.warning.assert_called()
        # Should still try to set prompts
        client.assistant.threads.set_suggested_prompts.assert_called_once()

    @pytest.mark.asyncio
    async def test_handler_set_prompts_api_error(self) -> None:
        """Test handler when setting prompts fails."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "assistant_thread_id": "thread-123",
            "channel_id": "C123",
            "user_id": "U123",
        }

        client.conversations_info.return_value = {
            "channel": {
                "name": "general",
                "topic": {"value": "General discussion"},
            }
        }
        client.assistant.threads.set_suggested_prompts.side_effect = SlackApiError(
            message="invalid_argument",
            response={"error": "invalid_argument"},
        )

        await assistant_thread_started_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_handler_unexpected_error(self) -> None:
        """Test handler with unexpected error."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "assistant_thread_id": "thread-123",
            "channel_id": "C123",
            "user_id": "U123",
        }

        client.conversations_info.side_effect = RuntimeError("Unexpected error")

        await assistant_thread_started_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_handler_no_user_id(self) -> None:
        """Test handler without user_id (optional field)."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "assistant_thread_id": "thread-123",
            "channel_id": "C123",
        }

        client.conversations_info.return_value = {
            "channel": {
                "name": "general",
                "topic": {"value": "General discussion"},
            }
        }

        await assistant_thread_started_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        client.assistant.threads.set_status.assert_called_once()


class TestGenerateSuggestedPrompts:
    """Tests for _generate_suggested_prompts function."""

    def test_generate_prompts_basic(self) -> None:
        """Test generating basic prompts without channel topic."""
        prompts = _generate_suggested_prompts("general")

        assert len(prompts) == 3
        assert prompts[0]["title"] == "Summarize"
        assert prompts[1]["title"] == "Explain"
        assert prompts[2]["title"] == "Help"

    def test_generate_prompts_with_topic(self) -> None:
        """Test generating prompts with channel topic."""
        prompts = _generate_suggested_prompts("general", "General discussion")

        assert len(prompts) == 3
        assert prompts[0]["title"] == "Summarize"

    def test_generate_prompts_engineering_channel(self) -> None:
        """Test generating prompts for engineering channel."""
        prompts = _generate_suggested_prompts("engineering", "Engineering team discussions and code reviews")

        assert len(prompts) == 4
        assert prompts[0]["title"] == "Code Review"
        assert any(p["title"] == "Summarize" for p in prompts)

    def test_generate_prompts_dev_channel(self) -> None:
        """Test generating prompts for dev channel."""
        prompts = _generate_suggested_prompts("dev", "Development team channel")

        assert len(prompts) == 4
        assert prompts[0]["title"] == "Code Review"

    def test_generate_prompts_design_channel(self) -> None:
        """Test generating prompts for design channel."""
        prompts = _generate_suggested_prompts("design", "UI/UX design discussions and feedback")

        assert len(prompts) == 4
        assert prompts[0]["title"] == "Design Feedback"

    def test_generate_prompts_ux_channel(self) -> None:
        """Test generating prompts for UX channel."""
        prompts = _generate_suggested_prompts("ux", "User experience design channel")

        assert len(prompts) == 4
        assert prompts[0]["title"] == "Design Feedback"

    def test_generate_prompts_empty_topic(self) -> None:
        """Test generating prompts with empty topic."""
        prompts = _generate_suggested_prompts("general", "")

        assert len(prompts) == 3
        assert prompts[0]["title"] == "Summarize"

    def test_generate_prompts_none_topic(self) -> None:
        """Test generating prompts with None topic."""
        prompts = _generate_suggested_prompts("general", None)

        assert len(prompts) == 3
        assert prompts[0]["title"] == "Summarize"

    def test_generate_prompts_all_have_fields(self) -> None:
        """Test that all prompts have required fields."""
        prompts = _generate_suggested_prompts("engineering", "Engineering team discussions")

        for prompt in prompts:
            assert "title" in prompt
            assert "description" in prompt
            assert isinstance(prompt["title"], str)
            assert isinstance(prompt["description"], str)
            assert len(prompt["title"]) > 0
            assert len(prompt["description"]) > 0
