import logging
from asyncio import sleep
from pprint import pprint
from typing import Any, Dict, Optional

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
from slack_bolt.kwargs_injection.async_args import AsyncArgs

# from slack_bolt.response import BoltResponse
from slack_sdk.web.async_client import AsyncWebClient

logger = logging.getLogger(__name__)


async def assistant_message(args: AsyncArgs) -> None:
    logger.debug(">> assistant_message(%s)", args)
    ## None:
    # options: Optional[Dict[str, Any]] = args.options
    # shortcut: Optional[Dict[str, Any]] = args.shortcut
    # action: Optional[Dict[str, Any]] = args.action
    # view: Optional[Dict[str, Any]] = args.view
    # command: Optional[Dict[str, Any]] = args.command
    # resp: BoltResponse = args.resp

    ## USEFUL DATA:

    event: Optional[Dict[str, Any]] = args.event
    print("event:")
    pprint(event)

    context: AsyncBoltContext = args.context
    print("context:")
    pprint(context)

    body: Dict[str, Any] = args.body
    print("body:")
    pprint(body)
    payload: Dict[str, Any] = args.payload
    print("payload:")
    pprint(payload)

    # same as event:
    message: Optional[Dict[str, Any]] = args.message
    print("message:")
    pprint(message)

    ## ACTIONS & HELPERS:

    ack: AsyncAck = args.ack
    say: AsyncSay = args.say
    respond: AsyncRespond = args.respond
    complete: AsyncComplete = args.complete
    fail: AsyncFail = args.fail
    set_status: Optional[AsyncSetStatus] = args.set_status
    set_title: Optional[AsyncSetTitle] = args.set_title
    set_suggested_prompts: Optional[AsyncSetSuggestedPrompts] = (
        args.set_suggested_prompts
    )
    get_thread_context: Optional[AsyncGetThreadContext] = args.get_thread_context
    save_thread_context: Optional[AsyncSaveThreadContext] = args.save_thread_context
    client: AsyncWebClient = args.client
    req: AsyncBoltRequest = args.req

    user_message = payload["text"]

    if set_title is not None:
        await set_title(user_message)
    if set_status is not None:
        await set_status("Thinking...")
    await sleep(0.3)

    if set_status is not None:
        await set_status("Still thinking...")
    await sleep(0.3)

    if get_thread_context is not None:
        thread_context = await get_thread_context()
        if thread_context is not None:
            channel = thread_context.channel_id
            await say(f"#{channel}? What's there? You said: {user_message}")
        else:
            await say(f"You said: {user_message}")
    else:
        await say(f"You said: {user_message}")

    logger.debug("<< assistant_message()")
