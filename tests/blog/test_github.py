from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from lsimons_bot.blog.github import CommitInfo, CommitStats, GitHubClient


class TestCommitInfo:
    def test_total_lines(self) -> None:
        commit = CommitInfo(
            repo_name="test-repo",
            sha="abc1234",
            message="Test commit",
            date=datetime.now(UTC),
            additions=100,
            deletions=50,
        )
        assert commit.total_lines == 150


class TestCommitStats:
    def test_is_significant_by_commits(self) -> None:
        stats = CommitStats(commits=[], total_commits=10, max_lines_in_commit=50)
        assert stats.is_significant(min_commits=5, min_lines=200) is True

    def test_is_significant_by_lines(self) -> None:
        stats = CommitStats(commits=[], total_commits=2, max_lines_in_commit=300)
        assert stats.is_significant(min_commits=5, min_lines=200) is True

    def test_not_significant(self) -> None:
        stats = CommitStats(commits=[], total_commits=2, max_lines_in_commit=50)
        assert stats.is_significant(min_commits=5, min_lines=200) is False


class TestGitHubClient:
    def test_get_commits_since(self) -> None:
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_repo = MagicMock()
        mock_repo.name = "test-repo"

        mock_commit = MagicMock()
        mock_commit.sha = "abc1234567890"
        mock_commit.commit.message = "Test commit"
        mock_commit.commit.author.date = datetime.now(UTC)
        mock_commit.stats.additions = 10
        mock_commit.stats.deletions = 5

        mock_repo.get_commits.return_value = [mock_commit]
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.get_user.return_value = mock_user

        with patch("lsimons_bot.blog.github.Github", return_value=mock_github):
            client = GitHubClient(token="token")
            since = datetime(2024, 1, 1, tzinfo=UTC)
            result = client.get_commits_since(since)

        assert result.total_commits == 1
        assert result.max_lines_in_commit == 15
        assert result.commits[0].sha == "abc1234"
