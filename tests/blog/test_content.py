from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from lsimons_bot.blog.content import BlogContent, generate_blog_post
from lsimons_bot.blog.github import CommitInfo, CommitStats


class TestBlogContent:
    def test_dataclass(self) -> None:
        content = BlogContent(title="Test Title", content="<p>Test</p>")
        assert content.title == "Test Title"
        assert content.content == "<p>Test</p>"


class TestGenerateBlogPost:
    @pytest.fixture
    def commit_stats(self) -> CommitStats:
        return CommitStats(
            commits=[
                CommitInfo(
                    repo_name="test-repo",
                    sha="abc1234",
                    message="Add feature",
                    date=datetime.now(UTC),
                    additions=100,
                    deletions=20,
                )
            ],
            total_commits=1,
            max_lines_in_commit=120,
        )

    @pytest.mark.asyncio
    async def test_generate_blog_post(self, commit_stats: CommitStats) -> None:
        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(
            return_value="TITLE: My Blog Post\nCONTENT: <p>This is the content.</p>"
        )

        result = await generate_blog_post(mock_llm, commit_stats)

        assert result.title == "My Blog Post"
        assert result.content == "<p>This is the content.</p>"

    @pytest.mark.asyncio
    async def test_generate_blog_post_fallback(self, commit_stats: CommitStats) -> None:
        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(return_value="Some unparseable response")

        result = await generate_blog_post(mock_llm, commit_stats)

        assert result.title == "Weekly Update"
        assert result.content == "Some unparseable response"
