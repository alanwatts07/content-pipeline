"""Clawbr.org platform module — posts and metrics via REST API."""

import os
import requests
from modules import PublishResult, Metrics

API_BASE = "https://clawbr.org/api/v1"


class ClawbrModule:
    name = "clawbr"

    @property
    def _key(self):
        return os.environ.get("CLAWBR_API_KEY", "")

    @property
    def _headers(self):
        return {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"}

    def publish(self, title: str, body: str, excerpt: str = "", **kwargs) -> PublishResult:
        """Post to Clawbr. Uses excerpt if provided (450 char limit), otherwise truncates body."""
        text = excerpt or body[:440]
        try:
            resp = requests.post(
                f"{API_BASE}/posts",
                headers=self._headers,
                json={"content": text},
                timeout=30,
            )
            data = resp.json()
            post_id = data.get("id") or data.get("post", {}).get("id", "")
            if post_id:
                return PublishResult(
                    platform_post_id=str(post_id),
                    url=f"https://clawbr.org/post/{post_id}",
                    success=True,
                )
            return PublishResult(success=False, error=str(data))
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    def get_metrics(self, platform_post_id: str) -> Metrics:
        """Fetch engagement metrics from Clawbr feed and find the matching post."""
        try:
            resp = requests.get(
                f"{API_BASE}/feed/global",
                headers=self._headers,
                params={"limit": 50},
                timeout=15,
            )
            data = resp.json()
            posts = data.get("posts", data if isinstance(data, list) else [])
            for post in posts:
                if str(post.get("id", "")) == str(platform_post_id):
                    return Metrics(
                        likes=post.get("likesCount", 0),
                        comments=post.get("repliesCount", 0),
                        shares=post.get("repostsCount", 0),
                        impressions=post.get("viewsCount", 0),
                    )
            return Metrics()
        except Exception:
            return Metrics()

    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        errors = []
        text = kwargs.get("excerpt", "") or body
        if len(text) > 450:
            errors.append(f"Text is {len(text)} chars, max 450 for Clawbr")
        return errors

    def is_configured(self) -> bool:
        return bool(self._key)
