import logging
import random
from asyncio import sleep
from typing import Any, Dict, List

from slack_bolt.async_app import (
    AsyncBoltContext,
    AsyncSay,
    AsyncSetStatus,
    AsyncSetTitle,
)
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse

logger = logging.getLogger(__name__)


loading_messages = [
    "Teaching the hamsters to type faster…",
    "Untangling the internet cables…",
    "Consulting the office goldfish…",
    "Polishing up the response just for you…",
    "Convincing the AI to stop overthinking…",
]

response_messages = [
    "That's interesting. Tell me more?",
    "What makes you say that?",
    "I'm not sure. Please elaborate.",
    "Can you provide more details?",
    "How does that make you feel?",
]


def pick_response_message() -> str:
    return random.choice(response_messages)


async def assistant_message(
    context: AsyncBoltContext,
    payload: Dict[str, Any],
    say: AsyncSay,
    set_status: AsyncSetStatus,
    set_title: AsyncSetTitle,
    client: AsyncWebClient,
) -> None:
    user_message = payload.get("text", "")
    logger.debug(">> assistant_message('%s',...)", user_message)
    channel_id = context.channel_id
    thread_ts = context.thread_ts
    messages: List[Dict[str, str]] = []

    await set_title(user_message)
    await set_status(status="thinking...", loading_messages=loading_messages)
    await sleep(0.05)

    if channel_id is not None and thread_ts is not None:
        try:
            messages = await read_thread(client, channel_id, thread_ts)
        except Exception as e:
            logger.error("Error reading the message thread: %s", e)
            await say(f"Error reading the message thread: {e}")
            return
    else:
        messages = [{"role": "user", "content": user_message}]
    logger.debug("message thread: %s", messages)

    await sleep(0.05)
    response = pick_response_message()
    await say(response)
    logger.debug("<< assistant_message()")


async def read_thread(
    client: AsyncWebClient, channel_id: str, thread_ts: str
) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    replies: AsyncSlackResponse = await client.conversations_replies(
        channel=channel_id,
        ts=thread_ts,
        oldest=thread_ts,
        limit=100,
    )
    for message in replies.get("messages", []):
        message_text = message.get("text", "")
        if message_text.strip() == "":
            continue
        bot_id = message.get("bot_id")
        role = "user" if bot_id is None else "assistant"
        messages.append({"role": role, "content": message_text})
    return messages
