"""Registers shortcut listeners with the Slack app.

Shortcut listeners respond to message shortcuts and global shortcuts.

To add a new shortcut listener:
1. Create a handler file in this directory (e.g., bookmark_message.py)
2. Implement the handler with full type annotations
3. Import the handler in this file
4. Register it using app.shortcut("shortcut_id")(handler)

Example:
    from .bookmark_message import bookmark_message_handler

    def register(app: App) -> None:
        app.shortcut("bookmark_message")(bookmark_message_handler)

See docs/spec/002-slack-listener-patterns.md for full details.
"""

from slack_bolt import App


def register(app: App) -> None:
    """Register shortcut listeners.

    Currently no shortcuts are implemented. When adding shortcuts,
    import handlers and register them with app.shortcut().
    """
    pass
