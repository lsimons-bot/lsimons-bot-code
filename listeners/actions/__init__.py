from slack_bolt import App

from .assistant_feedback import assistant_feedback_handler


def register(app: App) -> None:
    """Register all action listeners with the Slack app."""
    app.action("feedback_thumbs_up")(assistant_feedback_handler)
    app.action("feedback_thumbs_down")(assistant_feedback_handler)
