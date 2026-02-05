from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from lsimons_bot.blog.wordpress import BlogPost, WordPressClient


def _make_client() -> WordPressClient:
    return WordPressClient(
        username="user",
        app_password="pass",
        client_id="123",
        client_secret="secret",
        site_id="site123",
    )


class TestWordPressClient:
    def test_get_latest_post(self) -> None:
        client = _make_client()
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "title": {"rendered": "Test Post"},
                "date_gmt": "2024-01-15T10:00:00",
                "link": "https://example.com/test-post",
            }
        ]

        with patch("lsimons_bot.blog.wordpress.requests.get", return_value=mock_response):
            result = client.get_latest_post()

        assert result is not None
        assert result.id == 1
        assert result.title == "Test Post"

    def test_get_latest_post_empty(self) -> None:
        client = _make_client()
        mock_response = MagicMock()
        mock_response.json.return_value = []

        with patch("lsimons_bot.blog.wordpress.requests.get", return_value=mock_response):
            result = client.get_latest_post()

        assert result is None

    def test_create_post(self) -> None:
        client = _make_client()
        mock_token_response = MagicMock()
        mock_token_response.json.return_value = {"access_token": "test_token"}

        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "id": 2,
            "title": {"rendered": "New Post"},
            "link": "https://example.com/new-post",
        }

        with patch("lsimons_bot.blog.wordpress.requests.post") as mock_post:
            mock_post.side_effect = [mock_token_response, mock_post_response]
            result = client.create_post(title="New Post", content="<p>Content</p>")

        assert result.id == 2
        assert result.title == "New Post"


class TestBlogPost:
    def test_dataclass(self) -> None:
        post = BlogPost(
            id=1,
            title="Test",
            date=datetime.now(timezone.utc),
            link="https://example.com",
        )
        assert post.id == 1
        assert post.title == "Test"
