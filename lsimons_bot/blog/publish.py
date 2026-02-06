import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from lsimons_bot.blog.config import get_env_vars
from lsimons_bot.blog.content import generate_blog_post
from lsimons_bot.blog.github import CommitStats, GitHubClient
from lsimons_bot.blog.wordpress import BlogPost, WordPressClient
from lsimons_llm import load_config
from lsimons_llm.async_client import AsyncLLMClient

logger = logging.getLogger(__name__)

HOURS_THRESHOLD = 24


@dataclass
class PublishResult:
    should_publish: bool
    reason: str
    post: BlogPost | None = None
    stats: CommitStats | None = None


async def check_and_publish(dry_run: bool = False) -> PublishResult:
    env = get_env_vars()

    wp = WordPressClient(
        username=env["WORDPRESS_USERNAME"],
        app_password=env["WORDPRESS_APPLICATION_PASSWORD"],
        client_id=env["WORDPRESS_CLIENT_ID"],
        client_secret=env["WORDPRESS_CLIENT_SECRET"],
        site_id=env["WORDPRESS_SITE_ID"],
    )

    latest_post = wp.get_latest_post()
    now = datetime.now(timezone.utc)

    if latest_post:
        hours_since = (now - latest_post.date).total_seconds() / 3600
        if hours_since < HOURS_THRESHOLD:
            return PublishResult(
                should_publish=False,
                reason=f"Last post was {hours_since:.1f} hours ago (threshold: {HOURS_THRESHOLD}h)",
            )
        since_date = latest_post.date
    else:
        since_date = now - timedelta(days=7)

    gh = GitHubClient(token=env["GITHUB_TOKEN"])
    stats = gh.get_commits_since(since_date)

    if not stats.is_significant():
        return PublishResult(
            should_publish=False,
            reason=f"Not enough activity: {stats.total_commits} commits, max {stats.max_lines_in_commit} lines",
            stats=stats,
        )

    if dry_run:
        return PublishResult(
            should_publish=True,
            reason=f"Would publish: {stats.total_commits} commits, max {stats.max_lines_in_commit} lines",
            stats=stats,
        )

    config = load_config(
        base_url=env["LLM_BASE_URL"],
        api_key=env["LLM_AUTH_TOKEN"],
        model=env["LLM_DEFAULT_MODEL"],
    )
    llm = AsyncLLMClient(config)

    blog_content = await generate_blog_post(llm, stats)
    post = wp.create_post(title=blog_content.title, content=blog_content.content)

    return PublishResult(
        should_publish=True,
        reason=f"Published: {post.title}",
        post=post,
        stats=stats,
    )
