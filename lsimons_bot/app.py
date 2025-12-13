from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from lsimons_bot.config import get_env_vars

from . import assistant, home, messages


async def main():
    env_vars = get_env_vars()

    app = AsyncApp(
        token=env_vars["SLACK_BOT_TOKEN"],
        ignoring_self_assistant_message_events_enabled=False,
    )
    assistant.register(app)
    messages.register(app)
    home.register(app)

    handler = AsyncSocketModeHandler(app, env_vars["SLACK_APP_TOKEN"])
    await handler.start_async()
