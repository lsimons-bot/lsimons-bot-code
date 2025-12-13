from unittest.mock import MagicMock

from lsimons_bot.slack.home import register


class TestRegister:
    def test_register_happy_path(self) -> None:
        mock_app = MagicMock()
        mock_event = MagicMock()
        mock_app.event.return_value = mock_event

        register(mock_app)

        mock_app.event.assert_called_once_with("app_home_opened")
