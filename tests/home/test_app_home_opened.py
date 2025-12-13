import pytest

from lsimons_bot.home.app_home_opened import app_home_opened


class TestAppHomeOpened:
    @pytest.mark.asyncio
    async def test_app_home_opened_runs_without_error(self) -> None:
        await app_home_opened()
