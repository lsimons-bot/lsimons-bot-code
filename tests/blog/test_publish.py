from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from lsimons_bot.blog.github import CommitStats
from lsimons_bot.blog.publish import PublishResult, check_and_publish
from lsimons_bot.blog.wordpress import BlogPost


class TestPublishResult:
    def test_dataclass(self) -> None:
        result = PublishResult(should_publish=True, reason="Test reason")
        assert result.should_publish is True
        assert result.reason == "Test reason"
        assert result.post is None


class TestCheckAndPublish:
    @pytest.fixture
    def mock_env(self) -> dict[str, str]:
        return {
            "WORDPRESS_USERNAME": "wp-user",
            "WORDPRESS_APPLICATION_PASSWORD": "wp-app-pass",
            "WORDPRESS_CLIENT_ID": "123",
            "WORDPRESS_CLIENT_SECRET": "secret",
            "WORDPRESS_SITE_ID": "site123",
            "GITHUB_TOKEN": "gh-token",
            "LLM_BASE_URL": "http://localhost:8000",
            "LLM_AUTH_TOKEN": "llm-key",
            "LLM_DEFAULT_MODEL": "gpt-4",
        }

    @pytest.mark.asyncio
    async def test_recent_post_skips(self, mock_env: dict[str, str]) -> None:
        recent_post = BlogPost(
            id=1,
            title="Recent",
            date=datetime.now(timezone.utc) - timedelta(hours=12),
            link="https://example.com",
        )

        with (
            patch("lsimons_bot.blog.publish.get_env_vars", return_value=mock_env),
            patch("lsimons_bot.blog.publish.WordPressClient") as mock_wp_class,
        ):
            mock_wp = MagicMock()
            mock_wp.get_latest_post.return_value = recent_post
            mock_wp_class.return_value = mock_wp

            result = await check_and_publish()

        assert result.should_publish is False
        assert "12.0 hours ago" in result.reason

    @pytest.mark.asyncio
    async def test_not_significant_skips(self, mock_env: dict[str, str]) -> None:
        old_post = BlogPost(
            id=1,
            title="Old",
            date=datetime.now(timezone.utc) - timedelta(hours=72),
            link="https://example.com",
        )
        stats = CommitStats(commits=[], total_commits=2, max_lines_in_commit=50)

        with (
            patch("lsimons_bot.blog.publish.get_env_vars", return_value=mock_env),
            patch("lsimons_bot.blog.publish.WordPressClient") as mock_wp_class,
            patch("lsimons_bot.blog.publish.GitHubClient") as mock_gh_class,
        ):
            mock_wp = MagicMock()
            mock_wp.get_latest_post.return_value = old_post
            mock_wp_class.return_value = mock_wp

            mock_gh = MagicMock()
            mock_gh.get_commits_since.return_value = stats
            mock_gh_class.return_value = mock_gh

            result = await check_and_publish()

        assert result.should_publish is False
        assert "Not enough activity" in result.reason

    @pytest.mark.asyncio
    async def test_dry_run_returns_early(self, mock_env: dict[str, str]) -> None:
        old_post = BlogPost(
            id=1,
            title="Old",
            date=datetime.now(timezone.utc) - timedelta(hours=72),
            link="https://example.com",
        )
        stats = CommitStats(commits=[], total_commits=10, max_lines_in_commit=300)

        with (
            patch("lsimons_bot.blog.publish.get_env_vars", return_value=mock_env),
            patch("lsimons_bot.blog.publish.WordPressClient") as mock_wp_class,
            patch("lsimons_bot.blog.publish.GitHubClient") as mock_gh_class,
        ):
            mock_wp = MagicMock()
            mock_wp.get_latest_post.return_value = old_post
            mock_wp_class.return_value = mock_wp

            mock_gh = MagicMock()
            mock_gh.get_commits_since.return_value = stats
            mock_gh_class.return_value = mock_gh

            result = await check_and_publish(dry_run=True)

        assert result.should_publish is True
        assert "Would publish" in result.reason
        assert result.post is None
