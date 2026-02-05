# 004 - Bot and LLM Layer

**Purpose:** Provide an abstraction layer for LLM-powered conversational responses, enabling testability and separation from Slack integration

**Requirements:**
- Bot abstraction defines conversation interface independent of transport
- LLM client wraps AsyncOpenAI SDK for LiteLLM proxy communication
- System prompt configures bot personality and constraints
- Error handling returns user-friendly messages on LLM failures

**Design Approach:**
- Base `Bot` class with `chat(messages)` as main interface
- `LLMBot` subclass injects `LLMClient` dependency
- `Bot.chat()` prepends system prompt, then delegates to `chat_completion()`
- `LLMClient` handles raw OpenAI SDK calls with error wrapping
- Type alias `Messages` uses OpenAI's `ChatCompletionMessageParam` for compatibility

**Implementation Notes:**

## Bot Class (`lsimons_bot/bot/bot.py`)

Base class provides:
- `chat(messages)` - Main entry point, prepends system prompt
- `chat_completion(messages)` - Abstract method, returns fallback response
- `loading_messages()` - Status messages for UI feedback
- `system_content()` - Bot personality and constraints

## LLMBot Class (`lsimons_bot/app/main.py`)

Concrete implementation:
- Accepts `LLMClient` in constructor
- Overrides `chat_completion()` to call LLM

## LLMClient (`lsimons_bot/llm/client.py`)

AsyncOpenAI wrapper:
- Configurable `base_url`, `api_key`, `model`
- `chat_completion(messages, temperature, max_tokens)` async method
- Returns error message string on exception (no throw to caller)

## Message Types

```python
Message: TypeAlias = ChatCompletionMessageParam
Messages: TypeAlias = Iterable[Message]
```

## System Prompt

Defines bot identity as "lsimons-bot", assistant to Leo Simons at Schuberg Philis. Key constraints:
- No access to Slack workspace data beyond current thread
- No external database/API access
- Must preserve Slack special syntax (`<@USER_ID>`, `<#CHANNEL_ID>`)
- Professional, friendly tone with limited emoji use
