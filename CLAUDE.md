# CLAUDE.md

## What This Is

Content Pipeline — an agentic content lifecycle API. Agents create goals, break them into tasks, draft posts, publish across platforms, and track analytics. Platform modules plug in like legos.

## Quick Start

```bash
pip install -r requirements.txt
python api.py    # runs on port 8100
```

## How Agents Use This

### 1. Check what needs doing
```bash
curl http://localhost:8100/api/agent/status -H "Authorization: Bearer $PIPELINE_API_KEY"
```
Returns: active goals, pending tasks, drafts, recent posts, connected platforms.

### 2. Create a goal
```bash
curl -X POST http://localhost:8100/api/goals \
  -H "Content-Type: application/json" \
  -d '{"title": "Grow solar SEO", "target_platforms": ["nei_blog", "facebook"]}'
```

### 3. Create a task under that goal
```bash
curl -X POST http://localhost:8100/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"goal_id": "abc123", "title": "Write solar tax credit post", "task_type": "write", "assigned_to": "terrance"}'
```

### 4. Create a draft
```bash
curl -X POST http://localhost:8100/api/drafts \
  -H "Content-Type: application/json" \
  -d '{"task_id": "def456", "title": "Solar Tax Credits 2026", "body": "## The Big Changes...", "target_platforms": ["nei_blog", "facebook"]}'
```

### 5. Publish the draft to all target platforms
```bash
curl -X POST http://localhost:8100/api/drafts/DRAFT_ID/publish
```
This hits each platform module automatically — NEI blog + Facebook in one call.

### 6. Check what performed best
```bash
curl http://localhost:8100/api/posts
curl -X POST http://localhost:8100/api/posts/refresh-analytics
```

## Platform Modules

Add a new platform by creating a file in `modules/`:

```python
# modules/twitter.py
class TwitterModule:
    name = "twitter"
    def publish(self, title, body, excerpt="", **kwargs) -> PublishResult: ...
    def get_metrics(self, platform_post_id) -> Metrics: ...
    def validate(self, title, body, **kwargs) -> list[str]: ...
    def is_configured(self) -> bool: ...
```

Available modules: `facebook`, `clawbr`, `void_blog`, `nei_blog`

## Architecture

- **FastAPI** on port 8100
- **SQLite** database (pipeline.db, gitignored)
- **No external dependencies** beyond FastAPI + requests
- Auth via Bearer token (PIPELINE_API_KEY in .env)
