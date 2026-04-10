# Content Pipeline — Agent Operations Guide

You use the Content Pipeline API for ALL content work. Never post directly to platforms — the pipeline handles publishing and tracks analytics.

**API:** `http://localhost:8100`
**Auth:** `Authorization: Bearer $PIPELINE_API_KEY`
**Dashboard:** `http://localhost:8100/dashboard`

---

## Session Flow

Every session, follow this loop:

### 1. Check In

```bash
curl -s http://localhost:8100/api/agent/status \
  -H "Authorization: Bearer $PIPELINE_API_KEY"
```

This returns everything you need in one call:
- `active_goals` — what you're working toward
- `pending_tasks` — what needs doing right now
- `drafts` — content in progress
- `recent_posts` — what's already published
- `platforms` — what's connected

**Read this first. Don't duplicate work that's already done.**

### 2. Pick Your Work

Look at what's pending:
- **If there are pending tasks assigned to you** — do them
- **If there are active goals with no tasks** — break them into tasks
- **If there are approved drafts** — publish them
- **If nothing's pending** — check if a goal needs new tasks, or wait for new goals

### 3. Break Goals into Tasks

When you see an active goal with no tasks (or tasks are all done), create new ones:

```bash
curl -X POST http://localhost:8100/api/tasks \
  -H "Authorization: Bearer $PIPELINE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "goal_id": "GOAL_ID_HERE",
    "title": "Write post: Solar ROI in 2026",
    "description": "SEO blog post targeting 'solar roi 2026', 800-1200 words, include real numbers",
    "task_type": "write",
    "assigned_to": "terrance"
  }'
```

Task types: `research`, `write`, `post`, `analyze`, `other`

### 4. Write Drafts

When you pick up a `write` task, mark it in progress then create a draft:

```bash
# Mark task as started
curl -X PUT http://localhost:8100/api/tasks/TASK_ID \
  -H "Authorization: Bearer $PIPELINE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'

# Create the draft
curl -X POST http://localhost:8100/api/drafts \
  -H "Authorization: Bearer $PIPELINE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK_ID",
    "goal_id": "GOAL_ID",
    "title": "Is Solar Worth It in 2026? A Real Cost Breakdown",
    "body": "Full markdown content here...",
    "excerpt": "Short summary for social posts and previews",
    "target_platforms": ["nei_blog", "clawbr"],
    "created_by": "terrance"
  }'

# Mark task done
curl -X PUT http://localhost:8100/api/tasks/TASK_ID \
  -H "Authorization: Bearer $PIPELINE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### 5. Publish

Publish approved drafts (or drafts you just created — handler may auto-approve):

```bash
curl -X POST http://localhost:8100/api/drafts/DRAFT_ID/publish \
  -H "Authorization: Bearer $PIPELINE_API_KEY"
```

This publishes to ALL target platforms in one call. The pipeline handles the API calls to each platform. You get back results per platform:

```json
{
  "draft_id": "abc123",
  "results": [
    {"platform": "nei_blog", "success": true, "url": "https://..."},
    {"platform": "clawbr", "success": true, "post_id": "xyz789"}
  ]
}
```

### 6. Check Analytics

After posts have been live for a while, refresh metrics:

```bash
curl -X POST http://localhost:8100/api/posts/refresh-analytics \
  -H "Authorization: Bearer $PIPELINE_API_KEY"
```

Then check what's performing:

```bash
curl -s http://localhost:8100/api/posts \
  -H "Authorization: Bearer $PIPELINE_API_KEY"
```

Use this to inform future content — double down on topics that get engagement.

---

## Available Platforms

| Platform | What it posts | Content format |
|----------|--------------|----------------|
| `nei_blog` | New Energy Initiative blog | Full markdown, SEO metadata |
| `void_blog` | Void Technology blog | Full markdown |
| `clawbr` | Clawbr social platform | Short text, 450 char max |
| `facebook` | Facebook Page | Short text + optional link |

### Platform Tips

- **Blog posts** (`nei_blog`, `void_blog`): Full body goes as the post. Write 800-1200 words in markdown.
- **Clawbr**: Uses the `excerpt` field. Keep it under 450 chars. Punchy, opinionated, conversational.
- **Facebook**: Uses the `excerpt` field. Short and shareable.
- **Multi-platform**: Set `target_platforms` to publish everywhere at once. Write the `body` for blogs and `excerpt` for social — both get used.

---

## Content Guidelines

**For blog platforms (nei_blog, void_blog):**
- `body`: Full markdown (headers, bold, lists are fine)
- `excerpt`: 1-2 sentence summary for meta description and social cards
- Include `focusKeyword` in the title and first paragraph
- **Always include sources.** If you researched anything — stats, programs, prices, studies — add a "Sources" or "References" section at the bottom of the blog post with linked URLs. Real links to real pages. No made-up URLs. This builds credibility and SEO.

**For social platforms (clawbr, facebook):**
- The `excerpt` is your post text
- No markdown formatting — plain text only
- Strong take or useful insight, not a summary of the blog post
- Make it standalone — someone should get value without clicking through

---

## Example: Full Session

```
1. GET /api/agent/status
   → See goal "Solar SEO content push" with no tasks

2. POST /api/tasks  (×3)
   → "Write post: Solar tax credits 2026"      (task_type: write)
   → "Write post: Solar vs grid cost over 10yr" (task_type: write)
   → "Write post: Home battery storage guide"   (task_type: write)

3. PUT /api/tasks/TASK_1 → {"status": "in_progress"}

4. POST /api/drafts
   → title: "Solar Tax Credits in 2026: What Homeowners Actually Save"
   → body: full 1000-word markdown post
   → excerpt: "The federal solar tax credit is 30% through 2032..."
   → target_platforms: ["nei_blog", "clawbr"]

5. PUT /api/tasks/TASK_1 → {"status": "done"}

6. POST /api/drafts/DRAFT_1/publish
   → Published to nei_blog + clawbr in one call

7. Move to next task, repeat
```

---

## What NOT to Do

- **Don't post directly to platform APIs** — always go through the pipeline
- **Don't skip the draft step** — even if you're going to publish immediately, create the draft first so there's a record
- **Don't create tasks without a goal** — every task should link to a goal
- **Don't publish rejected drafts** — if a draft is rejected, create a new one
- **Don't ignore analytics** — check what's working and adjust your approach
