# Content Pipeline

![Status](https://img.shields.io/badge/status-building-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

An agentic content pipeline that manages the full lifecycle: **Goals → Tasks → Drafts → Posted → Analytics**. Platform modules (Facebook, X, LinkedIn, Clawbr, blogs) plug in like legos.

Built to be driven by autonomous AI agents — they create goals, break them into tasks, draft posts, publish across platforms, and track what performs best.

## Architecture

```
        Agent hits API
             │
             ▼
┌────────────────────────────────┐
│       Content Pipeline API      │
│         FastAPI + SQLite        │
├────────┬────────┬────────┬─────┤
│ Goals  │ Tasks  │ Drafts │Posts│
│        │        │        │     │
│"Grow   │"Write  │ draft  │live │
│ solar  │ 3 SEO  │ text + │on   │
│ SEO"   │ posts" │targets │FB   │
└────────┴────────┴───┬────┴─────┘
                      │
          ┌───────────┴───────────┐
          │   Platform Modules    │
          ├───────────────────────┤
          │ facebook   │ twitter  │
          │ clawbr     │ linkedin │
          │ void_blog  │ nei_blog │
          │ instagram  │ ...      │
          └───────────────────────┘
```

## Quick Start

```bash
pip install -r requirements.txt
python api.py
# → http://localhost:8100/docs
```

## API Overview

```bash
# Agent gets everything in one call
GET /api/agent/status

# Goal management
POST /api/goals        { title, description, target_platforms[] }
GET  /api/goals

# Task management
POST /api/tasks        { goal_id, title, task_type, assigned_to }
GET  /api/tasks?status=pending&assigned_to=terrance

# Draft content
POST /api/drafts       { task_id, title, body, target_platforms[] }
POST /api/drafts/:id/publish    # publishes to all target platforms

# Published posts + analytics
GET  /api/posts
GET  /api/posts/:id/analytics
POST /api/posts/refresh-analytics
```

## Platform Modules

Each module implements `publish()`, `get_metrics()`, and `validate()`:

| Module | Status | Platform |
|--------|--------|----------|
| `facebook` | 🔧 Building | Facebook Page via Graph API |
| `clawbr` | 🔧 Building | Clawbr.org via CLI |
| `void_blog` | 🔧 Building | Void Technology blog API |
| `nei_blog` | 🔧 Building | New Energy Initiative Sanity API |
| `twitter` | 📋 Planned | X API v2 |
| `linkedin` | 📋 Planned | LinkedIn API |
| `instagram` | 📋 Planned | Instagram Graph API |

## Tech Stack

- **FastAPI** — async API framework
- **SQLite** — single-file database, zero setup
- **Pydantic** — data validation and serialization
- **Python 3.11+** — type hints, async/await

## License

MIT
