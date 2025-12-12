# 003 - AI Assistant Integration with OpenAI Agents + LiteLLM

**Purpose:** Enable users to interact with AI assistants in Slack channels using split-view threads. The assistant uses the OpenAI Agents SDK with LiteLLM integration to support 100+ LLM providers via a centralized LiteLLM proxy, providing text streaming, thread context, suggested prompts, and feedback mechanisms.

**Requirements:**
- Support Slack Assistant API events (thread_started, context_changed, user_message)
- Integrate with OpenAI Agents SDK using LiteLLM for unified LLM access
- Connect to existing LiteLLM proxy at https://litellm.sbp.ai/
- Maintain thread context using Slack Assistant API context retrieval
- Stream responses to users in real-time
- Handle errors gracefully with user-friendly messages
- Support feedback mechanisms (thumbs up/down on responses)
- Configure required scopes, events, and environment variables
- Provide suggested prompts for user guidance

**Design Approach:**

### 1. Slack Assistant API Integration

The Slack Assistant API provides three main events:
- `assistant_thread_started`: Fired when user opens AI thread in a channel
- `assistant_context_changed`: Fired when thread context (selected messages/files) changes
- `assistant_user_message`: Fired when user sends message in assistant thread

These events arrive as part of the `assistant_events` payload in the socket mode connection.

### 2. OpenAI Agents + LiteLLM Integration

Use the OpenAI Agents SDK with LiteLLM model support to leverage your existing LiteLLM proxy:

**Key Benefits:**
- Single unified interface for 100+ LLM providers via LiteLLM proxy
- Centralized model management and cost tracking
- No direct provider API keys needed in Slack bot (only proxy auth)
- Built-in streaming and token usage tracking
- Agent framework handles complex multi-turn conversations

**Architecture:**
- Slack bot runs OpenAI Agents with `LitellmModel` backend
- `LitellmModel` configured to call your LiteLLM proxy at `https://litellm.sbp.ai/`
- Proxy handles provider routing and authentication
- Bot uses async agents for non-blocking request handling

**Model Configuration:**
- Model format: `provider/model-name` (e.g., `openai/gpt-4`, `anthropic/claude-3-sonnet-20240229`)
- Proxy URL: `https://litellm.sbp.ai/`
- Authentication: Proxy API key via `LITELLM_API_KEY` environment variable
- Model specified in config with optional custom system prompt

### 3. Thread Context Flow

Thread context represents the conversation and selected channel context:
- Context includes: thread_id, channel_id, user_id, selected messages, files, and custom data
- Thread context retrieved via `client.assistant.threads.retrieve(channel_id, thread_id)`
- Messages in context are converted to agent conversation history
- Build agent state: system message + context messages + user message

### 4. Event Handler Architecture

Create three event listeners in `listeners/events/`:
- `assistant_thread_started_handler.py`: Initialize thread, send welcome/suggested prompts
- `assistant_context_changed_handler.py`: Acknowledge context change, update tracking
- `assistant_user_message_handler.py`: Main handler - retrieve context, create agent, run with user message, stream response

Pattern follows [002-slack-listener-patterns.md]:
```python
async def assistant_user_message_handler(ack: Ack, body: dict[str, Any], client, logger) -> None:
    ack()
    # Extract thread_id, channel_id, user_message from body
    # Retrieve thread context via client.assistant.threads.retrieve()
    # Create agent with LitellmModel pointing to proxy
    # Run agent with user message and context
    # Stream response chunks to thread
    # Save response and suggested next prompts
```

### 5. Agent Configuration

Create a factory function to initialize agents with consistent configuration:

```python
from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

def create_assistant_agent(
    system_prompt: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> Agent:
    """Create configured assistant agent with LiteLLM proxy."""
    model = model or os.getenv("ASSISTANT_MODEL", "openai/gpt-4")
    api_key = api_key or os.getenv("LITELLM_API_KEY")
    
    return Agent(
        name="Slack Assistant",
        instructions=system_prompt or os.getenv("ASSISTANT_SYSTEM_PROMPT", "You are a helpful assistant."),
        model=LitellmModel(
            model=model,
            api_key=api_key,
            base_url="https://litellm.sbp.ai/",  # Proxy endpoint
        ),
    )
```

### 6. Error Handling Strategy

- LiteLLM/Agent errors (invalid model, auth failure): Log error, send user-friendly message
- Network errors: Log and send "Service temporarily unavailable"
- Missing context: Log warning, continue with user message only
- Invalid responses: Log error, send message with error details
- Timeouts: Set 60s timeout on agent runs, catch and handle gracefully
- Rate limiting: Track per-user/channel requests, implement backoff if needed

All errors logged at appropriate levels (warn for user-facing, error for system issues).

### 7. Configuration Requirements

**Slack App Scopes:**
- `assistant:write` - Create/update assistant responses
- `assistant:read` - Read thread context
- `channels:history` - Access channel message history for context
- `chat:write` - Send messages in channels

**Events to subscribe:**
- `assistant_thread_started`
- `assistant_context_changed`
- `assistant_user_message`

**Environment Variables:**
- `LITELLM_PROXY_URL`: Base URL of LiteLLM proxy (default: `https://litellm.sbp.ai/`)
- `LITELLM_API_KEY`: API key for proxy authentication (required)
- `ASSISTANT_MODEL`: Model to use (format: `provider/model-name`, e.g., `openai/gpt-4`)
- `ASSISTANT_SYSTEM_PROMPT`: Custom system prompt for assistant personality (optional)

**Requirements Update:**
- Add `openai-agents[litellm]` to dependencies

### 8. Data Flow Diagram

```
User opens AI thread
        ↓
[assistant_thread_started] event
        ↓
Initialize thread, send welcome/suggested prompts
        ↓
User selects context (messages/files)
        ↓
[assistant_context_changed] event
        ↓
Acknowledge context change
        ↓
User sends message
        ↓
[assistant_user_message] event
        ↓
Retrieve thread context via client.assistant.threads.retrieve()
        ↓
Create Agent with LitellmModel(base_url=https://litellm.sbp.ai/)
        ↓
Build message history from context + user message
        ↓
Run agent.run_async(user_message, context_history)
        ↓
Stream response chunks to user in thread
        ↓
Save response + suggested next prompts
```

### 9. Testing Approach

**Unit Tests:**
- Mock LiteLLM/Agent responses, test prompt construction
- Test context extraction from Slack payloads
- Test error handling (auth errors, timeouts, invalid responses)
- Test message streaming and formatting logic
- Test agent factory configuration

**Integration Tests:**
- Mock Slack client and socket mode
- Mock LiteLLM proxy responses
- Test full event flow: thread_started → context_changed → user_message
- Verify assistant_threads.retrieve() calls
- Verify response is properly streamed and saved

**Smoke Tests:**
- Import all assistant listeners and Agent classes
- Create app, call register(app)
- Verify no exceptions on import

**E2E Tests (Manual):**
- Test in actual Slack workspace with proxy configured
- Verify streaming works end-to-end
- Test error scenarios (invalid API key, model not found, timeout)
- Verify token usage tracking

**Mocking Strategy:**
- Mock `Agent.run_async()` to return fake responses
- Mock HTTP requests to proxy endpoint for integration tests
- Use fixtures for sample Slack API payloads
- Use fixtures for agent responses with proper format

---

## Implementation Notes

### Dependencies

Add to `requirements.txt`:
```
openai-agents[litellm]>=0.1.0
```

This includes:
- `openai` - OpenAI client and Agents SDK
- `litellm` - LLM provider abstraction layer
- All required async/streaming dependencies

Already included:
- `slack-bolt` - Slack event handling

### File Structure

```
listeners/
├── events/
│   ├── __init__.py
│   ├── assistant_thread_started.py
│   ├── assistant_context_changed.py
│   └── assistant_user_message.py
└── _utils/
    └── agent_factory.py (creates agents with consistent config)

tests/
└── listeners/
    ├── events/
    │   ├── test_assistant_thread_started.py
    │   ├── test_assistant_context_changed.py
    │   └── test_assistant_user_message.py
    └── _utils/
        └── test_agent_factory.py
```

### Handler Signature Pattern

Handlers must be async to support agent execution:

```python
from slack_bolt.request import BoltRequest
from slack_bolt import Ack
import asyncio

async def assistant_user_message_handler(
    ack: Ack,
    body: dict[str, Any],
    client: WebClient,
    logger: logging.Logger
) -> None:
    ack()
    # Extract data
    thread_id = body["assistant_thread_id"]
    channel_id = body["channel_id"]
    user_message = body["text"]
    
    # Run agent asynchronously
    result = await agent.run_async(user_message)
    
    # Stream or save response
    client.assistant.threads.set_suggested_prompts(...)
```

### Integration Points

- Extends existing listener pattern (spec 002)
- Uses shared agent factory utility from `listeners/_utils`
- Requires manifest update (Slack app configuration)
- Connects to existing LiteLLM proxy at `https://litellm.sbp.ai/`
- No database required for MVP

### Special Considerations

- OpenAI Agents SDK handles async execution and streaming transparently
- LiteLLM provider routing handled by proxy, not by bot
- Agent maintains conversation state across multiple user messages
- Token usage tracked via agent result context
- All LLM requests proxied through `https://litellm.sbp.ai/`, reducing direct provider dependencies
- Implement per-user/channel rate limiting to prevent abuse
- Log all agent requests/responses for debugging (sanitize sensitive data)
- Integrate with existing logging setup in `app.py`
- Support graceful timeouts (60s for agent execution)

### Security Considerations

- Store `LITELLM_API_KEY` securely (environment variable or secrets manager)
- Never log API keys or full request bodies
- Validate user permissions before processing assistant events
- Rate limit by user/channel to prevent DoS
- Sanitize thread context before passing to agent (no sensitive internal data)

### Reference Specs

- [001-spec-based-development.md] - How to implement this spec
- [002-slack-listener-patterns.md] - Listener registration and handler conventions
- [000-shared-patterns.md] - Shared code templates
- OpenAI Agents: https://openai.github.io/openai-agents-python/
- LiteLLM Integration: https://openai.github.io/openai-agents-python/models/litellm/