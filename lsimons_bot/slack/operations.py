"""Slack API operations module for lsimons_bot.

This module provides reusable wrappers for common Slack API operations,
including channel info, thread management, and message sending.
"""

from dataclasses import dataclass
from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from lsimons_bot.slack.exceptions import (
    InvalidRequestError,
    SlackAPIError,
    SlackChannelError,
    SlackThreadError,
)


@dataclass
class ChannelInfo:
    """Channel information."""

    id: str
    name: str
    topic: str
    is_private: bool


@dataclass
class Message:
    """Message information."""

    ts: str
    text: str
    user: str
    thread_ts: str | None = None


def get_channel_info(client: WebClient, channel_id: str) -> ChannelInfo:
    """Get channel information with error handling.

    Args:
        client: Slack WebClient instance
        channel_id: The channel ID to fetch info for

    Returns:
        ChannelInfo with channel details

    Raises:
        SlackChannelError: If channel lookup fails
        SlackAPIError: If Slack API returns an error
    """
    if not channel_id:
        raise InvalidRequestError("channel_id cannot be empty")

    try:
        response = client.conversations_info(channel=channel_id)
        channel: Any = response.get("channel")
        if not channel:
            raise KeyError("channel")

        channel_id_str: str = channel.get("id", channel_id)
        channel_name: str = channel.get("name", "unknown")
        channel_topic: str = channel.get("topic", {}).get("value", "")
        channel_is_private: bool = channel.get("is_private", False)

        return ChannelInfo(
            id=channel_id_str,
            name=channel_name,
            topic=channel_topic,
            is_private=channel_is_private,
        )
    except SlackApiError as e:
        error_code = e.response.get("error", str(e)) if hasattr(e, "response") else str(e)
        if error_code == "channel_not_found":
            raise SlackChannelError(f"Channel not found: {channel_id}") from e
        raise SlackAPIError(f"Failed to get channel info: {error_code}") from e
    except KeyError as e:
        raise SlackChannelError(f"Invalid channel response structure: {e}") from e


def format_channel_context(channel_info: ChannelInfo) -> str:
    """Format channel context for prompts.

    Args:
        channel_info: ChannelInfo instance

    Returns:
        Formatted channel context string
    """
    privacy = "private" if channel_info.is_private else "public"
    context = f"Channel: #{channel_info.name} ({privacy})"

    if channel_info.topic:
        context += f"\nTopic: {channel_info.topic}"

    return context


def set_thread_status(
    client: WebClient,
    channel_id: str,
    thread_ts: str,
    status: str,
) -> None:
    """Set assistant thread status.

    Args:
        client: Slack WebClient instance
        channel_id: The channel containing the thread
        thread_ts: The thread timestamp
        status: The status to set (e.g., "ok", "failed")

    Raises:
        SlackThreadError: If status update fails
        SlackAPIError: If Slack API returns an error
    """
    if not all([channel_id, thread_ts, status]):
        raise InvalidRequestError("channel_id, thread_ts, and status are required")

    try:
        client.assistant_threads_setStatus(
            channel_id=channel_id,
            thread_ts=thread_ts,
            status=status,
        )
    except SlackApiError as e:
        raise SlackThreadError(f"Failed to set thread status: {e.response['error']}") from e


def set_suggested_prompts(
    client: WebClient,
    channel_id: str,
    thread_ts: str,
    prompts: list[dict[str, str]],
) -> None:
    """Set suggested prompts for thread.

    Args:
        client: Slack WebClient instance
        channel_id: The channel containing the thread
        thread_ts: The thread timestamp
        prompts: List of prompt dicts with 'title' and 'prompt' keys

    Raises:
        SlackThreadError: If prompt update fails
        SlackAPIError: If Slack API returns an error
        InvalidRequestError: If prompts format is invalid
    """
    if not all([channel_id, thread_ts]):
        raise InvalidRequestError("channel_id and thread_ts are required")

    if not isinstance(prompts, list):
        raise InvalidRequestError("prompts must be a list")

    for prompt in prompts:
        if not isinstance(prompt, dict) or "title" not in prompt or "prompt" not in prompt:
            raise InvalidRequestError("Each prompt must have 'title' and 'prompt' keys")

    try:
        client.assistant_threads_setSuggestedPrompts(
            channel_id=channel_id,
            thread_ts=thread_ts,
            prompts=prompts,
        )
    except SlackApiError as e:
        raise SlackThreadError(f"Failed to set suggested prompts: {e.response['error']}") from e


def get_thread_history(
    client: WebClient,
    channel_id: str,
    thread_ts: str,
    limit: int = 10,
) -> list[Message]:
    """Get conversation history for a thread.

    Args:
        client: Slack WebClient instance
        channel_id: The channel containing the thread
        thread_ts: The thread timestamp
        limit: Maximum number of messages to fetch

    Returns:
        List of Message objects from the thread

    Raises:
        SlackThreadError: If history fetch fails
        SlackAPIError: If Slack API returns an error
    """
    if not all([channel_id, thread_ts]):
        raise InvalidRequestError("channel_id and thread_ts are required")

    if limit < 1:
        raise InvalidRequestError("limit must be >= 1")

    try:
        response = client.conversations_history(
            channel=channel_id,
            ts_from=thread_ts,
            inclusive=True,
            limit=limit,
        )

        messages = []
        for msg in response.get("messages", []):
            messages.append(
                Message(
                    ts=msg["ts"],
                    text=msg.get("text", ""),
                    user=msg.get("user", ""),
                    thread_ts=msg.get("thread_ts"),
                )
            )

        return messages
    except SlackApiError as e:
        raise SlackThreadError(f"Failed to get thread history: {e.response['error']}") from e
    except KeyError as e:
        raise SlackThreadError(f"Invalid message response structure: {e}") from e


def send_ephemeral(
    client: WebClient,
    channel_id: str,
    user_id: str,
    text: str,
    thread_ts: str | None = None,
) -> None:
    """Send ephemeral message to user.

    Args:
        client: Slack WebClient instance
        channel_id: The channel to send message in
        user_id: The user to send the ephemeral message to
        text: The message text
        thread_ts: Optional thread timestamp to send in a thread

    Raises:
        SlackAPIError: If message sending fails
        InvalidRequestError: If required parameters are missing
    """
    if not all([channel_id, user_id, text]):
        raise InvalidRequestError("channel_id, user_id, and text are required")

    try:
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=text,
            thread_ts=thread_ts,
        )
    except SlackApiError as e:
        raise SlackAPIError(f"Failed to send ephemeral message: {e.response['error']}") from e


def send_thread_reply(
    client: WebClient,
    channel_id: str,
    thread_ts: str,
    text: str,
    metadata: dict[str, object] | None = None,
) -> str:
    """Send a message reply in a thread.

    Args:
        client: Slack WebClient instance
        channel_id: The channel containing the thread
        thread_ts: The thread timestamp
        text: The message text
        metadata: Optional message metadata

    Returns:
        The timestamp of the sent message

    Raises:
        SlackThreadError: If message sending fails
        SlackAPIError: If Slack API returns an error
        InvalidRequestError: If required parameters are missing
    """
    if not all([channel_id, thread_ts, text]):
        raise InvalidRequestError("channel_id, thread_ts, and text are required")

    try:
        response = client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=text,
            metadata=metadata,
        )
        ts: str | None = response.get("ts")
        if ts is None:
            raise KeyError("ts")
        return ts
    except SlackApiError as e:
        raise SlackThreadError(f"Failed to send thread reply: {e.response['error']}") from e
    except KeyError as e:
        raise SlackThreadError(f"Invalid message response structure: {e}") from e
