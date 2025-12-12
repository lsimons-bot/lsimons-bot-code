"""Tests for _assistant_utils helper functions."""

from unittest.mock import MagicMock

import pytest
from slack_sdk.errors import SlackApiError

from listeners._assistant_utils import (
    format_thread_context,
    get_conversation_history,
    is_assistant_message,
)


class TestGetConversationHistory:
    """Tests for get_conversation_history function."""

    def test_get_conversation_history_basic(self) -> None:
        """Test retrieving basic conversation history."""
        client = MagicMock()
        client.conversations_replies.return_value = {
            "messages": [
                {"ts": "1.0", "user": "U123", "text": "Hello"},
                {"ts": "2.0", "user": "U456", "text": "Hi there"},
                {"ts": "3.0", "user": "U123", "text": "How are you?"},
            ]
        }

        result = get_conversation_history(client, "C123", "1.0")

        assert len(result) == 3
        assert result[0] == {"role": "user", "content": "Hello"}
        assert result[1] == {"role": "user", "content": "Hi there"}
        assert result[2] == {"role": "user", "content": "How are you?"}
        client.conversations_replies.assert_called_once_with(channel="C123", ts="1.0")

    def test_get_conversation_history_with_bot_messages(self) -> None:
        """Test that bot messages are marked as assistant."""
        client = MagicMock()
        client.conversations_replies.return_value = {
            "messages": [
                {"ts": "1.0", "user": "U123", "text": "Hello"},
                {
                    "ts": "2.0",
                    "bot_id": "B123",
                    "text": "I am here to help",
                    "bot_profile": {"name": "assistant"},
                },
                {"ts": "3.0", "user": "U123", "text": "Thanks"},
            ]
        }

        result = get_conversation_history(client, "C123", "1.0")

        assert len(result) == 3
        assert result[0] == {"role": "user", "content": "Hello"}
        assert result[1] == {"role": "assistant", "content": "I am here to help"}
        assert result[2] == {"role": "user", "content": "Thanks"}

    def test_get_conversation_history_skips_subtypes(self) -> None:
        """Test that message edits and deletes are skipped."""
        client = MagicMock()
        client.conversations_replies.return_value = {
            "messages": [
                {"ts": "1.0", "user": "U123", "text": "Original message"},
                {
                    "ts": "1.0",
                    "user": "U123",
                    "text": "Edited message",
                    "subtype": "message_changed",
                },
                {"ts": "2.0", "user": "U123", "text": "Second message"},
                {"ts": "3.0", "subtype": "message_deleted"},
            ]
        }

        result = get_conversation_history(client, "C123", "1.0")

        assert len(result) == 2
        assert result[0] == {"role": "user", "content": "Original message"}
        assert result[1] == {"role": "user", "content": "Second message"}

    def test_get_conversation_history_skips_empty_text(self) -> None:
        """Test that messages without text are skipped."""
        client = MagicMock()
        client.conversations_replies.return_value = {
            "messages": [
                {"ts": "1.0", "user": "U123", "text": "Hello"},
                {"ts": "2.0", "user": "U456"},  # No text
                {"ts": "3.0", "user": "U123", "text": ""},  # Empty text
                {"ts": "4.0", "user": "U123", "text": "World"},
            ]
        }

        result = get_conversation_history(client, "C123", "1.0")

        assert len(result) == 2
        assert result[0] == {"role": "user", "content": "Hello"}
        assert result[1] == {"role": "user", "content": "World"}

    def test_get_conversation_history_api_error(self) -> None:
        """Test handling of Slack API errors."""
        client = MagicMock()
        client.conversations_replies.side_effect = SlackApiError(
            message="not_in_channel",
            response={"error": "not_in_channel"},
        )

        with pytest.raises(SlackApiError):
            get_conversation_history(client, "C123", "1.0")

    def test_get_conversation_history_empty_thread(self) -> None:
        """Test handling of empty thread."""
        client = MagicMock()
        client.conversations_replies.return_value = {"messages": []}

        result = get_conversation_history(client, "C123", "1.0")

        assert result == []


class TestFormatThreadContext:
    """Tests for format_thread_context function."""

    def test_format_thread_context_basic(self) -> None:
        """Test basic channel context formatting."""
        result = format_thread_context("general")

        assert result == "You are in channel #general."

    def test_format_thread_context_with_topic(self) -> None:
        """Test context formatting with channel topic."""
        result = format_thread_context(
            "engineering",
            "Engineering team discussions and updates",
        )

        assert result == "You are in channel #engineering. Channel topic: Engineering team discussions and updates"

    def test_format_thread_context_with_empty_topic(self) -> None:
        """Test context formatting with empty topic."""
        result = format_thread_context("general", "")

        assert result == "You are in channel #general."

    def test_format_thread_context_with_special_characters(self) -> None:
        """Test context formatting with special characters in channel name."""
        result = format_thread_context("team-engineering")

        assert result == "You are in channel #team-engineering."


class TestIsAssistantMessage:
    """Tests for is_assistant_message function."""

    def test_is_assistant_message_with_bot_profile(self) -> None:
        """Test detection of message with bot_profile."""
        msg = {
            "ts": "1.0",
            "bot_profile": {"name": "assistant"},
            "text": "Hello",
        }

        assert is_assistant_message(msg) is True

    def test_is_assistant_message_with_bot_id(self) -> None:
        """Test detection of message with bot_id."""
        msg = {
            "ts": "1.0",
            "bot_id": "B123",
            "text": "Hello",
        }

        assert is_assistant_message(msg) is True

    def test_is_assistant_message_with_subtype(self) -> None:
        """Test detection of message with bot_message subtype."""
        msg = {
            "ts": "1.0",
            "subtype": "bot_message",
            "text": "Hello",
        }

        assert is_assistant_message(msg) is True

    def test_is_assistant_message_user_message(self) -> None:
        """Test that regular user messages are not detected as assistant."""
        msg = {
            "ts": "1.0",
            "user": "U123",
            "text": "Hello",
        }

        assert is_assistant_message(msg) is False

    def test_is_assistant_message_empty_dict(self) -> None:
        """Test detection with empty message dict."""
        assert is_assistant_message({}) is False

    def test_is_assistant_message_all_bot_indicators(self) -> None:
        """Test message with multiple bot indicators."""
        msg = {
            "ts": "1.0",
            "bot_profile": {"name": "assistant"},
            "bot_id": "B123",
            "subtype": "bot_message",
            "text": "Hello",
        }

        assert is_assistant_message(msg) is True
