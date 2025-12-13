from typing import Any, Dict

from slack_bolt.async_app import (
    AsyncAck,
    AsyncBoltContext,
    AsyncBoltRequest,
    AsyncGetThreadContext,
    AsyncRespond,
    AsyncSay,
    AsyncSetStatus,
    AsyncSetTitle,
)
from slack_bolt.context.complete.async_complete import AsyncComplete
from slack_bolt.context.fail.async_fail import AsyncFail
from slack_bolt.context.save_thread_context.async_save_thread_context import (
    AsyncSaveThreadContext,
)
from slack_bolt.context.set_suggested_prompts.async_set_suggested_prompts import (
    AsyncSetSuggestedPrompts,
)
from slack_bolt.response import BoltResponse
from slack_sdk.web.async_client import AsyncWebClient


# below is an example of a 'full' slack_bolt event handler method signature
# slack_bolt has a rather fancy dispatch mechanism
# so that any event handler can have any combination of parameters
# the details are in slack_bolt.kwargs_injection.async_args.AsyncArgs
async def slack_event_handler(
    ## CAN BE None:
    options: Dict[str, Any] | None,
    shortcut: Dict[str, Any] | None,
    action: Dict[str, Any] | None,
    view: Dict[str, Any] | None,
    command: Dict[str, Any] | None,
    resp: BoltResponse,
    ## DATA:
    event: Dict[str, Any] | None,
    context: AsyncBoltContext,
    body: Dict[str, Any],
    payload: Dict[str, Any],
    # same as event:
    message: Dict[str, Any] | None,
    ## ACTIONS & HELPERS:
    ack: AsyncAck,
    say: AsyncSay,
    respond: AsyncRespond,
    complete: AsyncComplete,
    fail: AsyncFail,
    set_status: AsyncSetStatus | None,
    set_title: AsyncSetTitle | None,
    set_suggested_prompts: AsyncSetSuggestedPrompts | None,
    get_thread_context: AsyncGetThreadContext | None,
    save_thread_context: AsyncSaveThreadContext | None,
    client: AsyncWebClient,
    req: AsyncBoltRequest,
) -> None:
    pass


# sample data from an invocation of assistant_message():
event = {
    "assistant_thread": {"action_token": "10113454590597.10138525474272.6d5f43aa145b052ce0f7650320d9767a"},
    "blocks": [
        {
            "block_id": "a8bcU",
            "elements": [
                {
                    "elements": [{"text": "hi", "type": "text"}],
                    "type": "rich_text_section",
                }
            ],
            "type": "rich_text",
        }
    ],
    "channel": "D0A387NCE2W",
    "channel_type": "im",
    "client_msg_id": "ce133266-eb72-4cbe-9c25-5b8ee81fb66d",
    "event_ts": "1765657699.728009",
    "parent_user_id": "U0A3BQUJQ5S",
    "text": "hi",
    "thread_ts": "1765656590.063629",
    "ts": "1765657699.728009",
    "type": "message",
    "user": "U0A3M4171BK",
}
context = {
    "ack": "<slack_bolt.context.ack.async_ack.AsyncAck object at 0x101bdcd70>",
    "actor_enterprise_id": "E0A3BPH11QC",
    "actor_user_id": "U0A3M4171BK",
    "authorize_result": {
        "bot_id": "B0A34Q56E5B",
        "bot_scopes": [
            "channels:history",
            "chat:write",
            "commands",
            "assistant:write",
            "im:history",
            "channels:read",
            "groups:read",
            "im:read",
            "mpim:read",
            "im:write",
            "app_mentions:read",
            "mpim:history",
        ],
        "bot_token": "xoxb-...",
        "bot_user_id": "U0A3BQUJQ5S",
        "enterprise_id": "E0A3BPH11QC",
        "team": None,
        "team_id": "E0A3BPH11QC",
        "url": None,
        "user": None,
        "user_id": "U0A3M4171BK",
        "user_scopes": None,
        "user_token": None,
    },
    "bot_id": "B0A34Q56E5B",
    "bot_token": "xoxb-...",
    "bot_user_id": "U0A3BQUJQ5S",
    "channel_id": "D0A387NCE2W",
    "client": "<slack_sdk.web.async_client.AsyncWebClient object at 0x101abafd0>",
    "complete": "<slack_bolt.context.complete.async_complete.AsyncComplete object at 0x101bdd010>",
    "enterprise_id": "E0A3BPH11QC",
    "fail": "<slack_bolt.context.fail.async_fail.AsyncFail object at 0x101bdd160>",
    "get_thread_context": "<slack_bolt.context.get_thread_context.async_get_thread_context.AsyncGetThreadContext object at 0x101bdcad0>",
    "is_enterprise_install": True,
    "listener_runner": "<slack_bolt.listener.asyncio_runner.AsyncioListenerRunner object at 0x101b49940>",
    "logger": "<Logger app.py (WARNING)>",
    "respond": "<slack_bolt.context.respond.async_respond.AsyncRespond object at 0x101bdcec0>",
    "save_thread_context": "<slack_bolt.context.save_thread_context.async_save_thread_context.AsyncSaveThreadContext object at 0x101bdcc20>",
    "say": "<slack_bolt.context.say.async_say.AsyncSay object at 0x101bdc050>",
    "set_status": "<slack_bolt.context.set_status.async_set_status.AsyncSetStatus object at 0x101bdc1a0>",
    "set_suggested_prompts": "<slack_bolt.context.set_suggested_prompts.async_set_suggested_prompts.AsyncSetSuggestedPrompts object at 0x101bdc980>",
    "set_title": "<slack_bolt.context.set_title.async_set_title.AsyncSetTitle object at 0x101bdc830>",
    "thread_ts": "1765656590.063629",
    "token": "xoxb-...",
    "user_id": "U0A3M4171BK",
}
body = {
    "api_app_id": "A0A34Q4D20M",
    "authorizations": [
        {
            "enterprise_id": "E0A3BPH11QC",
            "is_bot": True,
            "is_enterprise_install": True,
            "team_id": None,
            "user_id": "U0A3BQUJQ5S",
        }
    ],
    "context_enterprise_id": "E0A3BPH11QC",
    "context_team_id": None,
    "enterprise_id": "E0A3BPH11QC",
    "event": {
        "assistant_thread": {"action_token": "10113454590597.10138525474272.6d...7a"},
        "blocks": [
            {
                "block_id": "a8bcU",
                "elements": [
                    {
                        "elements": [{"text": "hi", "type": "text"}],
                        "type": "rich_text_section",
                    }
                ],
                "type": "rich_text",
            }
        ],
        "channel": "D0A387NCE2W",
        "channel_type": "im",
        "client_msg_id": "ce133266-eb72-4cbe-9c25-5b8ee81fb66d",
        "event_ts": "1765657699.728009",
        "parent_user_id": "U0A3BQUJQ5S",
        "text": "hi",
        "thread_ts": "1765656590.063629",
        "ts": "1765657699.728009",
        "type": "message",
        "user": "U0A3M4171BK",
    },
    "event_context": "4-eyJld...cifQ",
    "event_id": "Ev0A495YPNKS",
    "event_time": 1765657699,
    "is_ext_shared_channel": False,
    "team_id": "T0A42FFDY80",
    "token": "mXV...8x",
    "type": "event_callback",
}
payload = {
    "assistant_thread": {"action_token": "10113454590597.10138525474272.6d...7a"},
    "blocks": [
        {
            "block_id": "a8bcU",
            "elements": [
                {
                    "elements": [{"text": "hi", "type": "text"}],
                    "type": "rich_text_section",
                }
            ],
            "type": "rich_text",
        }
    ],
    "channel": "D0A387NCE2W",
    "channel_type": "im",
    "client_msg_id": "ce133266-eb72-4cbe-9c25-5b8ee81fb66d",
    "event_ts": "1765657699.728009",
    "parent_user_id": "U0A3BQUJQ5S",
    "text": "hi",
    "thread_ts": "1765656590.063629",
    "ts": "1765657699.728009",
    "type": "message",
    "user": "U0A3M4171BK",
}
