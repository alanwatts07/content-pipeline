"""Void Technology blog module — posts via agent API."""

import os
import requests
from modules import PublishResult, Metrics


class VoidBlogModule:
    name = "void_blog"

    @property
    def _url(self):
        return os.environ.get("VOID_API_URL", "https://voidtechnology.net")

    @property
    def _key(self):
        return os.environ.get("VOID_API_KEY", "")

    def publish(self, title: str, body: str, excerpt: str = "", **kwargs) -> PublishResult:
        try:
            resp = requests.post(
                f"{self._url}/api/agent/posts",
                headers={"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"},
                json={"title": title, "content": body, "excerpt": excerpt or None, "publish": True},
                timeout=30,
            )
            data = resp.json()
            if data.get("slug"):
                return PublishResult(
                    platform_post_id=data["slug"],
                    url=f"{self._url}/blog/{data['slug']}",
                    success=True,
                )
            return PublishResult(success=False, error=str(data))
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    def get_metrics(self, platform_post_id: str) -> Metrics:
        return Metrics()

    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        errors = []
        if len(title) < 3:
            errors.append("Title must be at least 3 characters")
        if len(body) < 50:
            errors.append("Body must be at least 50 characters")
        return errors

    def is_configured(self) -> bool:
        return bool(self._key)
