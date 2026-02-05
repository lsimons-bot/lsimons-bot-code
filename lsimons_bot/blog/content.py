import logging
from dataclasses import dataclass

from lsimons_bot.blog.github import CommitStats
from lsimons_llm.async_client import AsyncLLMClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are lsimons-bot, an AI coding assistant that writes blog posts about your work.

Your voice:
- Casual and direct, like a developer chatting with friends
- Self-aware that you're a bot (you can be playful about it)
- Technical but not jargon-heavy
- Honest about problems you hit and how you solved them

Write in first person. Keep it real."""

POST_PROMPT_TEMPLATE = """Write a short blog post about my recent coding work.

Commits:
{commits_summary}

Guidelines:
- 2-3 short paragraphs max
- Tell a story: what problem came up, what you tried, how you fixed it
- Be specific - mention actual error messages, file names, or APIs when relevant
- Skip the corporate speak ("leveraging", "ecosystem", "core components")
- It's OK to be a bit self-deprecating when things went wrong
- Use HTML formatting (no markdown)

Format your response exactly as:
TITLE: <short punchy title>
CONTENT: <your HTML content>"""


@dataclass
class BlogContent:
    title: str
    content: str


def _format_commits(stats: CommitStats) -> str:
    lines: list[str] = []
    for commit in stats.commits[:20]:
        lines.append(f"- [{commit.repo_name}] {commit.message} (+{commit.additions}/-{commit.deletions})")
    return "\n".join(lines)


async def generate_blog_post(llm: AsyncLLMClient, stats: CommitStats) -> BlogContent:
    logger.info("Generating blog post from %d commits", stats.total_commits)

    commits_summary = _format_commits(stats)
    prompt = POST_PROMPT_TEMPLATE.format(commits_summary=commits_summary)

    response = await llm.chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    title = "Weekly Update"
    content = response

    if "TITLE:" in response and "CONTENT:" in response:
        parts = response.split("CONTENT:", 1)
        title_part = parts[0].replace("TITLE:", "").strip()
        content_part = parts[1].strip() if len(parts) > 1 else ""
        if title_part:
            title = title_part
        if content_part:
            content = content_part

    return BlogContent(title=title, content=content)
