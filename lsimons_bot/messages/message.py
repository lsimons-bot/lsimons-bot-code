import logging
from typing import Any

logger = logging.getLogger(__name__)


async def message(body: dict[str, Any]) -> None:
    logger.debug(">> message(%s)", body)

    event = body.get("event", {})

    type = body.get("type", "")
    if type in ["event_callback"]:
        logger.debug("ignoring %s message", type)
        return

    bot_id = event.get("bot_id", {})
    if bot_id:
        logger.debug("ignoring bot message")
        return

    logger.debug("<< message()")
