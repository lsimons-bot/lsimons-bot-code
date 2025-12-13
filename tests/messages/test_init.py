from unittest.mock import MagicMock

from lsimons_bot.messages import register


class TestRegister:
    def test_register_happy_path(self) -> None:
        """Test that register adds message event handlers."""
        mock_app = MagicMock()
        mock_event = MagicMock()
        mock_app.event.return_value = mock_event

        register(mock_app)

        assert mock_app.event.call_count == 2
