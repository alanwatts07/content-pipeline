# Build Plan — Next Session

## 1. Kanban Dashboard UI
- Add `/dashboard` route to api.py that serves a single HTML page
- Inline CSS + JS, no build step, no framework
- 5 columns: Goals → Tasks → Drafts → Posted → Analytics
- Cards show title, status, platform badges, timestamps
- Cards are draggable between columns (updates status via API)
- Auto-refreshes every 30s
- Dark theme matching the other sites
- Mobile responsive

## 2. Wire Terrance to the Pipeline
- Update Terrance's session behavior to use the pipeline API instead of posting directly
- Flow: check /api/agent/status → create draft → publish via /api/drafts/:id/publish
- Pipeline handles multi-platform publishing (blog + Facebook in one call)
- Update his core memory with pipeline API instructions

## 3. Fix Facebook Token
- Regenerate token with `pages_manage_posts` permission
- Test posting via the facebook module
- Update .env in both content-pipeline and terrance

## 4. Analytics Cron
- Add cron job to refresh metrics every few hours
- POST /api/posts/refresh-analytics
- Store historical metrics so we can track trends

## 5. Issues to Create
- Create GitHub issues for each of the above as we build them
- Comment solutions as we go
- Clean commits, one per feature

## API is running
- Port 8100
- Swagger docs: http://localhost:8100/docs
- All 4 platform modules connected (facebook, clawbr, void_blog, nei_blog)
- Test data already in DB (1 goal, 1 task, 1 draft)
