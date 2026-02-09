# Agent Instructions for lsimons-bot

Python AI bot for Schuberg Philis Slack.

## Quick Reference

- **Setup**: `uv sync --all-groups`
- **Run**: `slack run`
- **Format**: `uv run ruff format .`
- **Lint**: `uv run ruff check . && uv run basedpyright lsimons_bot`
- **Test**: `uv run pytest`

## Structure

```
lsimons_bot/
├── app/           # Core (main.py, config.py)
└── slack/         # Integration layer
    ├── assistant/ # AI assistant handlers
    ├── home/      # Home tab handlers
    └── messages/  # Message event handlers
```

**Key patterns:**
- `app/` depends on `slack/` (registers handlers); `slack/` has NO dependency on `app/`
- Slack modules have `__init__.py` with `register(app)` function
- One handler per file
- Tests mirror source structure exactly

## Guidelines

**Code quality requirements:**
- ruff formatting
- ruff: zero warnings
- basedpyright: zero errors
- Full type annotations
- Minimum 80% test coverage

**Coding style:**
- Small files (<300 lines, most <25 lines)
- No docstrings on test methods
- Minimal mocking (only external dependencies)
- No over-engineering

**Specs:** All significant changes need a spec. See `docs/spec/`.

## Commit Message Convention

Follow [Conventional Commits](https://conventionalcommits.org/):

**Format:** `type(scope): description`

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation
- `style`: Formatting (no logic changes)
- `refactor`: Code restructuring
- `test`: Test changes
- `build`: Build system
- `ci`: CI configuration
- `perf`: Performance
- `revert`: Reverting commits
- `improvement`: General improvements
- `chore`: Maintenance

## Session Completion

Work is NOT complete until `git push` succeeds.

1. **Quality gates** (if code changed):
   ```bash
   uv run ruff format --check . && uv run ruff check .
   uv run basedpyright lsimons_bot
   uv run pytest
   ```

2. **Push**:
   ```bash
   git pull --rebase && git push
   git status  # must show "up to date with origin"
   ```

Never stop before pushing. If push fails, resolve and retry.
