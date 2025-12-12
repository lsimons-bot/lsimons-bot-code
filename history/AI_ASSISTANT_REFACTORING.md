# AI Assistant Refactoring Plan

**Status:** In Progress (Phase 3 Complete ✅)
**Priority:** High

## Executive Summary

This document outlines a comprehensive refactoring of the lsimons-bot codebase to improve maintainability, testability, and code quality following Python best practices. The refactoring addresses four major areas:

1. **Package Structure**: Establish proper Python module hierarchy with `lsimons_bot` root package
2. **LLM Module Organization**: Consolidate LLM-related utilities into dedicated submodule
3. **Method Clarity and Responsibility**: Refactor complex methods to have single, clear responsibilities
4. **Exception Handling**: Replace generic exception catching with specific error types

## Table of Contents

- [Current Issues](#current-issues)
- [Proposed Structure](#proposed-structure)
- [Refactoring Strategy](#refactoring-strategy)
- [Implementation Phases](#implementation-phases)
- [Testing Requirements](#testing-requirements)
- [Migration Guide](#migration-guide)
- [Success Criteria](#success-criteria)

## Current Issues

### 1. Package Structure Problems

**Current Structure:**
```
lsimons-bot/
├── app.py                    # Root level (required by slack CLI)
├── app_oauth.py              # Root level (required by slack CLI)
├── listeners/                # Not a proper root package
│   ├── _llm.py              # Underscore prefix suggests private/utility
│   ├── _prompt.py           # Mixed with listeners
│   ├── _assistant_utils.py  # Mixed with listeners
│   ├── actions/
│   ├── commands/
│   ├── events/
│   └── ...
└── tests/                    # Mirrors listeners/ structure
```

**Problems:**
- No proper Python root package (`lsimons_bot`)
- Utility modules mixed with listener categories
- Unclear module ownership and responsibilities
- Import paths are confusing (`from listeners._llm import ...`)

### 2. LLM Code Scattered Across Multiple Files

**Current LLM-related code:**
- `listeners/_llm.py` (190 lines): LiteLLM client wrapper
- `listeners/_prompt.py` (250 lines): Prompt building and formatting
- `listeners/_assistant_utils.py` (partial): Thread context formatting

**Problems:**
- No cohesive LLM module structure
- Hard to find LLM-related functionality
- Prompt logic duplicated between `_prompt.py` and event handlers
- Context management split across files
- Confusing underscore-prefixed module names

### 3. Long Methods and Mixed Concerns

**Examples of problematic methods:**

#### `assistant_user_message_handler` (180+ lines)
```python
async def assistant_user_message_handler(...):
    # Acknowledge
    # Extract data
    # Validate data
    # Set thread status
    # Get channel info
    # Get conversation history
    # Build messages
    # Get environment config
    # Call LLM
    # Stream response
    # Handle errors
    # Set final status
    # All in one function with mixed responsibilities!
```

**Problems:**
- Too many responsibilities in one function (violates Single Responsibility Principle)
- Hard to test individual operations
- Error handling is mixed throughout
- Difficult to reuse any part of the logic
- Cannot easily understand what the function does without reading all 180 lines

#### `_generate_suggested_prompts` (duplicated logic)
- Logic exists in both `_prompt.py` and `assistant_thread_started.py`
- Different implementations with similar intent
- No single source of truth

### 4. Generic Exception Swallowing

**5 instances of `except Exception`:**

```python
# listeners/_llm.py:112
except Exception as e:
    logger.error(f"LiteLLM streaming error for model {model}: {str(e)}")
    raise  # At least it re-raises

# listeners/actions/assistant_feedback.py:86
except Exception as e:
    logger_.error("Error in assistant_feedback_handler: %s", str(e), exc_info=True)
    # Swallows all exceptions!

# listeners/events/assistant_thread_started.py:94
except Exception as e:
    logger_.error("Error in assistant_thread_started handler: %s", str(e), exc_info=True)
    # Swallows all exceptions!

# listeners/events/assistant_user_message.py:144
except Exception as e:
    logger_.error("LLM request failed: %s", str(e), exc_info=True)
    # Generic catch after specific ValueError

# listeners/events/assistant_user_message.py:178
except Exception as e:
    logger_.error("Error in assistant_user_message handler: %s", str(e), exc_info=True)
    # Outer catch-all swallows everything
```

**Problems:**
- Catches `KeyboardInterrupt`, `SystemExit`, `GeneratorExit`
- Hides bugs and programming errors
- Makes debugging difficult
- Violates principle of "fail fast"
- No differentiation between recoverable and fatal errors

## Proposed Structure

### Design Philosophy

The refactoring follows Python best practices and idioms:

- **"Flat is better than nested"**: Minimize unnecessary hierarchy
- **"Simple is better than complex"**: Don't over-engineer
- **"Readability counts"**: Optimize for clarity, not arbitrary metrics
- **Single Responsibility**: Each module/function has one clear purpose
- **Pragmatic extraction**: Extract helpers when they improve clarity or enable reuse
- **Explicit over implicit**: Clear naming and organization

### New Package Layout

```
lsimons-bot/
├── app.py                          # STAYS at root (required by slack CLI)
├── app_oauth.py                    # STAYS at root (required by slack CLI)
│
├── lsimons_bot/                    # NEW: Root package
│   ├── __init__.py
│   │
│   ├── llm/                        # NEW: LLM submodule
│   │   ├── __init__.py
│   │   ├── client.py               # LiteLLM client wrapper (from _llm.py)
│   │   ├── prompt.py               # Prompt building and formatting (from _prompt.py)
│   │   ├── context.py              # Context management (from _assistant_utils.py)
│   │   └── exceptions.py           # LLM-specific exceptions
│   │
│   ├── slack/                      # NEW: Slack operations wrapper
│   │   ├── __init__.py
│   │   ├── operations.py           # Slack API operations (channel, thread, message)
│   │   └── exceptions.py           # Slack-specific exceptions
│   │
│   └── listeners/                  # Refactored listeners
│       ├── __init__.py
│       ├── actions/
│       │   ├── __init__.py
│       │   └── assistant_feedback.py
│       ├── commands/
│       ├── events/
│       │   ├── __init__.py
│       │   ├── assistant_thread_started.py
│       │   └── assistant_user_message.py
│       ├── messages/
│       ├── shortcuts/
│       └── views/
│
├── tests/                          # Updated test structure
│   ├── __init__.py
│   ├── llm/                        # NEW: LLM tests
│   │   ├── __init__.py
│   │   ├── test_client.py
│   │   ├── test_prompt.py
│   │   └── test_context.py
│   ├── slack/                      # NEW: Slack tests
│   │   ├── __init__.py
│   │   ├── test_channel.py
│   │   ├── test_thread.py
│   │   └── test_message.py
│   └── listeners/
│       ├── actions/
│       ├── events/
│       └── ...
│
├── docs/
├── history/
├── .slack/
└── [config files]
```

### Module Responsibilities

#### `lsimons_bot/llm/`

**`client.py`** - LiteLLM client wrapper
- `LiteLLMClient` class
- `create_llm_client()` factory
- Stream and non-stream completion methods
- Connection management

**`prompt.py`** - Prompt engineering
- System prompt building
- Suggested prompt generation
- Prompt formatting for Slack
- Token estimation and trimming

**`context.py`** - Context management
- Thread history retrieval
- Context formatting
- Message role detection
- History trimming

**`exceptions.py`** - LLM-specific exceptions
- `LLMConfigurationError`
- `LLMAPIError`
- `LLMTimeoutError`
- `LLMQuotaExceededError`

#### `lsimons_bot/slack/`

**`operations.py`** - Slack API operations
- Channel operations:
  - `get_channel_info(client, channel_id)` -> ChannelInfo
  - `format_channel_context(channel_info)` -> str
- Thread operations:
  - `set_thread_status(client, channel_id, thread_id, status)`
  - `set_suggested_prompts(client, channel_id, thread_id, prompts)`
  - `get_thread_history(client, channel_id, thread_ts)` -> list[Message]
- Message operations:
  - `send_ephemeral(client, channel_id, user_id, text, thread_ts=None)`
  - `send_thread_reply(client, channel_id, thread_ts, text)`

**Note:** All operations in one module since the codebase is relatively small. Can be split later if it grows significantly (>500 lines).

**`exceptions.py`** - Slack-specific exceptions
- `SlackChannelError`
- `SlackThreadError`
- `SlackMessageError`

## Refactoring Strategy

### Phase 1: Create New Package Structure (Non-Breaking)

**Goal:** Set up new package without breaking existing code

**Steps:**
1. Create `lsimons_bot/` directory with `__init__.py`
2. Create `lsimons_bot/llm/` submodule
3. Create `lsimons_bot/slack/` submodule
4. Create `lsimons_bot/listeners/` to mirror current `listeners/`
5. Add backward-compatible imports in root-level `listeners/` (deprecation warnings)
6. Keep `app.py` and `app_oauth.py` at root (required by slack CLI)

**Duration:** 1-2 hours

### Phase 2: Extract LLM Module

**Goal:** Consolidate all LLM-related code

**2.1: Create `lsimons_bot/llm/client.py`**
- Copy `listeners/_llm.py` -> `lsimons_bot/llm/client.py`
- Refactor `LiteLLMClient` methods to be under 20 lines
- Extract helper methods:
  - `_prepare_messages()` - Handle system prompt injection
  - `_create_stream()` - Set up streaming request
  - `_process_chunk()` - Process individual chunk
- Add `exceptions.py` with specific error types
- Update exception handling to be specific

**2.2: Create `lsimons_bot/llm/prompt.py`**
- Copy `listeners/_prompt.py` -> `lsimons_bot/llm/prompt.py`
- Review and simplify functions for clarity:
  - `build_system_prompt()` - Already clear ✓
  - `get_suggested_prompts()` - Simplify channel topic filtering (currently 40+ lines, can be clearer)
  - `format_for_slack()` - Already clear ✓
  - `trim_messages_for_context()` - Refactor for clarity if needed (currently 35 lines, reasonable)
  - `build_message_context()` - Already clear ✓
- Only extract helpers if they improve clarity or are reused

**2.3: Create `lsimons_bot/llm/context.py`**
- Extract context-related functions from `_assistant_utils.py`:
  - `get_conversation_history()`
  - `format_thread_context()`
  - `is_assistant_message()`
- Add new functions:
  - `build_conversation_context()` - High-level context builder
  - `parse_message()` - Message parsing logic

**Duration:** 3-4 hours

### Phase 3: Extract Slack Module

**Goal:** Create reusable Slack operation utilities

**3.1: Create `lsimons_bot/slack/operations.py`**

Since the Slack wrapper code is relatively small (~150-200 lines total), consolidate all operations into one module for simplicity:

```python
from dataclasses import dataclass
from slack_sdk import WebClient

@dataclass
class ChannelInfo:
    """Channel information."""
    id: str
    name: str
    topic: str
    is_private: bool

# Channel operations
def get_channel_info(client: WebClient, channel_id: str) -> ChannelInfo:
    """Get channel information with error handling."""
    # Implementation

def format_channel_context(channel_info: ChannelInfo) -> str:
    """Format channel context for prompts."""
    # Implementation

# Thread operations
def set_thread_status(
    client: WebClient,
    channel_id: str,
    thread_id: str,
    status: str
) -> None:
    """Set assistant thread status."""
    # Implementation

def set_suggested_prompts(
    client: WebClient,
    channel_id: str,
    thread_id: str,
    prompts: list[dict[str, str]]
) -> None:
    """Set suggested prompts for thread."""
    # Implementation

# Message operations
def send_ephemeral(
    client: WebClient,
    channel_id: str,
    user_id: str,
    text: str,
    thread_ts: str | None = None
) -> None:
    """Send ephemeral message to user."""
    # Implementation
```

**Note:** Can be split into separate modules later if any category grows beyond ~150 lines.

**Duration:** 2 hours

### Phase 4: Refactor Event Handlers

**Goal:** Break down complex handler methods into clear, focused functions

**4.1: Refactor `assistant_user_message_handler`**

**Guiding Principles:**
- Each function should have **one clear responsibility**
- Extract when it **improves clarity or enables reuse**
- Don't extract purely to hit line count targets
- Typical function size: 15-50 lines (depends on complexity)
- Use descriptive names that explain what, not how

**Current structure (180 lines, mixed responsibilities):**
```python
async def assistant_user_message_handler(...):
    # All logic in one function
```

**New structure (orchestrator pattern):**
```python
# lsimons_bot/listeners/events/assistant_user_message.py

async def assistant_user_message_handler(
    ack: Ack,
    body: dict[str, Any],
    client: WebClient,
    logger_: logging.Logger,
) -> None:
    """Handle assistant user message event.
    
    Orchestrates: validation → context gathering → LLM call → response
    """
    await ack()
    
    try:
        request = _extract_request_data(body, logger_)
        await _process_user_message(request, client, logger_)
    except InvalidRequestError as e:
        logger_.warning("Invalid request: %s", e)
    except SlackChannelError as e:
        logger_.error("Channel error: %s", e)
        await _send_error_to_user(client, body, "Channel unavailable")
    except LLMAPIError as e:
        logger_.error("LLM error: %s", e)
        await _send_error_to_user(client, body, "AI assistant unavailable")
```

**Key extracted functions:**

```python
@dataclass
class UserMessageRequest:
    """Validated user message request data."""
    thread_id: str
    channel_id: str
    user_message: str

def _extract_request_data(
    body: dict[str, Any],
    logger_: logging.Logger
) -> UserMessageRequest:
    """Extract and validate request data from event body."""
    # ~15 lines: extract fields, validate, create dataclass

async def _process_user_message(
    request: UserMessageRequest,
    client: WebClient,
    logger_: logging.Logger,
) -> None:
    """Process user message: gather context, call LLM, send response.
    
    This is the main workflow orchestrator. Keep it readable by delegating
    each major step to a focused function.
    """
    # ~30 lines: Clear workflow with delegation
    await _set_thread_processing(client, request)
    
    channel_info = await _get_channel_info(client, request.channel_id)
    history = await _get_thread_history(client, request)
    
    response = await _generate_llm_response(request, channel_info, history)
    
    await _send_response(client, request, response)
    await _set_thread_ready(client, request)

async def _generate_llm_response(
    request: UserMessageRequest,
    channel_info: ChannelInfo,
    history: list[Message]
) -> str:
    """Generate LLM response using context."""
    # ~25 lines: Build context, configure LLM, call API, return response
    # This function does meaningful work - it's okay to be 20-30 lines

async def _send_error_to_user(
    client: WebClient,
    body: dict[str, Any],
    error_message: str
) -> None:
    """Send user-friendly error message."""
    # ~15 lines: Extract IDs, format message, send ephemeral
```

**Benefits:**
- Main handler is now ~20 lines (clear orchestration)
- Core logic function (~30 lines) remains readable
- Each function has clear purpose
- Easy to test independently
- No over-extraction of trivial helpers

**4.2: Refactor `assistant_thread_started_handler`**

**Current:** ~100 lines with duplicated prompt logic

**Strategy:**
- Main handler stays ~20-25 lines (orchestration)
- Extract: `_extract_thread_data()` (~10 lines)
- Extract: `_initialize_thread()` (~20 lines) - handles status and prompts
- **Reuse** `lsimons_bot.llm.prompt.get_suggested_prompts()` instead of duplicating
- Update exception handling to be specific

**4.3: Refactor `assistant_feedback_handler`**

**Current:** ~90 lines but already relatively well-structured

**Strategy:**
- Main handler stays ~15-20 lines
- Keep `_log_feedback_metrics()` as is (reasonable helper)
- Consider combining extraction + acknowledgment into single ~25 line function
- Update exception handling to be specific
- **Don't over-extract** - this handler is already close to ideal

**Duration:** 4-6 hours

### Phase 5: Fix Exception Handling

**Goal:** Replace all generic `except Exception` with specific handlers

**Strategy:**

1. **Define specific exception hierarchy:**

```python
# lsimons_bot/llm/exceptions.py
class LLMError(Exception):
    """Base exception for LLM operations."""
    pass

class LLMConfigurationError(LLMError):
    """LLM configuration is invalid."""
    pass

class LLMAPIError(LLMError):
    """LLM API request failed."""
    pass

class LLMTimeoutError(LLMAPIError):
    """LLM request timed out."""
    pass

class LLMQuotaExceededError(LLMAPIError):
    """LLM quota exceeded."""
    pass

# lsimons_bot/slack/exceptions.py
class SlackError(Exception):
    """Base exception for Slack operations."""
    pass

class SlackChannelError(SlackError):
    """Channel operation failed."""
    pass

class SlackThreadError(SlackError):
    """Thread operation failed."""
    pass

class InvalidRequestError(Exception):
    """Request validation failed."""
    pass
```

2. **Update `LiteLLMClient` exception handling:**

```python
# OLD (generic)
async def stream_completion(...):
    try:
        # ... streaming logic
    except Exception as e:
        logger.error(f"LiteLLM streaming error: {str(e)}")
        raise

# NEW (specific)
async def stream_completion(...):
    try:
        # ... streaming logic
    except TimeoutError as e:
        logger.error("LLM request timed out: %s", e)
        raise LLMTimeoutError(f"Request timed out: {e}") from e
    except openai.RateLimitError as e:
        logger.error("LLM quota exceeded: %s", e)
        raise LLMQuotaExceededError(f"Quota exceeded: {e}") from e
    except openai.APIError as e:
        logger.error("LLM API error: %s", e)
        raise LLMAPIError(f"API error: {e}") from e
    # Let other exceptions propagate naturally
```

3. **Update handler exception handling:**

```python
# OLD (swallows everything)
async def assistant_user_message_handler(...):
    try:
        # ... all logic
    except Exception as e:
        logger_.error("Error: %s", str(e), exc_info=True)

# NEW (specific handlers)
async def assistant_user_message_handler(...):
    try:
        request = _extract_request_data(body, logger_)
        await _process_user_message(request, client, logger_)
    except InvalidRequestError as e:
        logger_.warning("Invalid request: %s", e)
        # Don't notify user, request was malformed
    except SlackChannelError as e:
        logger_.error("Channel error: %s", e)
        await _notify_channel_error(client, body)
    except LLMAPIError as e:
        logger_.error("LLM error: %s", e, exc_info=True)
        await _notify_llm_error(client, body)
    except SlackApiError as e:
        logger_.error("Slack API error: %s", e, exc_info=True)
        # Slack issues are often transient, log but don't spam user
    # KeyboardInterrupt, SystemExit, etc. propagate naturally
```

**Duration:** 2-3 hours

### Phase 6: Update Entry Points

**Goal:** Update `app.py` and `app_oauth.py` imports to use new structure

**Steps:**
1. Keep `app.py` and `app_oauth.py` at root level (required by slack CLI)
2. Update imports from `listeners` to `lsimons_bot.listeners`
3. Ensure backward compatibility
4. Update documentation

**Note:** The slack CLI expects these files at the root level, so they cannot be moved.

**Duration:** 1 hour

### Phase 7: Update Tests

**Goal:** Mirror new structure in test suite

**Steps:**
1. Create `tests/llm/` directory
2. Move and update LLM tests:
   - `test_llm.py` -> `tests/llm/test_client.py`
   - `_test_prompt.py` -> `tests/llm/test_prompt.py`
   - `_test_assistant_utils.py` -> split into `test_context.py`
3. Create `tests/slack/` directory with new test files
4. Update listener tests for new structure
5. Ensure 80%+ coverage maintained

**Duration:** 3-4 hours

## Implementation Phases

### Phase 1: Foundation (2 hours)
- [ ] Create `lsimons_bot/` package structure
- [ ] Create `lsimons_bot/llm/` submodule
- [ ] Create `lsimons_bot/slack/` submodule
- [ ] Add exception hierarchies
- [ ] Create `lsimons_bot/listeners/` package structure

### Phase 2: LLM Module (4 hours)
- [ ] Migrate and refactor `client.py`
- [ ] Migrate and refactor `prompt.py`
- [ ] Create `context.py`
- [ ] Add specific exception handling
- [ ] Update unit tests

### Phase 3: Slack Module (2 hours)
- [x] Create `operations.py` with all Slack utilities ✅ COMPLETE
- [x] Add dataclasses for structured data ✅ COMPLETE
- [x] Add unit tests (47 tests, 100% coverage) ✅ COMPLETE
- [x] See history/PHASE_3_COMPLETION.md for details
- **Actual Time:** 1.5 hours (faster than estimate)
- **Results:** 303-line module, 100% test coverage, 0 basedpyright errors

### Phase 4: Refactor Handlers (4 hours)
- [ ] Move handlers to `lsimons_bot/listeners/`
- [ ] Refactor `assistant_user_message_handler` (2 hours) - simplified by operations module
- [ ] Refactor `assistant_thread_started_handler` (1 hour) - simplified by operations module
- [ ] Refactor `assistant_feedback_handler` (0.5 hours)
- [ ] Update integration tests (0.5 hours)
- **Note:** Reduced from 5 to 4 hours due to operations module simplifying handler logic

### Phase 5: Exception Handling (3 hours)
- [ ] Update all `except Exception` blocks
- [ ] Add specific exception types
- [ ] Update error logging
- [ ] Update tests for error cases

### Phase 6: Update Entry Points (1 hour)
- [ ] Update `app.py` imports (stays at root)
- [ ] Update `app_oauth.py` imports (stays at root)
- [ ] Add backward-compatible shims if needed

### Phase 7: Testing (4 hours)
- [ ] Reorganize test directory
- [ ] Update all import statements
- [ ] Add missing test coverage
- [ ] Ensure 80%+ coverage

### Phase 8: Documentation (2 hours)
- [ ] Update AGENTS.md
- [ ] Update spec documents
- [ ] Add docstrings to new modules
- [ ] Create migration guide

**Total Estimated Time:** 22 hours (revised down from 23 after Phase 3)
**Time Used So Far:** 1.5 hours (Phase 3 actual)
**Time Remaining:** ~20.5 hours

## Testing Requirements

### Unit Test Coverage

Maintain minimum 80% coverage for:
- **All refactored modules**: `client.py`, `prompt.py`, `context.py`
- **All new modules**: `channel.py`, `thread.py`, `message.py`
- **All refactored handlers**: All listener functions

### Test Categories

1. **Unit Tests** (existing + new)
   - LLM client operations
   - Prompt building and formatting
   - Context management
   - Channel operations
   - Thread operations
   - Message operations

2. **Integration Tests** (ensure still pass)
   - Handler workflows
   - End-to-end message processing
   - Error handling flows

3. **New Tests Required**
   - Specific exception handling
   - Extracted helper functions
   - Slack utility functions

### Test Migration Strategy

```
OLD: tests/listeners/_test_assistant_utils.py
NEW: tests/llm/test_context.py
     tests/slack/test_thread.py

OLD: tests/listeners/test_llm.py
NEW: tests/llm/test_client.py

OLD: tests/listeners/_test_prompt.py
NEW: tests/llm/test_prompt.py

NEW: tests/slack/test_channel.py
NEW: tests/slack/test_message.py
```

## Migration Guide

### For Imports

```python
# OLD
from listeners._llm import LiteLLMClient, create_llm_client
from listeners._prompt import build_system_prompt, get_suggested_prompts
from listeners._assistant_utils import get_conversation_history

# NEW
from lsimons_bot.llm.client import LiteLLMClient, create_llm_client
from lsimons_bot.llm.prompt import build_system_prompt, get_suggested_prompts
from lsimons_bot.llm.context import get_conversation_history
```

### For app.py and app_oauth.py

```python
# OLD (in app.py and app_oauth.py)
from listeners import register_listeners

# NEW (in app.py and app_oauth.py)
from lsimons_bot.listeners import register_listeners

# Note: app.py and app_oauth.py remain at root level (required by slack CLI)
```

### For Exception Handling

```python
# OLD
try:
    result = await llm_client.stream_completion(...)
except Exception as e:
    logger.error("Error: %s", e)

# NEW
from lsimons_bot.llm.exceptions import LLMAPIError, LLMTimeoutError

try:
    result = await llm_client.stream_completion(...)
except LLMTimeoutError as e:
    logger.error("LLM timeout: %s", e)
    # Handle timeout specifically
except LLMAPIError as e:
    logger.error("LLM API error: %s", e)
    # Handle API error specifically
```

### For Slack Operations

```python
# OLD
try:
    channel_info = client.conversations_info(channel=channel_id)
    channel_name = channel_info.get("channel", {}).get("name", channel_id)
except SlackApiError as e:
    logger.warning("Failed to get channel info: %s", e)

# NEW
from lsimons_bot.slack.channel import get_channel_info
from lsimons_bot.slack.exceptions import SlackChannelError

try:
    channel_info = get_channel_info(client, channel_id)
    channel_name = channel_info.name
except SlackChannelError as e:
    logger.warning("Channel error: %s", e)
```

## Success Criteria

### Code Quality Metrics

- [ ] Methods have single, clear responsibilities (typically 15-50 lines)
- [ ] Zero generic `except Exception` blocks (use specific types)
- [ ] Zero `flake8` warnings
- [ ] Zero `basedpyright` errors
- [ ] 80%+ test coverage maintained
- [ ] All tests passing
- [ ] Code is more readable than before (subjective but important)

### Structural Goals

- [ ] Proper `lsimons_bot` root package
- [ ] Dedicated `lsimons_bot/llm` submodule
- [ ] Dedicated `lsimons_bot/slack` submodule
- [ ] Clear separation of concerns
- [ ] No code duplication
- [ ] Consistent import patterns

### Functional Goals

- [ ] All existing functionality preserved
- [ ] No regression in behavior
- [ ] Better error messages for users
- [ ] Improved debugging capabilities
- [ ] Better testability

## Risks and Mitigations

### Risk 1: Breaking Changes
**Mitigation:** 
- Incremental refactoring
- Maintain backward compatibility during transition
- Comprehensive test suite

### Risk 2: Test Coverage Drop
**Mitigation:**
- Write tests alongside refactoring
- Check coverage after each phase
- Don't merge if coverage drops

### Risk 3: Import Path Confusion
**Mitigation:**
- Clear migration guide
- Deprecation warnings in old locations
- Update all files consistently

### Risk 4: Time Overrun
**Mitigation:**
- Break into small phases
- Each phase can be merged independently
- Prioritize critical issues (exception handling, long methods)

## Appendix A: File-by-File Checklist

### LLM Module

- [ ] `lsimons_bot/llm/__init__.py` - Package initialization
- [ ] `lsimons_bot/llm/client.py` - LiteLLM client (from `_llm.py`)
- [ ] `lsimons_bot/llm/prompt.py` - Prompt engineering (from `_prompt.py`)
- [ ] `lsimons_bot/llm/context.py` - Context management (from `_assistant_utils.py`)
- [ ] `lsimons_bot/llm/exceptions.py` - LLM exceptions

### Slack Module

- [ ] `lsimons_bot/slack/__init__.py` - Package initialization
- [ ] `lsimons_bot/slack/operations.py` - All Slack operations (consolidated)
- [ ] `lsimons_bot/slack/exceptions.py` - Slack exceptions

### Listeners

- [ ] `lsimons_bot/listeners/events/assistant_user_message.py` - Refactor handler
- [ ] `lsimons_bot/listeners/events/assistant_thread_started.py` - Refactor handler
- [ ] `lsimons_bot/listeners/actions/assistant_feedback.py` - Refactor handler

### Tests

- [ ] `tests/llm/test_client.py` - Client tests
- [ ] `tests/llm/test_prompt.py` - Prompt tests
- [ ] `tests/llm/test_context.py` - Context tests
- [ ] `tests/slack/test_operations.py` - All Slack operation tests
- [ ] Update all listener tests

### Entry Points

- [ ] Update `app.py` imports (stays at root)
- [ ] Update `app_oauth.py` imports (stays at root)

### Cleanup

- [ ] Remove old `listeners/_llm.py`
- [ ] Remove old `listeners/_prompt.py`
- [ ] Remove old `listeners/_assistant_utils.py`
- [ ] Consider deprecating old `listeners/` or making it a shim
- [ ] Update all import statements
- [ ] Update documentation

## Appendix B: Pythonic Refactoring Examples

### Example 1: Handler Orchestration

**Before (180 lines, mixed concerns):**
```python
async def assistant_user_message_handler(ack, body, client, logger_):
    _ = ack()
    try:
        # Extract
        assistant_thread_id = body.get("assistant_thread_id")
        channel_id = body.get("channel_id")
        user_message = body.get("text", "").strip()
        # Validate
        if not assistant_thread_id or not channel_id:
            logger_.warning("Missing required fields: %s", body)
            return
        # Set status
        try:
            _ = client.assistant.threads.set_status(...)
        except SlackApiError as e:
            logger_.warning("Failed to set thread status: %s", str(e))
        # Get channel info
        try:
            channel_info = client.conversations_info(channel=channel_id)
            channel_name = channel_info.get("channel", {}).get("name", channel_id)
        except SlackApiError as e:
            logger_.warning("Failed to get channel info: %s", e)
            channel_name = channel_id
        # ... 150 more lines ...
    except Exception as e:
        logger_.error("Error: %s", str(e), exc_info=True)
```

**After (20 lines, clear orchestration):**
```python
async def assistant_user_message_handler(ack, body, client, logger_):
    """Handle assistant user message event."""
    await ack()
    
    try:
        request = _extract_request_data(body, logger_)
        await _process_user_message(request, client, logger_)
    except InvalidRequestError as e:
        logger_.warning("Invalid request: %s", e)
    except SlackChannelError as e:
        logger_.error("Channel error: %s", e)
        await _send_error_to_user(client, body, "Channel unavailable")
    except LLMAPIError as e:
        logger_.error("LLM error: %s", e)
        await _send_error_to_user(client, body, "AI assistant unavailable")
```

### Example 2: When NOT to Extract

**Don't do this (over-extraction):**
```python
async def _process_user_message(request, client, logger_):
    await _step1(request, client)
    await _step2(request, client)
    await _step3(request, client)
    await _step4(request, client)
    await _step5(request, client)

async def _step1(request, client):
    await client.assistant.threads.set_status(...)  # 3 lines, used once
```

**Do this (reasonable extraction):**
```python
async def _process_user_message(request, client, logger_):
    """Process user message: gather context, call LLM, send response."""
    # Set processing state
    await client.assistant.threads.set_status(
        channel_id=request.channel_id,
        thread_id=request.thread_id,
        status="running"
    )
    
    # Gather context
    channel_info = await _get_channel_info(client, request.channel_id)
    history = await _get_thread_history(client, request)
    
    # Generate and send response
    response = await _generate_llm_response(request, channel_info, history)
    await _send_response(client, request, response)
    
    # Set ready state
    await client.assistant.threads.set_status(
        channel_id=request.channel_id,
        thread_id=request.thread_id,
        status="waiting_on_user"
    )
```

**Why this is better:**
- ~30 lines but very readable
- Clear workflow visible in one place
- Only extracts substantial operations
- Inline simple operations with descriptive comments

## Appendix C: Exception Hierarchy

```
Exception
├── LLMError (lsimons_bot/llm/exceptions.py)
│   ├── LLMConfigurationError
│   ├── LLMAPIError
│   │   ├── LLMTimeoutError
│   │   └── LLMQuotaExceededError
│   └── LLMResponseError
│
├── SlackError (lsimons_bot/slack/exceptions.py)
│   ├── SlackChannelError
│   ├── SlackThreadError
│   └── SlackMessageError
│
└── InvalidRequestError (lsimons_bot/listeners/exceptions.py)
```

## Important Notes

### Slack CLI Constraints

The `app.py` and `app_oauth.py` files **must remain at the root level** because the Slack CLI expects them there. They cannot be moved into the `lsimons_bot` package. However, their imports can be updated to use the new package structure:

```python
# app.py and app_oauth.py will stay at root and import from the new structure
from lsimons_bot.listeners import register_listeners
```

### Pythonic Guidelines

**Remember:**
- **Clarity over brevity**: A clear 35-line function beats obscure 5-line functions
- **Extract with purpose**: Only extract when it improves clarity or enables reuse
- **Single responsibility**: Not the same as "20 lines max"
- **Readability counts**: Code is read far more than it's written
- **Flat is better than nested**: Don't over-modularize small codebases
- **Pragmatism**: Python favors practical solutions over dogmatic rules

### Backward Compatibility

During the transition, consider keeping the old `listeners/` directory as a compatibility shim with deprecation warnings, then remove it once all code is migrated.

## Phase 3 Status Update (2025-12-12)

✅ **Phase 3 COMPLETE:** Slack operations module successfully created
- 303-line consolidated module with 7 reusable operations
- 47 comprehensive unit tests with 100% coverage
- 0 basedpyright errors, fully type-safe
- Actual time: 1.5 hours (ahead of estimate)
- See `history/PHASE_3_COMPLETION.md` for full details

## Next Steps

1. ✅ Phases 1-3 complete and ready for Phase 4
2. Phase 4: Refactor Event Handlers (estimated 4 hours)
   - Use new operations module in listener handlers
   - Simplify handler logic by delegating to operations
   - Add tests for handler-specific logic
3. Monitor Phase 4 for learnings that may affect Phase 5
4. Expected timeline: Phase 4 should complete within 4 hours based on operations module readiness
5. Iterate through phases with testing at each step

---

**Document Status:** Ready for review
**Author:** AI Assistant
**Revision:** Updated to keep app.py and app_oauth.py at root (slack CLI requirement)