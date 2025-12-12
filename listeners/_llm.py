"""
Legacy shim for `listeners/_llm.py`.

This module exists to preserve backwards-compatible imports from older code that
used `listeners._llm`. The canonical, refactored location is now
`lsimons_bot.llm.client`.

This shim performs lazy forwarding: it emits a DeprecationWarning the first time
a symbol is accessed and then imports and returns the real symbol from the new
package. Keeping import-time side-effects minimal is intentional.

Note: This file is a temporary compatibility layer and will be removed in a
future release. See history/AI_ASSISTANT_REFACTORING.md for migration guidance.
"""

from __future__ import annotations

import importlib
import logging
import warnings
from typing import Any, Iterable, List

logger = logging.getLogger(__name__)

# Public API that this shim attempts to provide from the legacy module.
__all__ = [
    "LiteLLMClient",
    "create_llm_client",
]

_DEPRECATION_MESSAGE = (
    "Importing from 'listeners._llm' is deprecated and will be removed in a future "
    "release. Please update imports to use 'lsimons_bot.llm.client'.\n\n"
    "Example:\n\n"
    "    # Old (deprecated)\n"
    "    from listeners._llm import create_llm_client\n\n"
    "    # New (preferred)\n"
    "    from lsimons_bot.llm.client import create_llm_client\n\n"
    "Refer to history/AI_ASSISTANT_REFACTORING.md for migration details."
)


def _warn_deprecated() -> None:
    """Emit a deprecation warning for legacy imports."""
    # stacklevel=3 to point to the call site in most consumer stacks
    warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=3)
    logger.info("Deprecated import used: listeners._llm")


def _import_client_module():
    """Lazy import of the new client module."""
    try:
        module = importlib.import_module("lsimons_bot.llm.client")
        return module
    except Exception as e:  # pragma: no cover - defensive fallback
        logger.exception(
            "Failed to import 'lsimons_bot.llm.client' while resolving legacy shim"
        )
        raise ImportError(
            "Could not import 'lsimons_bot.llm.client'. Ensure the package is installed "
            "and that your PYTHONPATH is configured correctly."
        ) from e


def __getattr__(name: str) -> Any:
    """
    Lazy attribute accessor used for forwarding symbols from the new package.

    This is triggered when code does `from listeners._llm import <name>` or
    accesses `listeners._llm.<name>`.
    """
    # Only forward documented public names
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    _warn_deprecated()
    module = _import_client_module()

    # Map expected names to the attributes in the new module
    if hasattr(module, name):
        return getattr(module, name)

    # If the client module does not expose the name, raise a helpful error.
    raise AttributeError(
        f"'{name}' was not found in 'lsimons_bot.llm.client'. The shim may be out of "
        "date. Update your imports to the new module path."
    )


def __dir__() -> List[str]:
    """List available attributes for tab-completion and tooling."""
    base = set(__all__)
    # Attempt to include whatever is exported by the new module (best-effort).
    try:
        module = _import_client_module()
        base.update(x for x in dir(module) if x in __all__)
    except Exception:
        # If import fails, fall back to only the declared __all__.
        pass
    return sorted(base)
