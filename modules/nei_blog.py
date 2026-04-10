"""New Energy Initiative blog module — posts via Sanity API."""

import os
import requests
from modules import PublishResult, Metrics


class NEIBlogModule:
    name = "nei_blog"

    @property
    def _url(self):
        return os.environ.get("NEI_API_URL", "https://www.newenergyinitiative.com")

    @property
    def _key(self):
        return os.environ.get("NEI_API_KEY", "")

    def publish(self, title: str, body: str, excerpt: str = "", **kwargs) -> PublishResult:
        focus_keyword = kwargs.get("focus_keyword", title.split(":")[0].strip().lower())
        categories = kwargs.get("categories", ["solar"])

        try:
            resp = requests.post(
                f"{self._url}/api/create-post",
                headers={"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"},
                json={
                    "title": title,
                    "body": body,
                    "excerpt": excerpt or body[:200],
                    "metaDescription": excerpt or body[:160],
                    "focusKeyword": focus_keyword,
                    "categories": categories,
                },
                timeout=30,
            )
            data = resp.json()
            if data.get("success"):
                post = data.get("post", {})
                return PublishResult(
                    platform_post_id=post.get("slug", ""),
                    url=f"{self._url}{post.get('url', '')}",
                    success=True,
                )
            return PublishResult(success=False, error=str(data))
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    def get_metrics(self, platform_post_id: str) -> Metrics:
        return Metrics()

    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        errors = []
        if not title:
            errors.append("Title is required")
        if len(body) < 100:
            errors.append("Body should be at least 100 characters for a blog post")
        return errors

    def is_configured(self) -> bool:
        return bool(self._key)
