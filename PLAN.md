# Content Pipeline — Agentic Marketing Task System

## Concept

A central API that agents hit to manage the full content lifecycle: Goals → Tasks → Drafts → Posted → Analytics. Platform modules (Facebook, X, LinkedIn, Instagram, Clawbr, blogs) plug in like legos. Agents can create goals, break them into tasks, draft posts, publish across platforms, and track performance — all through one API.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Content Pipeline API                   │
│                   (FastAPI + SQLite)                      │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│  Goals   │  Tasks   │  Drafts  │  Posted  │  Analytics  │
│          │          │          │          │             │
│ "Grow    │ "Write   │ draft    │ published│ likes: 12   │
│  solar   │  3 solar │ text +   │ to FB,   │ clicks: 47  │
│  SEO"    │  posts"  │ platform │ NEI blog │ shares: 3   │
│          │          │ targets  │          │             │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
                          │
              ┌───────────┴───────────┐
              │   Platform Modules    │
              ├───────────────────────┤
              │ facebook.py  — Graph API post + read metrics    │
              │ twitter.py   — X API v2 post + read metrics     │
              │ linkedin.py  — LinkedIn API post                │
              │ instagram.py — Instagram Graph API              │
              │ clawbr.py    — clawbr CLI post                  │
              │ void_blog.py — Void Technology blog API         │
              │ nei_blog.py  — New Energy Initiative Sanity API │
              └───────────────────────────────────────────────┘
```

## Data Model

### Goals
```
id, title, description, status (active/completed/paused),
target_platforms[], target_metrics{}, created_at, due_date,
created_by (agent name or "operator")
```

### Tasks (broken down from goals)
```
id, goal_id, title, description, status (pending/in_progress/done),
assigned_to (agent name), task_type (research/write/post/analyze),
created_at, completed_at
```

### Drafts (content ready to post)
```
id, task_id, goal_id, title, body, excerpt,
target_platforms[] (which platforms to post to),
status (draft/approved/rejected),
created_by, created_at, approved_at
```

### Posts (published content)
```
id, draft_id, platform, platform_post_id,
url, posted_at, posted_by
```

### Analytics (per-post metrics, updated periodically)
```
id, post_id, platform, checked_at,
likes, comments, shares, clicks, impressions, reach
```

## API Endpoints

### Goals
```
GET    /api/goals                    — list all goals (filter by status)
GET    /api/goals/:id               — get goal with tasks + drafts + posts
POST   /api/goals                   — create a goal
PUT    /api/goals/:id               — update goal
```

### Tasks
```
GET    /api/tasks                    — list tasks (filter by status, goal, assignee)
POST   /api/tasks                   — create a task
PUT    /api/tasks/:id               — update task status
```

### Drafts
```
GET    /api/drafts                   — list drafts (filter by status, platform)
POST   /api/drafts                   — create a draft
PUT    /api/drafts/:id               — update/approve/reject draft
POST   /api/drafts/:id/publish       — publish draft to target platforms
```

### Posts
```
GET    /api/posts                    — list published posts (filter by platform, date)
GET    /api/posts/:id/analytics      — get metrics for a post
POST   /api/posts/refresh-analytics  — trigger metric refresh across platforms
```

### Agent Info (single call to get everything)
```
GET    /api/agent/status             — returns:
  {
    active_goals: [...],
    pending_tasks: [...],        // assigned to this agent
    drafts_awaiting_approval: [...],
    recent_posts: [...],         // last 10 with metrics
    top_performing: [...],       // best posts by engagement
    platforms: {                 // which modules are connected
      facebook: { connected: true, page: "Void Technology" },
      nei_blog: { connected: true },
      clawbr: { connected: true },
      twitter: { connected: false },
      ...
    }
  }
```

## Platform Modules

Each module is a Python file in `modules/` that implements:

```python
class PlatformModule:
    name: str                              # "facebook", "twitter", etc
    def publish(draft) -> post_result      # post content, return platform_post_id + url
    def get_metrics(post_id) -> metrics    # fetch likes/comments/shares/etc
    def validate(draft) -> errors          # check char limits, format, etc
```

Modules to build:
1. **facebook.py** — Graph API, already have token
2. **clawbr.py** — wraps `clawbr post`, 450 char limit
3. **void_blog.py** — POST /api/agent/posts, already working
4. **nei_blog.py** — POST /api/create-post, already working
5. **twitter.py** — X API v2 (needs app + token)
6. **linkedin.py** — LinkedIn API (needs app + token)
7. **instagram.py** — Instagram Graph API via Facebook (needs setup)

## Implementation Steps

### 1. Create project structure
```
~/Hackstuff/content-pipeline/
├── api.py              — FastAPI app
├── db.py               — SQLite setup + models
├── models.py           — Pydantic models
├── modules/
│   ├── __init__.py     — module registry
│   ├── facebook.py
│   ├── clawbr.py
│   ├── void_blog.py
│   └── nei_blog.py
├── pipeline.db         — SQLite database
├── .env                — API keys for all platforms
└── requirements.txt
```

### 2. Build the core API + SQLite database
- Goals, Tasks, Drafts, Posts, Analytics tables
- CRUD endpoints for each
- Agent status endpoint that returns everything in one call

### 3. Build the first 4 platform modules
- Facebook, Clawbr, Void Blog, NEI Blog (all already working, just wrap them)

### 4. Wire Terrance to use the pipeline
- Instead of posting directly, Terrance creates drafts in the pipeline
- Pipeline handles publishing to the right platforms
- Analytics refresh runs on cron

### 5. Add analytics cron
- Every few hours, hit each platform's API to refresh metrics
- Store in analytics table
- Agent can query "what's performing best"

## Auth
Simple Bearer token like the other APIs. One token for agents, stored in .env.

## Why SQLite
- Single file, no Docker, no setup
- Good enough for this volume (dozens of posts, not millions)
- Easy to inspect, backup, and commit the DB file to git if needed
- Can upgrade to PostgreSQL later if needed
