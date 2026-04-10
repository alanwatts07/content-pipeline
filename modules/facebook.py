"""Facebook Page module — posts via Graph API."""

import os
import requests
from modules import PublishResult, Metrics


class FacebookModule:
    name = "facebook"

    @property
    def _page_id(self):
        return os.environ.get("FB_PAGE_ID", "")

    @property
    def _token(self):
        return os.environ.get("FB_PAGE_ACCESS_TOKEN", "")

    def publish(self, title: str, body: str, excerpt: str = "", **kwargs) -> PublishResult:
        """Post to Facebook Page. Uses excerpt as message, with optional link."""
        message = excerpt or body[:500]
        link = kwargs.get("link", "")

        data = {"message": message, "access_token": self._token}
        if link:
            data["link"] = link

        try:
            resp = requests.post(
                f"https://graph.facebook.com/v19.0/{self._page_id}/feed",
                data=data, timeout=30,
            )
            result = resp.json()
            if "id" in result:
                post_id = result["id"]
                return PublishResult(
                    platform_post_id=post_id,
                    url=f"https://facebook.com/{post_id}",
                    success=True,
                )
            return PublishResult(success=False, error=result.get("error", {}).get("message", str(result)))
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    def get_metrics(self, platform_post_id: str) -> Metrics:
        try:
            resp = requests.get(
                f"https://graph.facebook.com/v19.0/{platform_post_id}",
                params={
                    "fields": "likes.summary(true),comments.summary(true),shares",
                    "access_token": self._token,
                },
                timeout=15,
            )
            data = resp.json()
            return Metrics(
                likes=data.get("likes", {}).get("summary", {}).get("total_count", 0),
                comments=data.get("comments", {}).get("summary", {}).get("total_count", 0),
                shares=data.get("shares", {}).get("count", 0),
            )
        except Exception:
            return Metrics()

    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        errors = []
        text = kwargs.get("excerpt", "") or body
        if len(text) > 63206:
            errors.append("Facebook post limit is 63,206 characters")
        return errors

    def is_configured(self) -> bool:
        return bool(self._page_id and self._token)
