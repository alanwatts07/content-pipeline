"""
Platform modules — each one implements publish(), get_metrics(), and validate().

To add a new platform:
1. Create a new file in modules/ (e.g. twitter.py)
2. Implement the PlatformModule interface
3. Register it in MODULES dict below

That's it. The API picks it up automatically.
"""

from __future__ import annotations
import os
from typing import Protocol, Optional


class PublishResult:
    """Result from publishing to a platform."""
    def __init__(self, platform_post_id: str = "", url: str = "", success: bool = True, error: str = ""):
        self.platform_post_id = platform_post_id
        self.url = url
        self.success = success
        self.error = error


class Metrics:
    """Engagement metrics from a platform."""
    def __init__(self, likes=0, comments=0, shares=0, clicks=0, impressions=0, reach=0):
        self.likes = likes
        self.comments = comments
        self.shares = shares
        self.clicks = clicks
        self.impressions = impressions
        self.reach = reach


class PlatformModule(Protocol):
    """Interface every platform module must implement."""
    name: str

    def publish(self, title: str, body: str, excerpt: str = "", **kwargs) -> PublishResult:
        """Publish content to the platform. Returns post ID + URL."""
        ...

    def get_metrics(self, platform_post_id: str) -> Metrics:
        """Fetch engagement metrics for a published post."""
        ...

    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        """Validate content before publishing. Returns list of error strings (empty = valid)."""
        ...

    def is_configured(self) -> bool:
        """Check if required env vars are set."""
        ...


def get_modules() -> dict[str, PlatformModule]:
    """Load all configured platform modules."""
    modules = {}

    # Import each module — only register if configured
    try:
        from modules.facebook import FacebookModule
        m = FacebookModule()
        if m.is_configured():
            modules[m.name] = m
    except Exception:
        pass

    try:
        from modules.clawbr import ClawbrModule
        m = ClawbrModule()
        if m.is_configured():
            modules[m.name] = m
    except Exception:
        pass

    try:
        from modules.void_blog import VoidBlogModule
        m = VoidBlogModule()
        if m.is_configured():
            modules[m.name] = m
    except Exception:
        pass

    try:
        from modules.nei_blog import NEIBlogModule
        m = NEIBlogModule()
        if m.is_configured():
            modules[m.name] = m
    except Exception:
        pass

    return modules
