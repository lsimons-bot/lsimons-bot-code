# 005 - Application Bootstrap

**Purpose:** Wire together all application components and start the Slack bot in socket mode

**Requirements:**
- Validate required environment variables at startup
- Initialize LLM client with configured model and credentials
- Create bot instance with LLM dependency
- Register all Slack handlers with the app
- Start socket mode handler for real-time events

**Design Approach:**
- Single `main()` async function in `lsimons_bot/app/main.py`
- Environment validation via `config.py` (fail-fast on missing vars)
- Explicit dependency construction (no DI framework)
- Handler registration via module-level `register(app)` functions
- Socket mode for firewall-friendly WebSocket connection

**Implementation Notes:**

## Entry Point (`app.py`)

```python
import asyncio
from lsimons_bot.app.main import main
asyncio.run(main())
```

## Bootstrap Sequence (`lsimons_bot/app/main.py`)

1. `get_env_vars()` validates and returns all required environment variables
2. Construct `LLMClient` with LiteLLM proxy credentials
3. Construct `LLMBot` with client dependency
4. Create `AsyncApp` with Slack bot token
5. Register handlers: `assistant.register(app, bot)`, `messages.register(app)`, `home.register(app)`
6. Create `AsyncSocketModeHandler` with app token
7. `await handler.start_async()` (blocks until shutdown)

## Configuration (`lsimons_bot/app/config.py`)

Required environment variables:
- `SLACK_BOT_TOKEN` - Bot OAuth token
- `SLACK_APP_TOKEN` - App-level token for socket mode (starts with `xapp-`)
- `LITELLM_API_BASE` - LiteLLM proxy URL
- `LITELLM_API_KEY` - LiteLLM API key
- `ASSISTANT_MODEL` - Model name for chat completions

Pattern: `validate_env_vars(required_vars)` returns dict or raises on missing vars.

## Handler Registration

Each Slack module exposes `register(app)` function:
- `assistant`: Requires `bot` parameter for AI responses
- `messages`: General message handling
- `home`: App home tab events
