# pyright: reportUnknownMemberType=none
import logging
from asyncio import sleep
from typing import Any, cast

from slack_bolt.async_app import (
    AsyncBoltContext,
    AsyncSay,
    AsyncSetStatus,
    AsyncSetTitle,
)
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse

from lsimons_bot.bot.bot import Bot, Messages

logger = logging.getLogger(__name__)


def assistant_message_handler_maker(
    bot: Bot,
):
    async def assistant_message(
        context: AsyncBoltContext,
        payload: dict[str, Any],
        say: AsyncSay,
        set_status: AsyncSetStatus,
        set_title: AsyncSetTitle,
        client: AsyncWebClient,
    ) -> None:
        user_message = cast(str, payload.get("text", ""))
        logger.debug(">> assistant_message('%s',...)", user_message)
        channel_id = context.channel_id
        thread_ts = context.thread_ts
        messages: Messages = []
        loading_messages = bot.loading_messages()

        if len(user_message) <= 50:
            _ = await set_title(user_message)

        _ = await set_status(status="thinking...", loading_messages=loading_messages)
        await sleep(0.05)

        if channel_id is not None and thread_ts is not None:
            try:
                messages = await read_thread(client, channel_id, thread_ts)
            except Exception as e:
                logger.error("Error reading the message thread: %s", e)
                _ = await say(f"Error reading the message thread: {e}")
                return
        else:
            messages = [{"role": "user", "content": user_message}]
        logger.debug("message thread: %s", messages)

        await sleep(0.05)
        response = await bot.chat(messages)
        _ = await say(response)
        logger.debug("<< assistant_message()")

    return assistant_message


async def read_thread(client: AsyncWebClient, channel_id: str, thread_ts: str) -> Messages:
    messages: Messages = []
    replies: AsyncSlackResponse = await client.conversations_replies(
        channel=channel_id,
        ts=thread_ts,
        oldest=thread_ts,
        limit=100,
    )
    raw_messages = cast(list[dict[str, Any]], replies.get("messages", []))
    for message in raw_messages:
        message_text = cast(str, message.get("text", ""))
        if message_text.strip() == "":
            continue
        bot_id = message.get("bot_id")
        if bot_id is None:
            messages.append({"role": "user", "content": message_text})
        else:
            messages.append({"role": "assistant", "content": message_text})
    return messages
