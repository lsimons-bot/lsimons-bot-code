from slack_bolt.async_app import AsyncApp

from .app_mention import app_mention
from .message import message


def register(app: AsyncApp) -> None:
    app.event("message")(message)
    app.event("app_mention")(app_mention)
