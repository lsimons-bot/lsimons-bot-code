"""Registers message listeners with the Slack app.

Message listeners respond to messages posted in channels or DMs.

To add a new message listener:
1. Create a handler file in this directory (e.g., mention_handler.py)
2. Implement the handler with full type annotations
3. Import the handler in this file
4. Register it using app.message()(handler) or app.message(pattern)(handler)

Example:
    from .mention_handler import mention_handler

    def register(app: App) -> None:
        app.message()(mention_handler)

See docs/spec/002-slack-listener-patterns.md for full details.
"""

from slack_bolt import App


def register(app: App) -> None:
    """Register message listeners.

    Currently no message listeners are implemented. When adding listeners,
    import handlers and register them with app.message().
    """
    pass
