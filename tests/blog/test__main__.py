import sys
from unittest.mock import AsyncMock, patch

from lsimons_bot.blog.__main__ import main
from lsimons_bot.blog.publish import PublishResult


class TestMain:
    def test_dry_run_success(self) -> None:
        result = PublishResult(should_publish=True, reason="Would publish")

        with (
            patch.object(sys, "argv", ["blog"]),
            patch(
                "lsimons_bot.blog.__main__.check_and_publish",
                new=AsyncMock(return_value=result),
            ),
        ):
            exit_code = main()

        assert exit_code == 1  # No post created in dry run

    def test_no_publish_needed(self) -> None:
        result = PublishResult(should_publish=False, reason="Recent post exists")

        with (
            patch.object(sys, "argv", ["blog"]),
            patch(
                "lsimons_bot.blog.__main__.check_and_publish",
                new=AsyncMock(return_value=result),
            ),
        ):
            exit_code = main()

        assert exit_code == 0

    def test_error_handling(self) -> None:
        with (
            patch.object(sys, "argv", ["blog"]),
            patch(
                "lsimons_bot.blog.__main__.check_and_publish",
                new=AsyncMock(side_effect=Exception("Test error")),
            ),
        ):
            exit_code = main()

        assert exit_code == 1
