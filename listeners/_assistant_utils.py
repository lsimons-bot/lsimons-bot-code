"""
Legacy shim for `listeners/_assistant_utils.py`.

This module preserves backwards-compatible imports from older code that used
`listeners._assistant_utils`. The canonical, refactored location is now
`lsimons_bot.llm.context`.

The shim performs lazy forwarding: it emits a DeprecationWarning the first time
a symbol is accessed and then resolves the symbol from the new module. Keep
import-time side-effects minimal so importing this module is safe.

This shim is temporary and will be removed in a future release. See
history/AI_ASSISTANT_REFACTORING.md for migration guidance.
"""

from __future__ import annotations

import importlib
import logging
import warnings
from typing import Any, List

logger = logging.getLogger(__name__)

__all__ = [
    "get_conversation_history",
    "format_thread_context",
    "is_assistant_message",
]

_DEPRECATION_MESSAGE = (
    "Importing from 'listeners._assistant_utils' is deprecated and will be "
    "removed in a future release. Please update imports to use "
    "'lsimons_bot.llm.context'.\n\n"
    "Example:\n\n"
    "    # Old (deprecated)\n"
    "    from listeners._assistant_utils import get_conversation_history\n\n"
    "    # New (preferred)\n"
    "    from lsimons_bot.llm.context import get_conversation_history\n\n"
    "Refer to history/AI_ASSISTANT_REFACTORING.md for migration details."
)


def _warn_deprecated() -> None:
    """Emit a deprecation warning for legacy imports."""
    # stacklevel=3 so the warning points to the user's import site in most stacks
    warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=3)
    logger.info("Deprecated import used: listeners._assistant_utils")


def _import_context_module():
    """Lazily import the new context module."""
    try:
        module = importlib.import_module("lsimons_bot.llm.context")
        return module
    except Exception as e:  # pragma: no cover - defensive fallback
        logger.exception(
            "Failed to import 'lsimons_bot.llm.context' while resolving legacy shim"
        )
        raise ImportError(
            "Could not import 'lsimons_bot.llm.context'. Ensure the package is available "
            "and that your PYTHONPATH is configured correctly."
        ) from e


def __getattr__(name: str) -> Any:
    """
    Lazy attribute accessor used for forwarding symbols from the new package.

    This is triggered when code does `from listeners._assistant_utils import <name>` or
    accesses `listeners._assistant_utils.<name>`.
    """
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    _warn_deprecated()
    module = _import_context_module()

    if hasattr(module, name):
        return getattr(module, name)

    raise AttributeError(
        f"'{name}' was not found in 'lsimons_bot.llm.context'. The shim may be out of "
        "date. Update your imports to the new module path."
    )


def __dir__() -> List[str]:
    """List available attributes for tab-completion and tooling."""
    base = set(__all__)
    try:
        module = _import_context_module()
        base.update(x for x in dir(module) if x in __all__)
    except Exception:
        # If import fails, fall back to only the declared __all__.
        pass
    return sorted(base)
