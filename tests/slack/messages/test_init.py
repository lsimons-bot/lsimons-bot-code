from unittest.mock import MagicMock

from lsimons_bot.slack.messages import register


class TestRegister:
    def test_register_happy_path(self) -> None:
        register(MagicMock())
