"""Pydantic models for the Content Pipeline API."""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


def new_id() -> str:
    return uuid.uuid4().hex[:12]


# ── Goals ──

class GoalCreate(BaseModel):
    title: str
    description: str = ""
    target_platforms: list[str] = Field(default_factory=list)
    target_metrics: dict = Field(default_factory=dict)
    created_by: str = "operator"
    due_date: Optional[str] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    target_platforms: Optional[list[str]] = None
    due_date: Optional[str] = None


class Goal(BaseModel):
    id: str
    title: str
    description: str
    status: str
    target_platforms: list[str]
    target_metrics: dict
    created_by: str
    created_at: str
    due_date: Optional[str]


# ── Tasks ──

class TaskCreate(BaseModel):
    goal_id: Optional[str] = None
    title: str
    description: str = ""
    task_type: str = "write"
    assigned_to: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None


class Task(BaseModel):
    id: str
    goal_id: Optional[str]
    title: str
    description: str
    status: str
    task_type: str
    assigned_to: Optional[str]
    created_at: str
    completed_at: Optional[str]


# ── Drafts ──

class DraftCreate(BaseModel):
    task_id: Optional[str] = None
    goal_id: Optional[str] = None
    title: str
    body: str
    excerpt: str = ""
    target_platforms: list[str] = Field(default_factory=list)
    created_by: Optional[str] = None


class DraftUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    excerpt: Optional[str] = None
    status: Optional[str] = None
    target_platforms: Optional[list[str]] = None


class Draft(BaseModel):
    id: str
    task_id: Optional[str]
    goal_id: Optional[str]
    title: str
    body: str
    excerpt: str
    target_platforms: list[str]
    status: str
    created_by: Optional[str]
    created_at: str
    approved_at: Optional[str]


# ── Posts ──

class Post(BaseModel):
    id: str
    draft_id: Optional[str]
    platform: str
    platform_post_id: Optional[str]
    url: Optional[str]
    posted_at: str
    posted_by: Optional[str]


# ── Analytics ──

class Analytics(BaseModel):
    id: str
    post_id: str
    platform: str
    checked_at: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    impressions: int = 0
    reach: int = 0


# ── Agent Status (everything in one call) ──

class AgentStatus(BaseModel):
    active_goals: list[Goal] = Field(default_factory=list)
    pending_tasks: list[Task] = Field(default_factory=list)
    drafts: list[Draft] = Field(default_factory=list)
    recent_posts: list[Post] = Field(default_factory=list)
    platforms: dict = Field(default_factory=dict)
