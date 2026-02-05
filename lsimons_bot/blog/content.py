import logging
from dataclasses import dataclass

from lsimons_bot.blog.github import CommitStats
from lsimons_bot.llm.client import LLMClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a friendly AI bot named lsimons-bot. You write engaging blog posts
about your coding activities. Keep the tone conversational and technical but accessible.
Write in first person as the bot."""

POST_PROMPT_TEMPLATE = """Write a blog post summarizing my recent coding work.

Here are my commits from the past few days:

{commits_summary}

Requirements:
- Title should be catchy and reflect the main work done
- Content should be 2-4 paragraphs
- Include specific details about what was built or fixed
- Keep it engaging and somewhat informal
- Use HTML formatting (no markdown)

Respond with exactly this format:
TITLE: <your title here>
CONTENT: <your HTML content here>"""


@dataclass
class BlogContent:
    title: str
    content: str


def _format_commits(stats: CommitStats) -> str:
    lines: list[str] = []
    for commit in stats.commits[:20]:
        lines.append(f"- [{commit.repo_name}] {commit.message} (+{commit.additions}/-{commit.deletions})")
    return "\n".join(lines)


async def generate_blog_post(llm: LLMClient, stats: CommitStats) -> BlogContent:
    logger.info("Generating blog post from %d commits", stats.total_commits)

    commits_summary = _format_commits(stats)
    prompt = POST_PROMPT_TEMPLATE.format(commits_summary=commits_summary)

    response = await llm.chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
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
