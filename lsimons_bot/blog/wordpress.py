import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://public-api.wordpress.com/wp/v2/sites"
TOKEN_URL = "https://public-api.wordpress.com/oauth2/token"


@dataclass
class BlogPost:
    id: int
    title: str
    date: datetime
    link: str


class WordPressClient:
    def __init__(
        self,
        username: str,
        app_password: str,
        client_id: str,
        client_secret: str,
        site_id: str,
    ) -> None:
        self.username = username
        self.app_password = app_password
        self.client_id = client_id
        self.client_secret = client_secret
        self.site_id = site_id
        self.base_url = f"{BASE_URL}/{site_id}/posts"
        self._access_token: str | None = None

    def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token

        logger.debug("Fetching OAuth2 access token")
        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "password",
                "username": self.username,
                "password": self.app_password,
            },
            timeout=30,
        )
        response.raise_for_status()
        self._access_token = response.json()["access_token"]
        return self._access_token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._get_access_token()}"}

    def get_latest_post(self) -> BlogPost | None:
        logger.debug("Fetching latest post from %s", self.base_url)
        response = requests.get(
            self.base_url,
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
            headers=self._headers(),
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
