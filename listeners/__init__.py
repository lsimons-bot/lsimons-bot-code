"""
Compatibility shim for legacy `listeners` package.

This module exists to maintain backward compatibility for code that imports
the top-level `listeners` package (e.g. `from listeners import register_listeners`).
The project has been refactored and the canonical location is now
`lsimons_bot.listeners`. This shim forwards calls to the new package and emits
a `DeprecationWarning` to guide developers to update their imports.

Notes:
- Importing this module will emit a DeprecationWarning (non-fatal).
- The shim performs lazy imports of the new package at call-time to minimize
  import-time side-effects.
- This shim is temporary and will be removed in a future release. See
  history/AI_ASSISTANT_REFACTORING.md for migration guidance.
"""

from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING, Any, Callable

logger = logging.getLogger(__name__)

# Visible API from this shim
__all__ = ["register_listeners", "register"]

_DEPRECATION_MESSAGE = (
    "Importing the top-level 'listeners' package is deprecated and will be "
    "removed in a future release. Please update imports to use "
    "'lsimons_bot.listeners'. Example:\n\n"
    "    # Old (deprecated)\n"
    "    from listeners import register_listeners\n\n"
    "    # New (preferred)\n"
    "    from lsimons_bot.listeners import register_listeners\n\n"
    "Refer to history/AI_ASSISTANT_REFACTORING.md for migration details."
)


def _warn_deprecated() -> None:
    """Emit a deprecation warning to encourage migration to the new package."""
    # Use stacklevel=3 so the warning points at the user's import site in most call stacks.
    warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=3)
    # Also log at INFO level so it's visible in environments that hide warnings.
    logger.info("Deprecated import used: %s", __name__)


def _lazy_forward(name: str) -> Callable[..., Any]:
    """
    Return a small forwarding function that lazily imports and invokes the
    corresponding attribute from `lsimons_bot.listeners`.

    This keeps import-time overhead low and ensures we only import the new
    package when consumers actually call the shimmed API.
    """

    def _forward(*args: Any, **kwargs: Any) -> Any:
        _warn_deprecated()
        # Local import to avoid import-time side-effects and reduce startup cost.
        try:
            from lsimons_bot import listeners as _new_listeners  # type: ignore
        except Exception as e:  # pragma: no cover - defensive fallback
            # If the new package cannot be imported, re-raise with a helpful message.
            logger.exception(
                "Failed to import lsimons_bot.listeners while forwarding %s", name
            )
            raise ImportError(
                "Could not import 'lsimons_bot.listeners'. Ensure the package "
                "is available and that your PYTHONPATH is configured correctly."
            ) from e

        target = getattr(_new_listeners, name, None)
        if target is None:
            raise AttributeError(
                f"Target '{name}' not found in 'lsimons_bot.listeners'. "
                "This shim may be out of date."
            )
        return target(*args, **kwargs)

    return _forward


# Backwards-compatible API:
# - `register_listeners(app)` was the historic entry point used by app.py
# - `register(app)` is provided as a short alias for callers that used that name
register_listeners = _lazy_forward("register_listeners")
register = register_listeners
