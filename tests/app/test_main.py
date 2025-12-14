from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lsimons_bot.app.main import main


class TestMain:
    @pytest.mark.asyncio
    async def test_main_happy_path(self) -> None:
        mock_env_vars = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "LITELLM_API_BASE": "http://localhost:8000",
            "LITELLM_API_KEY": "test-key",
            "ASSISTANT_MODEL": "test/gpt-5-mini",
        }

        with (
            patch("lsimons_bot.app.main.get_env_vars", return_value=mock_env_vars),
            patch("lsimons_bot.app.main.LLMClient"),
            patch("lsimons_bot.app.main.AsyncApp"),
            patch("lsimons_bot.app.main.assistant.register"),
            patch("lsimons_bot.app.main.messages.register"),
            patch("lsimons_bot.app.main.home.register"),
            patch("lsimons_bot.app.main.AsyncSocketModeHandler") as mock_handler_class,
        ):
            mock_handler = MagicMock()
            mock_handler.start_async = AsyncMock()
            mock_handler_class.return_value = mock_handler

            await main()
