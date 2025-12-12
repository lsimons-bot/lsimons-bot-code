# AI Assistant Feature - Beads Issues Summary

**Epic:** `lsimons-bot-czw`  
**Status:** Planning & Ready for Implementation  
**Total Issues:** 11  
**Estimated Effort:** 12-17 hours

---

## Issue Dependency Map

```
lsimons-bot-czw (EPIC)
│
├─ lsimons-bot-dyz (Spec) ──┐ BLOCKS
│                            │
│                    ┌───────┴─────────┐
│                    │                 │
│         lsimons-bot-ocl         lsimons-bot-u01
│         (LiteLLM Module)        (Config Slack App)
│                │                     │
│                └──────────┬──────────┘
│                           │
│         ┌─────────────────┼─────────────────┐
│         │                 │                 │
│    lsimons-bot-c6r   lsimons-bot-7gl   lsimons-bot-urs
│    (thread_started)  (user_message)     (feedback)
│         │                 │                 │
│         └────────┬────────┴────────┬────────┘
│                  │                 │
│         lsimons-bot-oaw    lsimons-bot-ad5
│         (utils)            (prompt engine)
│                  │                 │
│                  └────────┬────────┘
│                           │
│         ┌─────────────────┼─────────────────┐
│         │                 │                 │
│    lsimons-bot-852   lsimons-bot-cqi   lsimons-bot-cyf
│    (tests)           (docs spec)       (README)
```

---

## Phase 1: Foundation (Blockers for all other work)

### `lsimons-bot-dyz`: Spec: AI Assistant Integration with LiteLLM
- **Status:** Open
- **Priority:** 1 (High)
- **Type:** Task
- **Dependencies:** None (but blocks other work)
- **Description:**
  - Create comprehensive design spec for AI assistant feature
  - Cover: Slack Assistant API patterns, LiteLLM proxy integration, thread context flow
  - Include: Configuration requirements, error handling strategy, data flow diagram
  - Reference Slack API docs and project patterns spec
  - Output: `docs/spec/003-ai-assistant-architecture.md`

**Ready to work on this first. Get human approval before proceeding with implementation phases.**

---

## Phase 2: Infrastructure (Blocked by: Spec)

### `lsimons-bot-ocl`: Implement LiteLLM integration module
- **Status:** Open
- **Priority:** 1 (High)
- **Type:** Task
- **Depends on:** `lsimons-bot-dyz` (blocks)
- **Description:**
  - Create `listeners/_llm.py` module
  - OpenAI SDK wrapper pointing to LiteLLM proxy (https://litellm.sbp.ai/)
  - Support streaming via OpenAI SDK compatibility
  - Handle `LITELLM_API_KEY` and `LITELLM_API_BASE` env vars
  - Error handling and retries
  - Full type annotations
  - Unit tests with 80%+ coverage (mock HTTP responses, streaming chunks, errors)

### `lsimons-bot-u01`: Configure Slack app for Assistant feature
- **Status:** Open
- **Priority:** 1 (High)
- **Type:** Task
- **Depends on:** `lsimons-bot-dyz` (blocks)
- **Description:**
  - Update `manifest.json`:
    - Add Agents & AI Apps feature flag
    - Add scopes: `assistant:write`, `chat:write`, `im:history`
    - Subscribe to events: `assistant_thread_started`, `assistant_thread_context_changed`, `message.im`
  - Update `app.py`:
    - Add `ignoring_self_assistant_message_events_enabled=False`
    - Create and register Assistant middleware
  - Add `LITELLM_*` env vars to `.env.example`
  - Update `requirements.txt` if needed

---

## Phase 3: Core Listeners (Blocked by: Infrastructure)

### `lsimons-bot-c6r`: Implement Assistant thread_started listener
- **Status:** Open
- **Priority:** 1 (High)
- **Type:** Task
- **Depends on:** `lsimons-bot-dyz`, `lsimons-bot-ocl`, `lsimons-bot-u01`
- **Description:**
  - Create `listeners/events/assistant_thread_started.py`
  - Implements `@assistant.thread_started` event handler
  - Send welcome greeting message
  - Generate and set suggested prompts (based on channel context)
  - Store thread context
  - Use `get_thread_context` and `set_suggested_prompts` utilities
  - Error handling and logging
  - Tests with mocked Slack client

### `lsimons-bot-7gl`: Implement Assistant user_message listener
- **Status:** Open
- **Priority:** 1 (High)
- **Type:** Task
- **Depends on:** `lsimons-bot-dyz`, `lsimons-bot-ocl`, `lsimons-bot-u01`
- **Description:**
  - Create `listeners/events/assistant_user_message.py`
  - Implements `@assistant.user_message` event handler
  - Retrieve conversation history from thread
  - Set loading status via `set_status`
  - Call LiteLLM via `listeners/_llm.py` module
  - Stream response using `client.chat_stream()`
  - Error handling with user-friendly messages
  - Tests with mocked LLM and Slack streaming

### `lsimons-bot-urs`: Implement Assistant feedback action handler
- **Status:** Open
- **Priority:** 1 (High)
- **Type:** Task
- **Depends on:** `lsimons-bot-dyz`, `lsimons-bot-ocl`, `lsimons-bot-u01`
- **Description:**
  - Create `listeners/actions/assistant_feedback.py`
  - Implements `@app.action('feedback')` for thumbs up/down buttons
  - Log feedback type and message metadata
  - Send acknowledgment ephemeral message
  - Consider storing feedback for future analysis
  - Tests verifying logging and API calls

### `lsimons-bot-oaw`: Implement thread context utilities
- **Status:** Open
- **Priority:** 1 (High)
- **Type:** Task
- **Depends on:** `lsimons-bot-dyz`, `lsimons-bot-ocl`, `lsimons-bot-u01`
- **Description:**
  - Create `listeners/_assistant_utils.py` with helper functions:
    - `get_conversation_history(client, channel, thread_ts)` - formats thread replies as message dicts
    - `format_thread_context()` - formats channel/thread info for prompts
    - `is_assistant_message(msg)` - detects bot messages
  - Full type annotations
  - Unit tests with mocked API responses

---

## Phase 4: Enhancements (Blocked by: Core Listeners)

### `lsimons-bot-ad5`: Implement prompt engineering module
- **Status:** Open
- **Priority:** 1 (High)
- **Type:** Task
- **Depends on:** Core listeners (discovered-from)
- **Description:**
  - Create `listeners/_prompt.py`
  - System prompt template (professional tone, Slack markdown awareness, context injection)
  - Suggested prompt templates ("Summarize channel", "Answer question", "Brainstorm ideas")
  - Response formatting for Slack (markdown → text, preserve Slack mentions)
  - Token-aware prompt trimming
  - Tests: prompt composition, context injection, formatting

---

## Phase 5: Testing & Documentation (Blocked by: Enhancements)

### `lsimons-bot-852`: Comprehensive test suite for AI assistant feature
- **Status:** Open
- **Priority:** 2 (Medium)
- **Type:** Task
- **Depends on:** All implementation issues
- **Description:**
  - Create test suite achieving 80%+ coverage:
    - `tests/listeners/events/test_assistant_thread_started.py`
    - `tests/listeners/events/test_assistant_user_message.py`
    - `tests/listeners/events/test_assistant_context_changed.py`
    - `tests/listeners/actions/test_assistant_feedback.py`
    - `tests/listeners/test_assistant_utils.py`
    - `tests/listeners/test_prompt.py`
    - `tests/listeners/test_llm.py`
  - Integration tests for full flow
  - Fixtures for Slack payloads and mocked responses
  - Run pytest with coverage report, ensure all branches covered

### `lsimons-bot-cqi`: Documentation: AI Assistant architecture spec
- **Status:** Open
- **Priority:** 2 (Medium)
- **Type:** Task
- **Depends on:** All implementation issues
- **Description:**
  - Create `docs/spec/003-ai-assistant-architecture.md`
  - Document:
    - Overview of Slack Assistant API (events)
    - LiteLLM integration pattern
    - Thread context flow with DefaultThreadContextStore
    - Module structure and file organization
    - Configuration (env vars, manifest.json)
    - Data flow diagram
    - Example usage and common patterns
  - Keep concise, reference shared patterns

### `lsimons-bot-cyf`: Update README and setup instructions for AI assistant
- **Status:** Open
- **Priority:** 2 (Medium)
- **Type:** Task
- **Depends on:** All implementation issues
- **Description:**
  - Add to `README.md`:
    - High-level overview of AI assistant feature
    - Quick start for enabling in Slack workspace (note: paid plan required)
    - LiteLLM proxy configuration example
    - Environment variable documentation
    - Link to `docs/spec/003-ai-assistant-architecture.md`
    - Troubleshooting section for common issues

---

## Starting Point: Code Organization

```
lsimons-bot/
├── listeners/
│   ├── events/
│   │   ├── __init__.py                     (register())
│   │   ├── assistant_thread_started.py     (NEW - issue c6r)
│   │   ├── assistant_user_message.py       (NEW - issue 7gl)
│   │   └── assistant_context_changed.py    (NEW - implied, created with thread_started)
│   │
│   ├── actions/
│   │   ├── __init__.py                     (register())
│   │   └── assistant_feedback.py           (NEW - issue urs)
│   │
│   ├── _llm.py                             (NEW - issue ocl)
│   ├── _assistant_utils.py                 (NEW - issue oaw)
│   └── _prompt.py                          (NEW - issue ad5)
│
├── tests/
│   └── listeners/
│       ├── events/
│       │   ├── test_assistant_thread_started.py
│       │   ├── test_assistant_user_message.py
│       │   └── test_assistant_context_changed.py
│       ├── actions/
│       │   └── test_assistant_feedback.py
│       ├── test_llm.py
│       ├── test_assistant_utils.py
│       └── test_prompt.py
│
├── docs/
│   └── spec/
│       └── 003-ai-assistant-architecture.md   (NEW - issue cqi)
│
├── app.py                                  (UPDATE - issue u01)
├── manifest.json                           (UPDATE - issue u01)
├── requirements.txt                        (UPDATE - issue u01)
├── README.md                               (UPDATE - issue cyf)
└── .env.example                            (UPDATE - issue u01)
```

---

## Configuration Checklist

### Environment Variables Required
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
LITELLM_API_KEY=sk-...
LITELLM_API_BASE=https://litellm.sbp.ai/
LITELLM_MODEL=gpt-4o-mini          (or your preferred model)
```

### Slack App Manifest Changes
- [x] Enable "Agents & AI Apps" feature
- [x] Add scopes: `assistant:write`, `chat:write`, `im:history`
- [x] Subscribe to: `assistant_thread_started`, `assistant_thread_context_changed`, `message.im`

### Python Dependencies
- `slack-bolt>=1.27.0` (already have)
- `requests>=2.31.0` (for LiteLLM HTTP calls)

---

## Success Criteria

By the end of this feature work, you should have:

✅ Users can open assistant threads in Slack channels  
✅ Assistant responds to user messages using LiteLLM proxy  
✅ Responses stream in real-time  
✅ Thread context persists across channel switches  
✅ Users can rate responses (feedback buttons)  
✅ Error handling is graceful (no 500s, helpful messages)  
✅ 80%+ test coverage (lines, branches, functions)  
✅ Zero flake8/black violations  
✅ Full type annotations throughout  
✅ Clear architecture documentation  

---

## Next Steps

1. **Review planning document:** `history/AI_ASSISTANT_PLAN.md`
2. **Review this summary:** `history/AI_ASSISTANT_ISSUES_SUMMARY.md`
3. **Implement spec first:** Work on `lsimons-bot-dyz`
4. **Get human approval** of spec before proceeding
5. **Execute phases 2-5** in dependency order using `bd ready` to find unblocked work
