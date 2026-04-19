# Agent Instructions for lsimons-bot

> This file (`AGENTS.md`) is the canonical agent configuration. `CLAUDE.md` is a symlink to this file.

Python AI bot for Schuberg Philis Slack.

## Quick Reference

- **One-time**: `mise install` (also installs `fnox`)
- **Setup**: `mise run install` (or `uv sync --all-groups`)
- **Run**: `mise run run` (wraps `slack run` in `fnox exec`)
- **Blog publisher**: `mise run blog` (wraps `python -m lsimons_bot.blog` in `fnox exec`)
- **Format**: `mise run format` (or `uv run ruff format .`)
- **Lint**: `mise run lint` (ruff check + format --check)
- **Typecheck**: `mise run typecheck` (basedpyright lsimons_bot)
- **Test**: `mise run test` (or `uv run pytest`)
- **Full CI gate**: `mise run ci`

Secrets from 1Password (vault `AI`) are declared in `fnox.toml` and
injected at runtime by `fnox exec`. Non-secret config (and any secrets
not yet in 1Password) live in `.env`.

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

Work is NOT complete until CI passes on the pushed commit.

1. **Quality gates** (if code changed):
   ```bash
   mise run ci
   ```

2. **Push**:
   ```bash
   git pull --rebase && git push
   git status  # must show "up to date with origin"
   ```

3. **Verify CI**:
   ```bash
   mise run ci-watch
   ```
   On failure, inspect with `gh run view --log-failed`, fix, push, and re-watch.

Never stop before CI is green. If push or CI fails, resolve and retry.
