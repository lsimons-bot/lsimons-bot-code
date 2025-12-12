# Slack Bot that automates part of Leo Simons' (lsimons) work at Schuberg Philis

This is a Python AI bot for Schuberg Philis Slack workspace, providing AI assistant capabilities integrated with Slack's Assistant API and LiteLLM proxy for LLM access.

## Table of Contents

- [Overview](#overview)
- [AI Assistant Feature](#ai-assistant-feature)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

## Overview

This bot provides automation and AI assistance features for the Slack workspace. The main feature is the **AI Assistant**, which allows users to interact with an AI assistant directly in Slack channels using a split-view thread interface.

## AI Assistant Feature

### What is the AI Assistant?

The AI Assistant enables users to:
- Open AI threads in Slack channels with a split-view UI
- Chat with an AI assistant that understands channel context
- Receive suggested prompts to guide interactions
- Provide feedback on responses (thumbs up/down)

The assistant uses the **Slack Assistant API** and integrates with **LiteLLM proxy** to access 100+ LLM providers through a unified interface.

### Key Capabilities

- **Channel Context Awareness**: Assistant understands the channel topic and message history
- **Real-time Streaming**: Responses stream in real-time for better UX
- **Thread Context**: Assistant maintains conversation history within a thread
- **Suggested Prompts**: Channel-specific prompt suggestions guide user interactions
- **Feedback Tracking**: Users can provide feedback on responses for continuous improvement
- **Multi-Provider Support**: Access any LLM supported by LiteLLM (OpenAI, Anthropic, etc.)

## Quick Start

### Prerequisites

- **Slack Workspace**: Slack Enterprise Grid or Pro plan (AI Assistant API requires paid plan)
- **Slack App**: The app must have AI Assistant API enabled in workspace settings
- **LiteLLM Proxy**: Access to a running LiteLLM proxy instance
- **Python 3.10+**: LTS version recommended
- **uv**: UV package manager (latest stable)

### Setup Steps

1. **Enable AI Assistant in Slack Workspace**
   - Go to your Slack workspace settings
   - Navigate to App Management → Custom Apps
   - For this bot, enable "AI Assistant API" (requires paid plan)
   - Ensure the app has scopes: `assistant:write`, `assistant:read`, `channels:history`, `chat:write`

2. **Install Dependencies**
   ```bash
   cd lsimons-bot
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file or set environment variables:
   ```bash
   # LiteLLM Proxy Configuration
   LITELLM_PROXY_URL=https://litellm.sbp.ai/
   LITELLM_API_KEY=your-litellm-api-key
   
   # LLM Model Configuration
   ASSISTANT_MODEL=openai/gpt-4              # Format: provider/model-name
   
   # Optional: Custom System Prompt
   ASSISTANT_SYSTEM_PROMPT="You are a helpful assistant in Slack..."
   ```

4. **Run the Bot**
   ```bash
   slack run
   ```

   The bot will connect to Slack via Socket Mode and start listening for assistant events.

### LiteLLM Proxy Configuration

The bot expects a LiteLLM proxy running at the URL specified in `LITELLM_PROXY_URL`.

**Proxy Endpoint Configuration:**
```
Base URL: https://litellm.sbp.ai/
Authentication: API key in `Authorization: Bearer {LITELLM_API_KEY}` header
Models: Any model supported by LiteLLM (openai/gpt-4, anthropic/claude-3-sonnet, etc.)
```

**Example LiteLLM Proxy Setup (on your server):**
```bash
litellm --model openai/gpt-4 \
  --api_key sk-your-openai-key \
  --port 8000
```

Then point `LITELLM_PROXY_URL` to your proxy endpoint.

## Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `LITELLM_PROXY_URL` | Yes | Base URL of LiteLLM proxy | `https://litellm.sbp.ai/` |
| `LITELLM_API_KEY` | Yes | API key for proxy authentication | (your API key) |
| `ASSISTANT_MODEL` | No | LLM model to use | `openai/gpt-4` |
| `ASSISTANT_SYSTEM_PROMPT` | No | Custom system prompt | `You are helpful...` |

### Slack App Manifest Configuration

The `manifest.json` file configures your Slack app. Ensure the following scopes are enabled:

```json
{
  "oauth_scopes": [
    "assistant:write",
    "assistant:read",
    "channels:history",
    "chat:write"
  ],
  "socket_mode_enabled": true,
  "socket_mode_request_all_events": false
}
```

Event subscriptions should include:
- `assistant_thread_started`
- `assistant_context_changed`
- `assistant_user_message`

## Troubleshooting

### AI Assistant not appearing in channels

**Issue**: Users don't see the AI Assistant option in their channels.

**Solutions**:
1. Verify the Slack workspace has a paid plan (AI Assistant API requires Enterprise Grid or Pro)
2. Check that the app has `assistant:write` and `assistant:read` scopes in workspace settings
3. Verify the app is installed in the channel (not just the workspace)
4. Restart the bot: `slack run`

### "AI assistant unavailable" error

**Issue**: Users get an error message when trying to use the assistant.

**Solutions**:
1. Verify `LITELLM_API_KEY` is set correctly: `echo $LITELLM_API_KEY`
2. Test proxy connectivity: `curl -H "Authorization: Bearer $LITELLM_API_KEY" $LITELLM_PROXY_URL/models`
3. Check bot logs for detailed error messages: `logs` or `journalctl` depending on deployment
4. Verify the model exists on the proxy: `curl $LITELLM_PROXY_URL/models`

### "Configuration error" messages

**Issue**: Users see "Configuration error. Please check settings."

**Solutions**:
1. Verify `ASSISTANT_MODEL` is set and formatted correctly (e.g., `openai/gpt-4`)
2. Verify the model is available on your LiteLLM proxy
3. Check proxy logs for model availability and routing issues
4. Verify all required environment variables are set

### Slow or no response from assistant

**Issue**: Assistant takes too long to respond or doesn't respond at all.

**Solutions**:
1. Check network connectivity to LiteLLM proxy
2. Check proxy logs for rate limiting or timeout errors
3. Verify model availability and load on proxy
4. Increase timeout if model is consistently slow (default is 60 seconds)
5. Check Slack rate limiting: bot may be rate limited by Slack API

### Empty or truncated responses

**Issue**: Assistant responses are empty or incomplete.

**Solutions**:
1. Check proxy logs for streaming errors
2. Verify response format is correct (should be plain text)
3. Check bot logs for response handling errors
4. Verify LLM model supports streaming (all standard models do)

## Development

See [AGENTS.md] for development guidelines, including:
- Project structure and organization
- Testing and code quality standards
- Git workflow and commit conventions
- Issue tracking with `bd` (beads)

### Running Tests

```bash
# Run all tests
uv run pytest .

# Run with coverage
uv run pytest . --cov=lsimons_bot

# Run linting
uv run flake8 lsimons_bot tests
basedpyright lsimons_bot

# Format code
uv run black .
```

## Documentation

See [docs] for additional documentation:
- [docs/spec/000-shared-patterns.md] - Common code patterns
- [docs/spec/001-spec-based-development.md] - How to write and implement specs
- [docs/spec/002-slack-listener-patterns.md] - Slack listener conventions
- [docs/spec/003-ai-assistant-integration.md] - AI Assistant architecture and integration details

## License

See [LICENSE.md] for license information. The original Slack template is MIT licensed, while new code is private.

See [SLACK_README.md] for the original Slack template setup instructions.

[docs]: ./docs
[docs/spec]: ./docs/spec
[docs/spec/000-shared-patterns.md]: ./docs/spec/000-shared-patterns.md
[docs/spec/001-spec-based-development.md]: ./docs/spec/001-spec-based-development.md
[docs/spec/002-slack-listener-patterns.md]: ./docs/spec/002-slack-listener-patterns.md
[docs/spec/003-ai-assistant-integration.md]: ./docs/spec/003-ai-assistant-integration.md
[AGENTS.md]: ./AGENTS.md
[LICENSE.md]: ./LICENSE.md
[SLACK_README.md]: ./SLACK_README.md
```

Now let me commit this update: