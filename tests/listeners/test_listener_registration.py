"""Tests for listener registration functions."""

from unittest.mock import MagicMock, patch

from slack_bolt import App

from lsimons_bot.listeners import (
    actions,
    commands,
    events,
    messages,
    register_listeners,
    shortcuts,
    views,
)


class TestRegisterListeners:
    """Tests for register_listeners function."""

    @patch("lsimons_bot.listeners.views.register")
    @patch("lsimons_bot.listeners.shortcuts.register")
    @patch("lsimons_bot.listeners.messages.register")
    @patch("lsimons_bot.listeners.events.register")
    @patch("lsimons_bot.listeners.commands.register")
    @patch("lsimons_bot.listeners.actions.register")
    def test_register_listeners_calls_all_categories(
        self,
        mock_actions,
        mock_commands,
        mock_events,
        mock_messages,
        mock_shortcuts,
        mock_views,
    ) -> None:
        """Test that register_listeners calls register in all categories."""
        app = MagicMock(spec=App)

        register_listeners(app)

        mock_actions.assert_called_once_with(app)
        mock_commands.assert_called_once_with(app)
        mock_events.assert_called_once_with(app)
        mock_messages.assert_called_once_with(app)
        mock_shortcuts.assert_called_once_with(app)
        mock_views.assert_called_once_with(app)


class TestActionsRegister:
    """Tests for actions.register function."""

    def test_actions_register_registers_feedback_actions(self) -> None:
        """Test actions.register registers thumbs up/down feedback actions."""
        app = MagicMock(spec=App)

        actions.register(app)

        # Verify both feedback actions are registered
        assert app.action.call_count == 2
        app.action.assert_any_call("feedback_thumbs_up")
        app.action.assert_any_call("feedback_thumbs_down")


class TestCommandsRegister:
    """Tests for commands.register function."""

    def test_commands_register_no_registrations(self) -> None:
        """Test commands.register makes no registrations (empty module)."""
        app = MagicMock(spec=App)

        commands.register(app)

        # Verify no command registrations were made
        app.command.assert_not_called()


class TestEventsRegister:
    """Tests for events.register function."""

    def test_events_register_registers_assistant_events(self) -> None:
        """Test events.register registers assistant thread and message events."""
        app = MagicMock(spec=App)

        events.register(app)

        # Verify both assistant events are registered
        assert app.event.call_count == 2
        app.event.assert_any_call("assistant_thread_started")
        app.event.assert_any_call("assistant_user_message")


class TestMessagesRegister:
    """Tests for messages.register function."""

    def test_messages_register_no_registrations(self) -> None:
        """Test messages.register makes no registrations (empty module)."""
        app = MagicMock(spec=App)

        messages.register(app)

        # Verify no message registrations were made
        app.message.assert_not_called()


class TestShortcutsRegister:
    """Tests for shortcuts.register function."""

    def test_shortcuts_register_no_registrations(self) -> None:
        """Test shortcuts.register makes no registrations (empty module)."""
        app = MagicMock(spec=App)

        shortcuts.register(app)

        # Verify no shortcut registrations were made
        app.shortcut.assert_not_called()


class TestViewsRegister:
    """Tests for views.register function."""

    def test_views_register_no_registrations(self) -> None:
        """Test views.register makes no registrations (empty module)."""
        app = MagicMock(spec=App)

        views.register(app)

        # Verify no view registrations were made
        app.view.assert_not_called()
