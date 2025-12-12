"""Unit tests for Slack operations module."""

from unittest.mock import MagicMock

import pytest
from slack_sdk.errors import SlackApiError

from lsimons_bot.slack.exceptions import (
    InvalidRequestError,
    SlackAPIError,
    SlackChannelError,
    SlackThreadError,
)
from lsimons_bot.slack.operations import (
    ChannelInfo,
    Message,
    format_channel_context,
    get_channel_info,
    get_thread_history,
    send_ephemeral,
    send_thread_reply,
    set_suggested_prompts,
    set_thread_status,
)


class TestChannelInfo:
    """Tests for ChannelInfo dataclass."""

    def test_channel_info_creation(self) -> None:
        """Test ChannelInfo can be created with required fields."""
        channel = ChannelInfo(
            id="C123",
            name="general",
            topic="General discussion",
            is_private=False,
        )

        assert channel.id == "C123"
        assert channel.name == "general"
        assert channel.topic == "General discussion"
        assert channel.is_private is False

    def test_channel_info_private_channel(self) -> None:
        """Test ChannelInfo for private channel."""
        channel = ChannelInfo(
            id="C456",
            name="secret",
            topic="Secret stuff",
            is_private=True,
        )

        assert channel.is_private is True


class TestMessage:
    """Tests for Message dataclass."""

    def test_message_creation(self) -> None:
        """Test Message can be created with required fields."""
        msg = Message(
            ts="1234567890.123456",
            text="Hello world",
            user="U123",
        )

        assert msg.ts == "1234567890.123456"
        assert msg.text == "Hello world"
        assert msg.user == "U123"
        assert msg.thread_ts is None

    def test_message_with_thread_ts(self) -> None:
        """Test Message with thread timestamp."""
        msg = Message(
            ts="1234567890.123456",
            text="Reply in thread",
            user="U123",
            thread_ts="1234567890.000000",
        )

        assert msg.thread_ts == "1234567890.000000"


class TestFormatChannelContext:
    """Tests for format_channel_context function."""

    def test_format_public_channel_with_topic(self) -> None:
        """Test formatting public channel with topic."""
        channel = ChannelInfo(
            id="C123",
            name="general",
            topic="General discussion",
            is_private=False,
        )

        result = format_channel_context(channel)

        assert "#general (public)" in result
        assert "General discussion" in result

    def test_format_private_channel_with_topic(self) -> None:
        """Test formatting private channel with topic."""
        channel = ChannelInfo(
            id="C123",
            name="secret",
            topic="Secret discussions",
            is_private=True,
        )

        result = format_channel_context(channel)

        assert "#secret (private)" in result
        assert "Secret discussions" in result

    def test_format_channel_without_topic(self) -> None:
        """Test formatting channel without topic."""
        channel = ChannelInfo(
            id="C123",
            name="general",
            topic="",
            is_private=False,
        )

        result = format_channel_context(channel)

        assert "#general (public)" in result
        assert "Topic:" not in result


class TestGetChannelInfo:
    """Tests for get_channel_info function."""

    def test_get_channel_info_success(self) -> None:
        """Test successfully retrieving channel info."""
        client = MagicMock()
        client.conversations_info.return_value = {
            "channel": {
                "id": "C123",
                "name": "general",
                "topic": {"value": "General discussion"},
                "is_private": False,
            }
        }

        result = get_channel_info(client, "C123")

        assert result.id == "C123"
        assert result.name == "general"
        assert result.topic == "General discussion"
        assert result.is_private is False
        client.conversations_info.assert_called_once_with(channel="C123")

    def test_get_channel_info_no_topic(self) -> None:
        """Test retrieving channel without topic."""
        client = MagicMock()
        client.conversations_info.return_value = {
            "channel": {
                "id": "C123",
                "name": "general",
                "is_private": False,
            }
        }

        result = get_channel_info(client, "C123")

        assert result.topic == ""

    def test_get_channel_info_empty_channel_id(self) -> None:
        """Test with empty channel ID."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            get_channel_info(client, "")

    def test_get_channel_info_not_found(self) -> None:
        """Test channel not found error."""
        client = MagicMock()
        error = SlackApiError(
            message="channel not found",
            response={"error": "channel_not_found"},
        )
        client.conversations_info.side_effect = error

        with pytest.raises(SlackChannelError):
            get_channel_info(client, "C999")

    def test_get_channel_info_api_error(self) -> None:
        """Test other Slack API errors."""
        client = MagicMock()
        error = SlackApiError(
            message="not in channel",
            response={"error": "not_in_channel"},
        )
        client.conversations_info.side_effect = error

        with pytest.raises(SlackAPIError):
            get_channel_info(client, "C123")

    def test_get_channel_info_key_error(self) -> None:
        """Test handling of malformed response."""
        client = MagicMock()
        client.conversations_info.return_value = {}

        with pytest.raises(SlackChannelError):
            get_channel_info(client, "C123")


class TestSetThreadStatus:
    """Tests for set_thread_status function."""

    def test_set_thread_status_success(self) -> None:
        """Test successfully setting thread status."""
        client = MagicMock()

        set_thread_status(client, "C123", "1234567890.000000", "ok")

        client.assistant_threads_setStatus.assert_called_once_with(
            channel_id="C123",
            thread_ts="1234567890.000000",
            status="ok",
        )

    def test_set_thread_status_missing_channel_id(self) -> None:
        """Test with missing channel ID."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            set_thread_status(client, "", "1234567890.000000", "ok")

    def test_set_thread_status_missing_thread_ts(self) -> None:
        """Test with missing thread timestamp."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            set_thread_status(client, "C123", "", "ok")

    def test_set_thread_status_missing_status(self) -> None:
        """Test with missing status."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            set_thread_status(client, "C123", "1234567890.000000", "")

    def test_set_thread_status_api_error(self) -> None:
        """Test Slack API error."""
        client = MagicMock()
        error = SlackApiError(
            message="invalid thread ts",
            response={"error": "invalid_thread_ts"},
        )
        client.assistant_threads_setStatus.side_effect = error

        with pytest.raises(SlackThreadError):
            set_thread_status(client, "C123", "invalid", "ok")


class TestSetSuggestedPrompts:
    """Tests for set_suggested_prompts function."""

    def test_set_suggested_prompts_success(self) -> None:
        """Test successfully setting suggested prompts."""
        client = MagicMock()
        prompts = [
            {"title": "Explain", "prompt": "Explain this code"},
            {"title": "Simplify", "prompt": "Simplify this"},
        ]

        set_suggested_prompts(client, "C123", "1234567890.000000", prompts)

        client.assistant_threads_setSuggestedPrompts.assert_called_once_with(
            channel_id="C123",
            thread_ts="1234567890.000000",
            prompts=prompts,
        )

    def test_set_suggested_prompts_empty_list(self) -> None:
        """Test with empty prompts list."""
        client = MagicMock()

        set_suggested_prompts(client, "C123", "1234567890.000000", [])

        client.assistant_threads_setSuggestedPrompts.assert_called_once()

    def test_set_suggested_prompts_missing_channel_id(self) -> None:
        """Test with missing channel ID."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            set_suggested_prompts(client, "", "1234567890.000000", [])

    def test_set_suggested_prompts_missing_thread_ts(self) -> None:
        """Test with missing thread timestamp."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            set_suggested_prompts(client, "C123", "", [])

    def test_set_suggested_prompts_not_list(self) -> None:
        """Test with non-list prompts."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            set_suggested_prompts(client, "C123", "1234567890.000000", "not a list")

    def test_set_suggested_prompts_missing_title(self) -> None:
        """Test with prompt missing title."""
        client = MagicMock()
        prompts = [{"prompt": "Explain this"}]

        with pytest.raises(InvalidRequestError):
            set_suggested_prompts(client, "C123", "1234567890.000000", prompts)

    def test_set_suggested_prompts_missing_prompt(self) -> None:
        """Test with prompt missing prompt field."""
        client = MagicMock()
        prompts = [{"title": "Explain"}]

        with pytest.raises(InvalidRequestError):
            set_suggested_prompts(client, "C123", "1234567890.000000", prompts)

    def test_set_suggested_prompts_api_error(self) -> None:
        """Test Slack API error."""
        client = MagicMock()
        error = SlackApiError(
            message="invalid prompts",
            response={"error": "invalid_prompts"},
        )
        client.assistant_threads_setSuggestedPrompts.side_effect = error
        prompts = [{"title": "Test", "prompt": "Test"}]

        with pytest.raises(SlackThreadError):
            set_suggested_prompts(client, "C123", "1234567890.000000", prompts)


class TestGetThreadHistory:
    """Tests for get_thread_history function."""

    def test_get_thread_history_success(self) -> None:
        """Test successfully retrieving thread history."""
        client = MagicMock()
        client.conversations_history.return_value = {
            "messages": [
                {
                    "ts": "1234567890.000000",
                    "text": "First message",
                    "user": "U123",
                },
                {
                    "ts": "1234567890.000001",
                    "text": "Second message",
                    "user": "U456",
                    "thread_ts": "1234567890.000000",
                },
            ]
        }

        result = get_thread_history(client, "C123", "1234567890.000000")

        assert len(result) == 2
        assert result[0].text == "First message"
        assert result[1].text == "Second message"
        assert result[1].thread_ts == "1234567890.000000"

    def test_get_thread_history_no_messages(self) -> None:
        """Test thread with no messages."""
        client = MagicMock()
        client.conversations_history.return_value = {"messages": []}

        result = get_thread_history(client, "C123", "1234567890.000000")

        assert len(result) == 0

    def test_get_thread_history_custom_limit(self) -> None:
        """Test with custom message limit."""
        client = MagicMock()
        client.conversations_history.return_value = {"messages": []}

        get_thread_history(client, "C123", "1234567890.000000", limit=50)

        client.conversations_history.assert_called_once_with(
            channel="C123",
            ts_from="1234567890.000000",
            inclusive=True,
            limit=50,
        )

    def test_get_thread_history_missing_channel_id(self) -> None:
        """Test with missing channel ID."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            get_thread_history(client, "", "1234567890.000000")

    def test_get_thread_history_missing_thread_ts(self) -> None:
        """Test with missing thread timestamp."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            get_thread_history(client, "C123", "")

    def test_get_thread_history_invalid_limit(self) -> None:
        """Test with invalid limit."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            get_thread_history(client, "C123", "1234567890.000000", limit=0)

    def test_get_thread_history_api_error(self) -> None:
        """Test Slack API error."""
        client = MagicMock()
        error = SlackApiError(
            message="channel not found",
            response={"error": "channel_not_found"},
        )
        client.conversations_history.side_effect = error

        with pytest.raises(SlackThreadError):
            get_thread_history(client, "C999", "1234567890.000000")

    def test_get_thread_history_missing_ts_in_response(self) -> None:
        """Test with malformed message response."""
        client = MagicMock()
        client.conversations_history.return_value = {
            "messages": [
                {
                    "text": "Message without ts",
                    "user": "U123",
                }
            ]
        }

        with pytest.raises(SlackThreadError):
            get_thread_history(client, "C123", "1234567890.000000")


class TestSendEphemeral:
    """Tests for send_ephemeral function."""

    def test_send_ephemeral_success(self) -> None:
        """Test successfully sending ephemeral message."""
        client = MagicMock()

        send_ephemeral(client, "C123", "U456", "Hello user")

        client.chat_postEphemeral.assert_called_once_with(
            channel="C123",
            user="U456",
            text="Hello user",
            thread_ts=None,
        )

    def test_send_ephemeral_with_thread(self) -> None:
        """Test sending ephemeral message in thread."""
        client = MagicMock()

        send_ephemeral(client, "C123", "U456", "Hello in thread", thread_ts="1234567890.000000")

        client.chat_postEphemeral.assert_called_once_with(
            channel="C123",
            user="U456",
            text="Hello in thread",
            thread_ts="1234567890.000000",
        )

    def test_send_ephemeral_missing_channel(self) -> None:
        """Test with missing channel ID."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            send_ephemeral(client, "", "U456", "Hello")

    def test_send_ephemeral_missing_user(self) -> None:
        """Test with missing user ID."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            send_ephemeral(client, "C123", "", "Hello")

    def test_send_ephemeral_missing_text(self) -> None:
        """Test with missing message text."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            send_ephemeral(client, "C123", "U456", "")

    def test_send_ephemeral_api_error(self) -> None:
        """Test Slack API error."""
        client = MagicMock()
        error = SlackApiError(
            message="user not in channel",
            response={"error": "user_not_in_channel"},
        )
        client.chat_postEphemeral.side_effect = error

        with pytest.raises(SlackAPIError):
            send_ephemeral(client, "C123", "U999", "Hello")


class TestSendThreadReply:
    """Tests for send_thread_reply function."""

    def test_send_thread_reply_success(self) -> None:
        """Test successfully sending thread reply."""
        client = MagicMock()
        client.chat_postMessage.return_value = {"ts": "1234567890.000001"}

        result = send_thread_reply(client, "C123", "1234567890.000000", "Reply text")

        assert result == "1234567890.000001"
        client.chat_postMessage.assert_called_once_with(
            channel="C123",
            thread_ts="1234567890.000000",
            text="Reply text",
            metadata=None,
        )

    def test_send_thread_reply_with_metadata(self) -> None:
        """Test sending thread reply with metadata."""
        client = MagicMock()
        client.chat_postMessage.return_value = {"ts": "1234567890.000001"}
        metadata = {"event_type": "test"}

        result = send_thread_reply(
            client,
            "C123",
            "1234567890.000000",
            "Reply text",
            metadata=metadata,
        )

        assert result == "1234567890.000001"
        client.chat_postMessage.assert_called_once_with(
            channel="C123",
            thread_ts="1234567890.000000",
            text="Reply text",
            metadata=metadata,
        )

    def test_send_thread_reply_missing_channel(self) -> None:
        """Test with missing channel ID."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            send_thread_reply(client, "", "1234567890.000000", "Reply")

    def test_send_thread_reply_missing_thread_ts(self) -> None:
        """Test with missing thread timestamp."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            send_thread_reply(client, "C123", "", "Reply")

    def test_send_thread_reply_missing_text(self) -> None:
        """Test with missing message text."""
        client = MagicMock()

        with pytest.raises(InvalidRequestError):
            send_thread_reply(client, "C123", "1234567890.000000", "")

    def test_send_thread_reply_api_error(self) -> None:
        """Test Slack API error."""
        client = MagicMock()
        error = SlackApiError(
            message="channel not found",
            response={"error": "channel_not_found"},
        )
        client.chat_postMessage.side_effect = error

        with pytest.raises(SlackThreadError):
            send_thread_reply(client, "C999", "1234567890.000000", "Reply")

    def test_send_thread_reply_missing_ts_in_response(self) -> None:
        """Test with malformed response."""
        client = MagicMock()
        client.chat_postMessage.return_value = {}

        with pytest.raises(SlackThreadError):
            send_thread_reply(client, "C123", "1234567890.000000", "Reply")
