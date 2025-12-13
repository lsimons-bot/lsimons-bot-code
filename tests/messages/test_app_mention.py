import pytest

from lsimons_bot.messages.app_mention import app_mention


class TestAppMention:
    @pytest.mark.asyncio
    async def test_app_mention_runs_without_error(self) -> None:
        """Test that app_mention handles body without raising exceptions."""
        body = {
            "event": {
                "type": "app_mention",
                "text": "<@U123> hello",
                "user": "U456",
            }
        }
        await app_mention(body)
