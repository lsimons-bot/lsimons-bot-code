"""Registers view listeners with the Slack app.

View listeners respond to modal view submissions and closures.

To add a new view listener:
1. Create a handler file in this directory (e.g., survey_submission.py)
2. Implement the handler with full type annotations
3. Import the handler in this file
4. Register it using app.view("callback_id")(handler)

Example:
    from .survey_submission import survey_submission_handler

    def register(app: App) -> None:
        app.view("survey_submission")(survey_submission_handler)

See docs/spec/002-slack-listener-patterns.md for full details.
"""

from slack_bolt import App


def register(app: App) -> None:
    """Register view listeners.

    Currently no views are implemented. When adding views,
    import handlers and register them with app.view().
    """
    pass
