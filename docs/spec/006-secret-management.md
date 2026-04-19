# 006 - Secret Management via fnox

**Purpose:** Resolve 1Password-backed secrets at runtime via `fnox` rather
than relying on a shell-wide 1Password integration populating the caller's
environment.

**Requirements:**
- Secrets stored in 1Password (vault `AI`) are injected into the process
  environment only when the bot or blog publisher actually runs
- Non-secret config (and any secrets not yet in 1Password) continues to
  load from `.env` via `mise`'s `_.file` directive
- CI-relevant tasks (`lint`, `typecheck`, `test`) run without any
  1Password access — tests mock the env vars they need
- `fnox` is pinned as a project tool in `.mise.toml` so `mise install`
  produces a usable checkout

**Design Approach:**
- `fnox.toml` declares a single `[providers.op]` (type `1password`,
  default vault `AI`) and lists each secret as an op:// reference
- Runtime tasks wrap the underlying command in `fnox exec --` so
  secrets land in the subprocess environment and nowhere else
- `.env.example` documents the split between fnox-managed secrets and
  `.env`-managed config

**Implementation Notes:**

## Secrets currently migrated

| Env var | 1Password reference |
|---|---|
| `LLM_AUTH_TOKEN` | `op://AI/LLM_AUTH_TOKEN/password` |
| `WORDPRESS_CLIENT_SECRET` | `op://AI/WORDPRESS_CLIENT_SECRET/password` |
| `WORDPRESS_APPLICATION_PASSWORD` | `op://AI/WORDPRESS_APPLICATION_PASSWORD/password` |
| `GITHUB_WORDPRESS_TOKEN` | `op://AI/GITHUB_TOKEN/password` |

Slack tokens (`SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`) and the LiteLLM key
(`LITELLM_API_KEY`) are not yet in 1Password — they stay in `.env`. To
migrate one, add a 1Password item and a matching entry under `[secrets]`
in `fnox.toml`.

## Task wiring (`.mise.toml`)

- `mise run run` → `fnox exec -- slack run`
- `mise run blog` → `fnox exec -- uv run python -m lsimons_bot.blog`

Tasks that don't need secrets (`install`, `lint`, `format`, `typecheck`,
`test`, `ci`) run plain `uv` commands — no fnox wrapper, no 1Password
interaction.

## Prerequisites

- `op` signed in (session or biometric unlock) so the 1Password provider
  can fetch references
- `mise install` installs `fnox` from its mise registry entry
  (prebuilt GitHub release binary — no cargo compile)
