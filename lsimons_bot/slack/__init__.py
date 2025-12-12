"""Slack integration module for lsimons_bot.

This module provides utilities and abstractions for interacting with Slack,
including channel operations, thread management, and error handling.
"""

from lsimons_bot.slack.exceptions import (
    InvalidRequestError,
    SlackAPIError,
    SlackAuthError,
    SlackChannelError,
    SlackError,
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

__all__ = [
    # Exceptions
    "SlackError",
    "SlackAPIError",
    "SlackAuthError",
    "SlackChannelError",
    "SlackThreadError",
    "InvalidRequestError",
    # Dataclasses
    "ChannelInfo",
    "Message",
    # Operations
    "get_channel_info",
    "format_channel_context",
    "set_thread_status",
    "set_suggested_prompts",
    "get_thread_history",
    "send_ephemeral",
    "send_thread_reply",
]
