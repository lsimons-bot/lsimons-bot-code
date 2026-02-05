# 003 - Blog Module

**Purpose:** Automatically generate and publish blog posts summarizing lsimons-bot's recent GitHub activity

**Requirements:**
- Check WordPress.com for last blog post date
- If >48 hours since last post, fetch GitHub commits by lsimons-bot
- If significant work (>5 commits OR any commit >200 lines), generate blog post via LLM
- Publish to WordPress.com
- CLI invocable: `python -m lsimons_bot.blog` with `--dry-run` option

**Design Approach:**
- New `lsimons_bot/blog/` submodule following existing module patterns
- Use `requests` for WordPress.com REST API (OAuth2 bearer token)
- Use `PyGithub` for GitHub API
- Reuse existing `lsimons_bot.llm.client.LLMClient` for content generation
- Environment variables: `WORDPRESS_ACCESS_TOKEN`, `WORDPRESS_SITE_ID`, `GITHUB_TOKEN`

**Implementation Notes:**
- WordPress.com API: `GET/POST https://public-api.wordpress.com/wp/v2/sites/{site_id}/posts`
- GitHub: Get commits across all public repos for `lsimons-bot` user
- Commit size calculated via stats (additions + deletions)
- Config pattern matches `lsimons_bot/app/config.py`
