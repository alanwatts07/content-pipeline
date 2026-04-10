"""
Content Pipeline API — agentic content lifecycle management.

Goals → Tasks → Drafts → Posted → Analytics
Platform modules plug in like legos.

Usage:
    python api.py                    # Start on port 8100
    uvicorn api:app --port 8100      # Same thing
"""

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

from db import get_db, init_db
from models import (
    GoalCreate, GoalUpdate, Goal,
    TaskCreate, TaskUpdate, Task,
    DraftCreate, DraftUpdate, Draft,
    Post, Analytics, AgentStatus, new_id,
)
from modules import get_modules

# ── Init ──

init_db()
app = FastAPI(title="Content Pipeline", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PIPELINE_API_KEY = os.environ.get("PIPELINE_API_KEY", "")


# ── Auth ──

def require_auth(request: Request):
    if not PIPELINE_API_KEY:
        return  # no key set = open access (dev mode)
    auth = request.headers.get("authorization", "")
    if auth.replace("Bearer ", "") != PIPELINE_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ── Helpers ──

def row_to_dict(row) -> dict:
    if row is None:
        return {}
    d = dict(row)
    # Parse JSON strings back to objects
    for key in ("target_platforms", "target_metrics"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                d[key] = [] if "platforms" in key else {}
    return d


# ── Agent Status (everything in one call) ──

@app.get("/api/agent/status", response_model=AgentStatus)
def agent_status(_=Depends(require_auth)):
    """Returns everything an agent needs: goals, tasks, drafts, posts, platforms."""
    db = get_db()

    goals = [row_to_dict(r) for r in db.execute(
        "SELECT * FROM goals WHERE status = 'active' ORDER BY created_at DESC"
    ).fetchall()]

    tasks = [row_to_dict(r) for r in db.execute(
        "SELECT * FROM tasks WHERE status IN ('pending', 'in_progress') ORDER BY created_at DESC"
    ).fetchall()]

    drafts = [row_to_dict(r) for r in db.execute(
        "SELECT * FROM drafts WHERE status IN ('draft', 'approved') ORDER BY created_at DESC"
    ).fetchall()]

    posts = [row_to_dict(r) for r in db.execute(
        "SELECT * FROM posts ORDER BY posted_at DESC LIMIT 20"
    ).fetchall()]

    modules = get_modules()
    platforms = {name: {"connected": True} for name in modules}

    db.close()
    return AgentStatus(
        active_goals=goals,
        pending_tasks=tasks,
        drafts=drafts,
        recent_posts=posts,
        platforms=platforms,
    )


# ── Goals ──

@app.get("/api/goals")
def list_goals(status: str = None, _=Depends(require_auth)):
    db = get_db()
    if status:
        rows = db.execute("SELECT * FROM goals WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM goals ORDER BY created_at DESC").fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]


@app.get("/api/goals/{goal_id}")
def get_goal(goal_id: str, _=Depends(require_auth)):
    db = get_db()
    goal = db.execute("SELECT * FROM goals WHERE id = ?", (goal_id,)).fetchone()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    tasks = db.execute("SELECT * FROM tasks WHERE goal_id = ?", (goal_id,)).fetchall()
    drafts = db.execute("SELECT * FROM drafts WHERE goal_id = ?", (goal_id,)).fetchall()
    db.close()
    return {**row_to_dict(goal), "tasks": [row_to_dict(t) for t in tasks], "drafts": [row_to_dict(d) for d in drafts]}


@app.post("/api/goals")
def create_goal(req: GoalCreate, _=Depends(require_auth)):
    db = get_db()
    goal_id = new_id()
    db.execute(
        "INSERT INTO goals (id, title, description, target_platforms, target_metrics, created_by, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (goal_id, req.title, req.description, json.dumps(req.target_platforms), json.dumps(req.target_metrics), req.created_by, req.due_date),
    )
    db.commit()
    db.close()
    return {"id": goal_id, "status": "created"}


@app.put("/api/goals/{goal_id}")
def update_goal(goal_id: str, req: GoalUpdate, _=Depends(require_auth)):
    db = get_db()
    updates, params = [], []
    if req.title is not None:
        updates.append("title = ?"); params.append(req.title)
    if req.description is not None:
        updates.append("description = ?"); params.append(req.description)
    if req.status is not None:
        updates.append("status = ?"); params.append(req.status)
    if req.target_platforms is not None:
        updates.append("target_platforms = ?"); params.append(json.dumps(req.target_platforms))
    if req.due_date is not None:
        updates.append("due_date = ?"); params.append(req.due_date)
    if not updates:
        raise HTTPException(status_code=400, detail="Nothing to update")
    params.append(goal_id)
    db.execute(f"UPDATE goals SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    db.close()
    return {"id": goal_id, "status": "updated"}


# ── Tasks ──

@app.get("/api/tasks")
def list_tasks(status: str = None, assigned_to: str = None, goal_id: str = None, _=Depends(require_auth)):
    db = get_db()
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"; params.append(status)
    if assigned_to:
        query += " AND assigned_to = ?"; params.append(assigned_to)
    if goal_id:
        query += " AND goal_id = ?"; params.append(goal_id)
    query += " ORDER BY created_at DESC"
    rows = db.execute(query, params).fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]


@app.post("/api/tasks")
def create_task(req: TaskCreate, _=Depends(require_auth)):
    db = get_db()
    task_id = new_id()
    db.execute(
        "INSERT INTO tasks (id, goal_id, title, description, task_type, assigned_to) VALUES (?, ?, ?, ?, ?, ?)",
        (task_id, req.goal_id, req.title, req.description, req.task_type, req.assigned_to),
    )
    db.commit()
    db.close()
    return {"id": task_id, "status": "created"}


@app.put("/api/tasks/{task_id}")
def update_task(task_id: str, req: TaskUpdate, _=Depends(require_auth)):
    db = get_db()
    updates, params = [], []
    if req.title is not None:
        updates.append("title = ?"); params.append(req.title)
    if req.description is not None:
        updates.append("description = ?"); params.append(req.description)
    if req.status is not None:
        updates.append("status = ?"); params.append(req.status)
        if req.status == "done":
            updates.append("completed_at = ?"); params.append(datetime.now().isoformat())
    if req.assigned_to is not None:
        updates.append("assigned_to = ?"); params.append(req.assigned_to)
    if not updates:
        raise HTTPException(status_code=400, detail="Nothing to update")
    params.append(task_id)
    db.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    db.close()
    return {"id": task_id, "status": "updated"}


# ── Drafts ──

@app.get("/api/drafts")
def list_drafts(status: str = None, _=Depends(require_auth)):
    db = get_db()
    if status:
        rows = db.execute("SELECT * FROM drafts WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM drafts ORDER BY created_at DESC").fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]


@app.post("/api/drafts")
def create_draft(req: DraftCreate, _=Depends(require_auth)):
    db = get_db()
    draft_id = new_id()
    db.execute(
        "INSERT INTO drafts (id, task_id, goal_id, title, body, excerpt, target_platforms, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (draft_id, req.task_id, req.goal_id, req.title, req.body, req.excerpt, json.dumps(req.target_platforms), req.created_by),
    )
    db.commit()
    db.close()
    return {"id": draft_id, "status": "created"}


@app.put("/api/drafts/{draft_id}")
def update_draft(draft_id: str, req: DraftUpdate, _=Depends(require_auth)):
    db = get_db()
    updates, params = [], []
    if req.title is not None:
        updates.append("title = ?"); params.append(req.title)
    if req.body is not None:
        updates.append("body = ?"); params.append(req.body)
    if req.excerpt is not None:
        updates.append("excerpt = ?"); params.append(req.excerpt)
    if req.status is not None:
        updates.append("status = ?"); params.append(req.status)
        if req.status == "approved":
            updates.append("approved_at = ?"); params.append(datetime.now().isoformat())
    if req.target_platforms is not None:
        updates.append("target_platforms = ?"); params.append(json.dumps(req.target_platforms))
    if not updates:
        raise HTTPException(status_code=400, detail="Nothing to update")
    params.append(draft_id)
    db.execute(f"UPDATE drafts SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    db.close()
    return {"id": draft_id, "status": "updated"}


@app.post("/api/drafts/{draft_id}/publish")
def publish_draft(draft_id: str, _=Depends(require_auth)):
    """Publish a draft to all its target platforms."""
    db = get_db()
    draft = db.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    draft_dict = row_to_dict(draft)
    platforms = draft_dict.get("target_platforms", [])
    if not platforms:
        raise HTTPException(status_code=400, detail="No target platforms set")

    modules = get_modules()
    results = []

    for platform in platforms:
        module = modules.get(platform)
        if not module:
            results.append({"platform": platform, "success": False, "error": f"Module '{platform}' not found or not configured"})
            continue

        errors = module.validate(draft_dict["title"], draft_dict["body"])
        if errors:
            results.append({"platform": platform, "success": False, "error": "; ".join(errors)})
            continue

        pub = module.publish(
            title=draft_dict["title"],
            body=draft_dict["body"],
            excerpt=draft_dict.get("excerpt", ""),
        )

        if pub.success:
            post_id = new_id()
            db.execute(
                "INSERT INTO posts (id, draft_id, platform, platform_post_id, url) VALUES (?, ?, ?, ?, ?)",
                (post_id, draft_id, platform, pub.platform_post_id, pub.url),
            )
            results.append({"platform": platform, "success": True, "post_id": post_id, "url": pub.url})
        else:
            results.append({"platform": platform, "success": False, "error": pub.error})

    # Mark draft as published if at least one platform succeeded
    if any(r["success"] for r in results):
        db.execute("UPDATE drafts SET status = 'published' WHERE id = ?", (draft_id,))

    db.commit()
    db.close()
    return {"draft_id": draft_id, "results": results}


# ── Posts ──

@app.get("/api/posts")
def list_posts(platform: str = None, limit: int = 20, _=Depends(require_auth)):
    db = get_db()
    if platform:
        rows = db.execute("SELECT * FROM posts WHERE platform = ? ORDER BY posted_at DESC LIMIT ?", (platform, limit)).fetchall()
    else:
        rows = db.execute("SELECT * FROM posts ORDER BY posted_at DESC LIMIT ?", (limit,)).fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]


@app.get("/api/posts/{post_id}/analytics")
def get_analytics(post_id: str, _=Depends(require_auth)):
    db = get_db()
    rows = db.execute("SELECT * FROM analytics WHERE post_id = ? ORDER BY checked_at DESC LIMIT 1", (post_id,)).fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]


@app.post("/api/posts/refresh-analytics")
def refresh_analytics(_=Depends(require_auth)):
    """Refresh metrics for all recent posts."""
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY posted_at DESC LIMIT 50").fetchall()
    modules = get_modules()
    refreshed = 0

    for post in posts:
        post_dict = row_to_dict(post)
        module = modules.get(post_dict["platform"])
        if not module or not post_dict.get("platform_post_id"):
            continue

        metrics = module.get_metrics(post_dict["platform_post_id"])
        analytics_id = new_id()
        db.execute(
            "INSERT INTO analytics (id, post_id, platform, likes, comments, shares, clicks, impressions, reach) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (analytics_id, post_dict["id"], post_dict["platform"], metrics.likes, metrics.comments, metrics.shares, metrics.clicks, metrics.impressions, metrics.reach),
        )
        refreshed += 1

    db.commit()
    db.close()
    return {"refreshed": refreshed}


# ── Health ──

@app.get("/ping")
def ping():
    modules = get_modules()
    return {"status": "ok", "platforms": list(modules.keys())}


# ── Run ──

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
