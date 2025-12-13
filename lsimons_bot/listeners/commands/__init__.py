"""Registers command listeners with the Slack app.

Command listeners respond to slash commands (e.g., /help, /status).

To add a new command listener:
1. Create a handler file in this directory (e.g., help_command.py)
2. Implement the handler with full type annotations
3. Import the handler in this file
4. Register it using app.command("command_name")(handler)

Example:
    from .help_command import help_command_handler

    def register(app: App) -> None:
        app.command("/help")(help_command_handler)

See docs/spec/002-slack-listener-patterns.md for full details.
"""

from slack_bolt import App


def register(app: App) -> None:
    """Register command listeners.

    Currently no commands are implemented. When adding commands,
    import handlers and register them with app.command().
    """
    pass
