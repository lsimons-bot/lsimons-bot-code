# AI Assistant Feature Plan

**Status:** Planning  
**Created:** 2025-12-12  
**Epic:** lsimons-bot-czw

## Overview

Add an AI assistant feature to the Slack bot using Slack's Agents & AI Apps platform and LiteLLM API proxy for LLM interactions.

## Key Features

### Slack Platform Integration
- **Assistant Threads**: Users can open AI assistant threads in Slack channels
- **Split View UI**: Conversations happen in a dedicated split-panel view
- **Thread Context**: Automatically tracks which channel the assistant is helping with
- **Loading States**: Shows "thinking..." status during LLM processing
- **Suggested Prompts**: Offers quick-start suggestions when thread starts
- **Text Streaming**: Streams LLM responses for natural chat experience
- **Feedback Buttons**: Users can rate responses (thumbs up/down)

### LiteLLM Integration
- Use LiteLLM API proxy at `https://litellm.sbp.ai/` instead of direct OpenAI calls
- Allows model flexibility and centralized LLM management
- Requires authentication (API key in environment)
- Supports streaming for real-time response updates

## Architecture

### Components

```
listeners/
├── events/
│   ├── __init__.py
│   ├── assistant_thread_started.py      # NEW: Handle thread creation
│   ├── assistant_thread_context.py      # NEW: Handle context changes
│   └── assistant_user_message.py        # NEW: Handle user messages
├── actions/
│   └── assistant_feedback.py            # NEW: Handle feedback buttons
└── _utils.py                            # NEW: LLM interaction helpers

src/
├── assistant/                           # NEW: Core assistant logic
│   ├── __init__.py
│   ├── llm_client.py                   # NEW: LiteLLM wrapper
│   ├── prompt_engine.py                # NEW: Prompt engineering
│   ├── context_manager.py              # NEW: Thread context management
│   └── message_formatter.py            # NEW: Slack message formatting
└── config.py                           # NEW: Configuration (LiteLLM URL, etc.)

tests/
├── listeners/events/
│   ├── test_assistant_thread_started.py
│   ├── test_assistant_thread_context.py
│   └── test_assistant_user_message.py
├── listeners/actions/
│   └── test_assistant_feedback.py
└── assistant/
    ├── test_llm_client.py
    ├── test_prompt_engine.py
    ├── test_context_manager.py
    └── test_message_formatter.py
```

### Data Flow

1. **User opens thread** → `assistant_thread_started` event
   - Say greeting message
   - Show suggested prompts (e.g., "Summarize channel")
   - Store thread context (channel_id, thread_ts)

2. **Thread context changes** → `assistant_thread_context_changed` event
   - Update stored context when user switches channels
   - Automatically saved as message metadata

3. **User sends message** → `message.im` event
   - Retrieve thread history and context
   - Build message list with role (user/assistant)
   - Call LiteLLM with prompt and history
   - Stream response using `chat_stream()`
   - Append feedback buttons

4. **User provides feedback** → `block_actions` event
   - Log feedback (positive/negative)
   - Send acknowledgment message

## Configuration Requirements

### Slack App Settings
- ✅ Enable **Agents & AI Apps** feature in app settings
- ✅ Add scopes: `assistant:write`, `chat:write`, `im:history`
- ✅ Subscribe to events: `assistant_thread_started`, `assistant_thread_context_changed`, `message.im`

### Environment Variables
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
LITELLM_API_KEY=sk-...          # LiteLLM API key
LITELLM_API_BASE=https://litellm.sbp.ai/
LITELLM_MODEL=gpt-4o-mini       # Or any model supported by proxy
```

### Dependencies
```
slack-bolt>=1.27.0
requests>=2.31.0              # For LiteLLM API calls
python-dotenv>=1.0.0          # For environment variables
```

## Implementation Tasks (Beads Issues)

### Phase 1: Foundation
- [ ] **dyz**: Spec document with detailed design
- [ ] **TBD**: Set up `src/assistant/` module structure
- [ ] **TBD**: Implement LiteLLM client wrapper
- [ ] **TBD**: Implement prompt engineering module
- [ ] **TBD**: Implement context manager with DefaultThreadContextStore

### Phase 2: Event Handlers
- [ ] **TBD**: Create `assistant_thread_started` listener
- [ ] **TBD**: Create `assistant_thread_context_changed` listener
- [ ] **TBD**: Create `assistant_user_message` listener with streaming
- [ ] **TBD**: Create feedback action handler

### Phase 3: Polish
- [ ] **TBD**: Add message formatting for Slack (markdown → Block Kit)
- [ ] **TBD**: Implement error handling and user-friendly error messages
- [ ] **TBD**: Add suggested prompts configuration
- [ ] **TBD**: Comprehensive test suite (80%+ coverage)

### Phase 4: Documentation
- [ ] **TBD**: Update manifest.json with new event subscriptions
- [ ] **TBD**: Create assistant feature documentation
- [ ] **TBD**: Add setup instructions to README

## Testing Strategy

### Unit Tests
- LiteLLM client: mock API calls, test streaming, error handling
- Prompt engine: test prompt building, context injection
- Context manager: test get/save operations
- Message formatter: test Slack Block Kit generation
- Event handlers: mock Slack client, test listener logic

### Test Coverage Target
- Minimum 80% line/branch/function coverage
- All public APIs tested
- Error paths covered

### Integration Points to Mock
- `slack_sdk.WebClient` - mock conversations_replies, chat_postMessage
- LiteLLM HTTP API - mock streaming responses
- Thread context storage - use in-memory store for tests

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| LiteLLM API downtime | Implement retry logic, graceful error messages |
| Token/context limits | Implement message history trimming, max length checks |
| Cost of API calls | Monitor usage, set rate limits if needed |
| Slack API rate limits | Use appropriate backoff, batch operations where possible |
| User confusion with AI | Clear suggested prompts, honest error messages |

## Success Criteria

- ✅ Users can open assistant threads in channels
- ✅ Assistant responds to user messages using LiteLLM
- ✅ Responses stream in real-time
- ✅ Thread context persists across channel switches
- ✅ Users can rate responses (feedback)
- ✅ Error handling is graceful (no 500s, helpful messages)
- ✅ 80%+ test coverage
- ✅ Zero flake8/black violations
- ✅ Full type annotations

## References

- Slack Bolt AI Apps: https://docs.slack.dev/tools/bolt-python/concepts/ai-apps/
- Slack AI Overview: https://docs.slack.dev/ai/
- LiteLLM Docs: https://docs.litellm.ai/
- Project Specs: `docs/spec/002-slack-listener-patterns.md`
