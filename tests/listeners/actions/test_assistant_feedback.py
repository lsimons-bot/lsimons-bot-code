"""Tests for assistant_feedback action handler."""

import logging
from unittest.mock import MagicMock

import pytest
from slack_sdk.errors import SlackApiError

from listeners.actions.assistant_feedback import (
    _log_feedback_metrics,
    assistant_feedback_handler,
)


class TestAssistantFeedbackHandler:
    """Tests for assistant_feedback_handler function."""

    @pytest.mark.asyncio
    async def test_handler_thumbs_up(self) -> None:
        """Test handling thumbs up feedback."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "actions": [{"value": "feedback_thumbs_up"}],
            "user": {"id": "U123"},
            "channel": {"id": "C123"},
            "message": {"ts": "1234567890.123456"},
            "team": {"id": "T123"},
        }

        await assistant_feedback_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        client.chat_postEphemeral.assert_called_once()
        test_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_handler_thumbs_down(self) -> None:
        """Test handling thumbs down feedback."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "actions": [{"value": "feedback_thumbs_down"}],
            "user": {"id": "U456"},
            "channel": {"id": "C456"},
            "message": {"ts": "1234567891.123456"},
            "team": {"id": "T123"},
        }

        await assistant_feedback_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        client.chat_postEphemeral.assert_called_once()
        test_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_handler_missing_action_value(self) -> None:
        """Test handler with missing action value."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "actions": [{}],
            "user": {"id": "U123"},
            "channel": {"id": "C123"},
            "message": {"ts": "1234567890.123456"},
            "team": {"id": "T123"},
        }

        await assistant_feedback_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.warning.assert_called()
        client.chat_postEphemeral.assert_not_called()

    @pytest.mark.asyncio
    async def test_handler_missing_user_id(self) -> None:
        """Test handler with missing user_id."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "actions": [{"value": "feedback_thumbs_up"}],
            "user": {},
            "channel": {"id": "C123"},
            "message": {"ts": "1234567890.123456"},
            "team": {"id": "T123"},
        }

        await assistant_feedback_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.warning.assert_called()
        client.chat_postEphemeral.assert_not_called()

    @pytest.mark.asyncio
    async def test_handler_missing_actions_array(self) -> None:
        """Test handler with missing actions array."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "user": {"id": "U123"},
            "channel": {"id": "C123"},
            "message": {"ts": "1234567890.123456"},
            "team": {"id": "T123"},
        }

        await assistant_feedback_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_handler_ephemeral_message_failure(self) -> None:
        """Test handler when sending ephemeral message fails."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "actions": [{"value": "feedback_thumbs_up"}],
            "user": {"id": "U123"},
            "channel": {"id": "C123"},
            "message": {"ts": "1234567890.123456"},
            "team": {"id": "T123"},
        }

        client.chat_postEphemeral.side_effect = SlackApiError(
            message="channel_not_found",
            response={"error": "channel_not_found"},
        )

        await assistant_feedback_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_handler_unexpected_error(self) -> None:
        """Test handler with unexpected error."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "actions": [{"value": "feedback_thumbs_up"}],
            "user": {"id": "U123"},
            "channel": {"id": "C123"},
            "message": {"ts": "1234567890.123456"},
            "team": {"id": "T123"},
        }

        client.chat_postEphemeral.side_effect = RuntimeError("Unexpected error")

        await assistant_feedback_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        test_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_handler_without_optional_fields(self) -> None:
        """Test handler without optional fields like team_id."""
        ack = MagicMock()
        client = MagicMock()
        test_logger = MagicMock(spec=logging.Logger)

        body = {
            "actions": [{"value": "feedback_thumbs_up"}],
            "user": {"id": "U123"},
            "channel": {"id": "C123"},
            "message": {"ts": "1234567890.123456"},
        }

        await assistant_feedback_handler(ack, body, client, test_logger)

        ack.assert_called_once()
        client.chat_postEphemeral.assert_called_once()


class TestLogFeedbackMetrics:
    """Tests for _log_feedback_metrics function."""

    def test_log_feedback_metrics_positive(self) -> None:
        """Test logging positive feedback metrics."""
        test_logger = MagicMock(spec=logging.Logger)

        _log_feedback_metrics(
            feedback_type="positive",
            user_id="U123",
            channel_id="C123",
            response_ts="1234567890.123456",
            team_id="T123",
            logger_=test_logger,
        )

        test_logger.info.assert_called_once()
        call_args = test_logger.info.call_args
        assert call_args[0][0] == "feedback_event"

    def test_log_feedback_metrics_negative(self) -> None:
        """Test logging negative feedback metrics."""
        test_logger = MagicMock(spec=logging.Logger)

        _log_feedback_metrics(
            feedback_type="negative",
            user_id="U456",
            channel_id="C456",
            response_ts="1234567891.123456",
            team_id="T456",
            logger_=test_logger,
        )

        test_logger.info.assert_called_once()
        call_args = test_logger.info.call_args
        assert call_args[0][0] == "feedback_event"

    def test_log_feedback_metrics_with_none_values(self) -> None:
        """Test logging metrics with None values."""
        test_logger = MagicMock(spec=logging.Logger)

        _log_feedback_metrics(
            feedback_type="positive",
            user_id=None,
            channel_id=None,
            response_ts=None,
            team_id=None,
            logger_=test_logger,
        )

        test_logger.info.assert_called_once()
