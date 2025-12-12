# AGENTS.md - Instructions for AI Coding Agents

This document provides instructions for AI code-generation agents.

## Response Style

- Be concise in responses - avoid over-explaining changes.
- Focus on the specific task requested rather than extensive commentary.

## Project Overview

- Python AI bot for Schuberg Philis Slack.

## Project Structure

```
lsimons-bot/
├── TODO
└── [config files]        # Root-level configuration
```

## Development Standards

### Specs

- All significant changes need a spec.
- See [docs/spec/001-spec-based-development.md] for how to write specs.
- Common patterns are in [docs/spec/000-shared-patterns.md] to keep individual specs short.

### Code Quality Requirements

All code must meet these quality standards:

1. **Code Coverage**: Minimum 80% test coverage (branches, functions, lines, statements)
2. **flake8**: Zero warnings or errors
3. **black**: All code must be formatted
4. **Type Safety**: Full and strict Python typing

### Commit Message Convention

Follow [Conventional Commits](https://conventionalcommits.org/) with these types:

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code formatting (no logic changes)
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `build`: Build system changes
- `ci`: CI configuration changes
- `perf`: Performance improvements
- `revert`: Reverting commits
- `improvement`: General code improvements
- `chore`: Maintenance tasks

**Format**: `type(scope): description`
**Example**: `feat(core-model): add new validation rules`

## Development process - building and testing

### Process

Always follow this development process:

1. Make sure the git working directory is clean
2. Create a new git branch
3. For a significant change like a new feature, create a spec doc
4. Ask for human review of the spec
5. Only if the human confirms, implement the spec
6. Create tests for the new functionality
7. Run tests, linting, and formatting
8. Commit changes with a proper commit message
9. Do *not* try to handle git branch, push, or pull requests, ask the human

### Initial Setup

```zsh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
slack run
```

### Testing

Run pytest from root directory for unit testing:

```zsh
pytest .
```

### Linting

Run flake8 from root directory for linting:

```zsh
flake8 *.py && flake8 listeners/
```

### Formatting

Run black from root directory for code formatting:

```zsh
black .
```

## Environment and Dependencies

### Required Tools

- **Python**: LTS version
- **uv**: Latest stable version
- **Docker**: For dependent services
- **Slack Apps SDK**: Latest stable version
