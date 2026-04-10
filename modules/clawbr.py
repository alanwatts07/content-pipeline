"""Clawbr.org platform module — posts via clawbr CLI."""

import os
import subprocess
from modules import PublishResult, Metrics


class ClawbrModule:
    name = "clawbr"

    def publish(self, title: str, body: str, excerpt: str = "", **kwargs) -> PublishResult:
        """Post to Clawbr. Uses excerpt if provided (450 char limit), otherwise truncates body."""
        text = excerpt or body[:440]
        try:
            result = subprocess.run(
                ["clawbr", "post", text],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "CLAWBR_API_KEY": os.environ.get("CLAWBR_API_KEY", "")},
            )
            if result.returncode != 0:
                return PublishResult(success=False, error=result.stderr[:200])
            return PublishResult(platform_post_id=result.stdout.strip()[:100], success=True)
        except Exception as e:
            return PublishResult(success=False, error=str(e))

    def get_metrics(self, platform_post_id: str) -> Metrics:
        return Metrics()

    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        errors = []
        text = kwargs.get("excerpt", "") or body
        if len(text) > 450:
            errors.append(f"Text is {len(text)} chars, max 450 for Clawbr")
        return errors

    def is_configured(self) -> bool:
        return bool(os.environ.get("CLAWBR_API_KEY"))
