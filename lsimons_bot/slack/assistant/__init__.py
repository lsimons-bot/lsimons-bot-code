# pyright: reportUnknownMemberType=none, reportUnknownVariableType=none
from slack_bolt.async_app import AsyncApp, AsyncAssistant

from lsimons_bot.bot.bot import Bot

from .assistant_message import assistant_message_handler_maker
from .assistant_thread_started import assistant_thread_started


def register(app: AsyncApp, bot: Bot) -> None:
    assistant = AsyncAssistant()
    _ = assistant.thread_started(assistant_thread_started)
    _ = assistant.user_message(
        assistant_message_handler_maker(
            bot,
        )
    )
    _ = app.use(assistant)
