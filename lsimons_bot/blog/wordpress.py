import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://public-api.wordpress.com/wp/v2/sites"


@dataclass
class BlogPost:
    id: int
    title: str
    date: datetime
    link: str


class WordPressClient:
    def __init__(self, username: str, app_password: str, site_id: str) -> None:
        self.username = username
        self.app_password = app_password
        self.site_id = site_id
        self.base_url = f"{BASE_URL}/{site_id}/posts"

    def _auth(self) -> tuple[str, str]:
        return (self.username, self.app_password)

    def get_latest_post(self) -> BlogPost | None:
        logger.debug("Fetching latest post from %s", self.base_url)
        response = requests.get(
            self.base_url,
            auth=self._auth(),
            params={"per_page": 1, "orderby": "date", "order": "desc"},
            timeout=30,
        )
        response.raise_for_status()
        posts = response.json()

        if not posts:
            return None

        post = posts[0]
        return BlogPost(
            id=post["id"],
            title=post["title"]["rendered"],
            date=datetime.fromisoformat(post["date_gmt"]).replace(tzinfo=timezone.utc),
            link=post["link"],
        )

    def create_post(self, title: str, content: str) -> BlogPost:
        logger.info("Creating new blog post: %s", title)
        response = requests.post(
            self.base_url,
            auth=self._auth(),
            json={"title": title, "content": content, "status": "publish"},
            timeout=60,
        )
        response.raise_for_status()
        post = response.json()

        return BlogPost(
            id=post["id"],
            title=post["title"]["rendered"],
            date=datetime.now(timezone.utc),
            link=post["link"],
        )
