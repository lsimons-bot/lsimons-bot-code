"""
Top-level 'listeners' package removed.

This repository no longer provides a legacy top-level `listeners` package.
All code and imports must use the new package layout under the top-level
package `lsimons_bot`. The removal is intentional and non-backwards-compatible.

If you are seeing this ImportError it means some code is still importing from:

    import listeners
    from listeners import register_listeners
    from listeners._llm import create_llm_client
    from listeners._prompt import build_system_prompt
    from listeners._assistant_utils import get_conversation_history

Update those imports to the new locations. Examples:

    # Old (deprecated)
    from listeners import register_listeners
    from listeners._llm import create_llm_client
    from listeners._prompt import build_system_prompt
    from listeners._assistant_utils import get_conversation_history

    # New (required)
    from lsimons_bot.listeners import register_listeners
    from lsimons_bot.llm.client import create_llm_client
    from lsimons_bot.llm.prompt import build_system_prompt
    from lsimons_bot.llm.context import get_conversation_history

Migration notes:
- Search the repository (and any downstream consumers) for occurrences of
  "from listeners" or "import listeners" and replace them with the new paths.
- See history/AI_ASSISTANT_REFACTORING.md and docs/spec/003-ai-assistant-integration.md
  for migration guidance and examples.
- Consider using a codemod (sed, perl, or a small Python script) to update imports
  across multiple files.

This module raises on import to fail fast and surface remaining legacy imports
so they can be updated promptly.
"""

raise ImportError(
    "The legacy top-level 'listeners' package has been removed.\n\n"
    "Update your imports to use the refactored package layout under "
    "'lsimons_bot'. Example:\n\n"
    "    from lsimons_bot.listeners import register_listeners\n\n"
    "Refer to history/AI_ASSISTANT_REFACTORING.md for the full migration guide."
)
