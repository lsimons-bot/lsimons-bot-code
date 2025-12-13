# pyright: reportExplicitAny=none, reportUnknownMemberType=none
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def app_mention(body: dict[str, Any]) -> None:
    logger.debug(">> app_mention(%s)", body)
    logger.debug("<< app_mention()")
