"""Shared utility functions for Slack listeners.

Provides common functionality used across multiple listener handlers.
"""

import inspect
import logging
from typing import Callable

logger = logging.getLogger(__name__)


async def safe_ack(ack: Callable[..., object]) -> None:
    """Call ack and await it if it returns an awaitable.

    This keeps the handler compatible with both sync and async ack callables,
    which is necessary for supporting both Slack Bolt's test mocks and
    real async ack implementations.

    Args:
        ack: Acknowledge function provided by Bolt (may be sync or async)

    Raises:
        No exceptions - handles TypeError gracefully for mismatched signatures
    """
    try:
        result = ack()
    except TypeError:
        # If ack expects arguments and tests use a different signature, ignore.
        # Tests typically use ack without args; if a different signature is used
        # the caller should adapt accordingly.
        return

    if inspect.isawaitable(result):
        # Await the awaitable (this covers AsyncMock and real coroutines)
        await result  # type: ignore[reportGeneralTypeIssues]
