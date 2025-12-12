# 002 - Slack Bolt Listener Patterns

**Purpose:** Define consistent patterns for adding listeners to this codebase.

---

## Directory layout

```
listeners/
├── __init__.py              # Orchestrates registration
├── actions/
│   ├── __init__.py
│   └── <handler>.py         # One handler per file
├── commands/
│   ├── __init__.py
│   └── <handler>.py
├── events/
│   ├── __init__.py
│   └── <handler>.py
├── messages/
│   ├── __init__.py
│   └── <handler>.py
├── shortcuts/
│   ├── __init__.py
│   └── <handler>.py
└── views/
    ├── __init__.py
    └── <handler>.py
```

---

## Registration pattern

Each category exposes `register(app: App)` in its `__init__.py`:

```python
# listeners/actions/__init__.py
from slack_bolt import App
from .approve_request import approve_request_handler

def register(app: App) -> None:
    app.action("approve_request")(approve_request_handler)
```

The orchestrator (`listeners/__init__.py`) imports and calls each:

```python
from slack_bolt import App
from . import actions, commands, events, messages, shortcuts, views

def register_all(app: App) -> None:
    actions.register(app)
    commands.register(app)
    events.register(app)
    messages.register(app)
    shortcuts.register(app)
    views.register(app)
```

**Key rule:** No registration at import time. Only when `register(app)` is called.

---

## Handler conventions

- **File naming:** `snake_case`, reflect purpose (e.g., `approve_request.py`)
- **Function naming:** `<name>_handler` (e.g., `approve_request_handler`)
- **One handler per file** to reduce merge conflicts
- **Type annotations:** Full typing required
- **No import-time side effects:** Keep handlers import-safe

Example handler:

```python
from typing import Any
from slack_bolt import Ack, App

def approve_request_handler(ack: Ack, body: dict[str, Any], logger) -> None:
    ack()
    logger.info("approved by %s", body.get("user"))
    # implementation here
```

---

## Adding a listener

1. Create file in appropriate category (e.g., `listeners/actions/approve_request.py`)
2. Implement handler with full type annotations
3. Update category `__init__.py` to import and register
4. Add tests in `tests/listeners/<category>/`
5. Run `pytest`, `flake8`, `black`
6. Commit with proper message and include `.beads/issues.jsonl`

---

## Testing

- Unit test handler logic separately from Slack Bolt binding
- Use fixtures for fake payloads
- Add smoke test: import category, create app, call `register(app)`, verify no exceptions
- Avoid networked tests

---

## Key constraints

- Import-safe: no network calls or environment dependencies at import time
- No helpers at module level; keep category `__init__.py` minimal
- For shared utilities, use `listeners/_utils.py` or `listeners/_types.py`
- Refer to [docs/spec/001-spec-based-development.md] for how to write specs
- Refer to [docs/spec/000-shared-patterns.md] for shared patterns