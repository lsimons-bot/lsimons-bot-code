from typing import override

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from lsimons_bot.app.config import get_env_vars
from lsimons_bot.bot.bot import Bot, Messages
from lsimons_bot.llm.client import LLMClient
from lsimons_bot.slack import assistant, home, messages


class LLMBot(Bot):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__()
        self.llm: LLMClient = llm

    @override
    async def chat_completion(self, messages: Messages) -> str:
        return await self.llm.chat_completion(messages)


async def main() -> None:
    env_vars = get_env_vars()
    llm_base_url = env_vars["LITELLM_API_BASE"]
    llm_api_key = env_vars["LITELLM_API_KEY"]
    llm_assistant_model = env_vars["ASSISTANT_MODEL"]
    slack_bot_token = env_vars["SLACK_BOT_TOKEN"]
    slack_app_token = env_vars["SLACK_APP_TOKEN"]

    llm = LLMClient(base_url=llm_base_url, api_key=llm_api_key, model=llm_assistant_model)

    bot = LLMBot(llm)

    app = AsyncApp(
        token=slack_bot_token,
        ignoring_self_assistant_message_events_enabled=False,
    )
    assistant.register(app, bot)
    messages.register(app)
    home.register(app)

    handler = AsyncSocketModeHandler(app, slack_app_token)
    await handler.start_async()
