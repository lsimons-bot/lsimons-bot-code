from slack_bolt import App

from .assistant_thread_started import assistant_thread_started_handler


def register(app: App) -> None:
    """Register event listeners with the Slack app."""
    app.event("assistant_thread_started")(assistant_thread_started_handler)
