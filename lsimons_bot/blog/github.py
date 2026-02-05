import logging
from dataclasses import dataclass
from datetime import datetime

from github import Github

logger = logging.getLogger(__name__)

GITHUB_USERNAME = "lsimons-bot"
GITHUB_AUTHOR_EMAIL = "bot@leosimons.com"


@dataclass
class CommitInfo:
    repo_name: str
    sha: str
    message: str
    date: datetime
    additions: int
    deletions: int

    @property
    def total_lines(self) -> int:
        return self.additions + self.deletions


@dataclass
class CommitStats:
    commits: list[CommitInfo]
    total_commits: int
    max_lines_in_commit: int

    def is_significant(self, min_commits: int = 5, min_lines: int = 200) -> bool:
        return self.total_commits > min_commits or self.max_lines_in_commit > min_lines


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.client = Github(token)
        self.username = GITHUB_USERNAME

    def get_commits_since(self, since: datetime) -> CommitStats:
        logger.info("Fetching commits since %s for user %s", since, self.username)
        commits: list[CommitInfo] = []
        max_lines = 0

        # PyGithub expects naive UTC datetimes
        since_naive = since.replace(tzinfo=None) if since.tzinfo else since

        user = self.client.get_user(self.username)
        repos = list(user.get_repos())
        logger.debug("Found %d repos for user %s", len(repos), self.username)
        for repo in repos:
            logger.debug("Processing repo: %s", repo.name)
            try:
                repo_commits = list(repo.get_commits(author=GITHUB_AUTHOR_EMAIL, since=since_naive))
                logger.debug("Repo %s: found %d commits", repo.name, len(repo_commits))
                for commit in repo_commits:
                    stats = commit.stats
                    additions = stats.additions if stats else 0
                    deletions = stats.deletions if stats else 0
                    total = additions + deletions

                    commit_info = CommitInfo(
                        repo_name=repo.name,
                        sha=commit.sha[:7],
                        message=commit.commit.message.split("\n")[0],
                        date=commit.commit.author.date,
                        additions=additions,
                        deletions=deletions,
                    )
                    commits.append(commit_info)
                    max_lines = max(max_lines, total)
            except Exception as e:
                logger.warning("Error fetching commits from %s: %s", repo.name, e)
                continue

        commits.sort(key=lambda c: c.date, reverse=True)
        logger.info("Found %d commits since %s", len(commits), since)

        return CommitStats(
            commits=commits,
            total_commits=len(commits),
            max_lines_in_commit=max_lines,
        )
