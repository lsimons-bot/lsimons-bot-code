# AI Assistant Feature - READ ME FIRST

**Status:** ✅ Planning Complete & Ready for Implementation  
**Epic ID:** `lsimons-bot-czw`  
**Created:** 2025-12-12  
**Total Issues:** 11 beads issues across 5 phases  
**Estimated Effort:** 12-17 hours

---

## What Was Done

I've created a comprehensive plan for adding an **AI assistant feature** to your Slack bot. The assistant will:

- ✅ Run in Slack's split-view thread UI (Agents & AI Apps feature)
- ✅ Use your **LiteLLM API proxy** at `https://litellm.sbp.ai/` instead of direct OpenAI calls
- ✅ Stream responses in real-time for better UX
- ✅ Maintain conversation context across channel switches
- ✅ Support user feedback (thumbs up/down) for response quality
- ✅ Include suggested prompts to help users get started

## Planning Documents

All in `history/`:

1. **`AI_ASSISTANT_PLAN.md`** - Comprehensive architecture overview
2. **`AI_ASSISTANT_ISSUES_SUMMARY.md`** - Full description of all 11 beads issues
3. **`AI_ASSISTANT_QUICK_REF.md`** - Quick reference for developers

## Beads Issues Created

All work tracked as 11 beads issues:

| Phase | Issues | IDs |
|-------|--------|-----|
| 1 | Specification (BLOCKER) | dyz |
| 2 | Infrastructure | ocl, u01 |
| 3 | Core Listeners | c6r, 7gl, urs, oaw |
| 4 | Enhancements | ad5 |
| 5 | Polish & Docs | 852, cqi, cyf |

## Key Architecture Decisions

### Why LiteLLM?
- Centralized LLM management (one URL, one API key)
- Can swap models without code changes
- Cost tracking and rate limiting at proxy level

### Why Slack Assistant Class?
- Purpose-built for AI apps in Slack
- Handles thread state automatically
- Split-view UI included
- Streaming support baked in

### Module Structure
```
listeners/
├── _llm.py                    # LiteLLM wrapper
├── _assistant_utils.py        # Context + history helpers
├── _prompt.py                 # System prompts + engineering
├── events/
│   ├── assistant_thread_started.py
│   └── assistant_user_message.py
└── actions/
    └── assistant_feedback.py
```

## Next Steps

1. **Review planning documents** in `history/`
2. **Use bd to track work:** `bd ready --json` shows what's available
3. **Start with Phase 1 (Spec):** `bd update lsimons-bot-dyz --status in_progress`
4. **Follow phases in dependency order** - bd will block work until prerequisites are done

## Quick Commands

```bash
# See what's ready to work on
bd ready --json

# View an issue with dependencies
bd show lsimons-bot-dyz

# Start work on an issue
bd update lsimons-bot-dyz --status in_progress

# Close an issue (unblocks dependents)
bd close lsimons-bot-dyz --reason "Spec complete and approved"

# Check dependencies
bd dep tree lsimons-bot-czw
```

## Development Process

Follow the standard workflow in AGENTS.md:
1. Check ready work: `bd ready --json`
2. Claim issue: `bd update <id> --status in_progress`
3. Implement, test, format, lint
4. Close issue: `bd close <id> --reason "..."`
5. Always commit `.beads/issues.jsonl` with code changes

## Success Criteria

When complete, you'll have:
- ✅ Users can open AI assistant threads in Slack
- ✅ Assistant responds via LiteLLM proxy
- ✅ Responses stream in real-time
- ✅ Thread context persists
- ✅ Users can rate responses
- ✅ 80%+ test coverage
- ✅ Zero flake8/black violations
- ✅ Full type annotations

---

**Status:** ✅ Dependencies configured, ready for execution
**Next Action:** Review planning docs and start Phase 1 (Spec)