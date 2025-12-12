# AI Assistant Feature - Quick Reference

**Epic:** `lsimons-bot-czw`

## Beads Issues by Phase

| Phase | Issue ID | Title |
|-------|----------|-------|
| 1 | dyz | Spec: AI Assistant Integration with LiteLLM |
| 2 | ocl | Implement LiteLLM integration module |
| 2 | u01 | Configure Slack app for Assistant feature |
| 3 | c6r | Implement Assistant thread_started listener |
| 3 | 7gl | Implement Assistant user_message listener |
| 3 | urs | Implement Assistant feedback action handler |
| 3 | oaw | Implement thread context utilities |
| 4 | ad5 | Implement prompt engineering module |
| 5 | 852 | Comprehensive test suite (80%+ coverage) |
| 5 | cqi | Documentation: AI Assistant architecture spec |
| 5 | cyf | Update README and setup instructions |

## Files to Create

```
listeners/
├── _llm.py                           # LiteLLM wrapper
├── _assistant_utils.py               # Context + history helpers
├── _prompt.py                        # System prompts + suggested prompts
├── events/
│   ├── assistant_thread_started.py
│   ├── assistant_user_message.py
│   └── assistant_context_changed.py
└── actions/
    └── assistant_feedback.py

docs/spec/
└── 003-ai-assistant-architecture.md

tests/listeners/
├── events/test_assistant_*.py
├── actions/test_assistant_feedback.py
├── test_llm.py
├── test_assistant_utils.py
└── test_prompt.py
```

## Required Configuration

### Environment Variables
```
LITELLM_API_KEY=sk-...
LITELLM_API_BASE=https://litellm.sbp.ai/
LITELLM_MODEL=gpt-4o-mini
```

### Slack App Settings
- Enable: Agents & AI Apps
- Scopes: assistant:write, chat:write, im:history
- Events: assistant_thread_started, assistant_thread_context_changed, message.im

### app.py Change
```python
from slack_bolt.app.app import Assistant

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    ignoring_self_assistant_message_enabled=False,
)

assistant = Assistant()
app.use(assistant)
```

## Slack API Patterns

### thread_started Event
```python
@assistant.thread_started
def handle_thread_started(say, get_thread_context, set_suggested_prompts):
    say("Welcome message")
    set_suggested_prompts(prompts=[...])
```

### user_message Event
```python
@assistant.user_message
def handle_user_message(client, context, get_thread_context, payload, say, set_status):
    set_status("thinking...")
    # Get history, call LLM, stream response
    streamer = client.chat_stream(channel=..., thread_ts=...)
    for chunk in llm_response:
        streamer.append(markdown_text=chunk)
    streamer.stop(blocks=feedback_blocks)
```

### Feedback Action
```python
@app.action("feedback")
def handle_feedback(ack, body, client):
    ack()
    feedback_type = body["actions"][0]["value"]
    client.chat_postEphemeral(channel=..., text="...")
```

## LiteLLM Integration

```python
# listeners/_llm.py
import openai

def get_llm_client():
    return openai.OpenAI(
        api_key=os.getenv("LITELLM_API_KEY"),
        base_url=os.getenv("LITELLM_API_BASE")
    )

def stream_llm_response(messages, system_prompt):
    client = get_llm_client()
    response = client.chat.completions.create(
        model=os.getenv("LITELLM_MODEL"),
        messages=[{"role": "system", "content": system_prompt}] + messages,
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

## Common Patterns

### Get Conversation History
```python
def get_conversation_history(client, channel_id, thread_ts):
    replies = client.conversations_replies(
        channel=channel_id,
        ts=thread_ts,
        limit=10
    )
    messages = []
    for msg in replies["messages"]:
        role = "user" if msg.get("bot_id") is None else "assistant"
        messages.append({"role": role, "content": msg["text"]})
    return messages
```

### Set Loading Status
```python
set_status(
    status="thinking...",
    loading_messages=[
        "Consulting the AI...",
        "Processing your request...",
        "Generating response...",
    ]
)
```

### Create Feedback Block
```python
def create_feedback_blocks():
    from slack_sdk.models.blocks import ContextActionsBlock, FeedbackButtonsElement, FeedbackButtonObject
    
    return [
        ContextActionsBlock(
            elements=[
                FeedbackButtonsElement(
                    action_id="feedback",
                    positive_button=FeedbackButtonObject(
                        text="Good Response",
                        value="good-feedback",
                    ),
                    negative_button=FeedbackButtonObject(
                        text="Bad Response",
                        value="bad-feedback",
                    ),
                )
            ]
        )
    ]
```

## Useful References

- **Slack API:** https://docs.slack.dev/tools/bolt-python/concepts/ai-apps/
- **Project Patterns:** `docs/spec/002-slack-listener-patterns.md`
- **Planning Docs:** Check `history/AI_ASSISTANT_PLAN.md` and `history/AI_ASSISTANT_ISSUES_SUMMARY.md`
- **Development:** See `AGENTS.md` for testing, linting, formatting, and commit standards

## Workflow

1. `bd ready --json` - See what's available
2. `bd update <id> --status in_progress` - Claim work
3. Implement following project patterns
4. `pytest .` and `flake8 *.py listeners/` and `black .` (per AGENTS.md)
5. `bd close <id> --reason "..."` - Mark done
6. Commit with `.beads/issues.jsonl` included