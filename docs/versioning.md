# Draft / Preview / Publish / Rollback

This document explains how the content versioning system works.

---

## Core Concept

Every page has two content states:

| State | Field | Who sees it | How it's updated |
|-------|-------|-------------|-----------------|
| **Draft** | `content_draft` | Nobody (only in preview) | Every save/AI edit |
| **Published** | `content_published` | Public visitors | Only on Publish action |

When a user or AI edits content, they're always editing the **draft**.
The public site always shows **published** content.
Nothing goes live until you explicitly publish.

---

## The Workflow

```
Edit (web or AI) → content_draft updated → real-time preview via SSE
                                                        ↓
                                              Click "Publish"
                                                        ↓
                             content_published ← content_draft
                             PageVersion snapshot created
                                                        ↓
                                              Public site updated
```

---

## Real-Time Preview (SSE)

When the admin editor is open, it connects to a Server-Sent Events stream:

```
GET /api/v1/pages/{page_id}/preview-stream
Authorization: Bearer {jwt_token}
```

Whenever `content_draft` is updated (by web editor or AI tool), the backend broadcasts
the new content to all connected preview clients. The preview pane re-renders instantly.

This means:
- You can watch your AI assistant build the page in real-time
- No polling, no manual refresh
- Sub-second latency from edit → preview update

The preview iframe in the admin shows your site with `?preview=true`, which serves
`content_draft` instead of `content_published`.

---

## Publishing

To make your changes live:

**Web editor:** Click the **Publish** button in the top right of the page editor.

**MCP tool (AI):**
```
publish_page(site_id="...", page_id="...")
```

**API:**
```
POST /api/v1/sites/{site_id}/pages/{page_id}/publish
Authorization: Bearer {jwt_token}
```

On publish:
1. `content_published` is set to the current `content_draft` for all sections
2. A `PageVersion` snapshot is created
3. `last_published_at` is updated on the page
4. Old snapshots beyond the limit (5) are deleted

---

## Version History

Every time you publish, a snapshot is saved as a `PageVersion`.

**The PageVersion stores:**
- Full JSON snapshot of all sections at that moment
- Timestamp (`published_at`)
- Who published it (`published_by` user ID)
- Optional label ("Before homepage redesign")

**Limits:**
- Free tier: stores 1 previous version (rollback to previous only)
- Pro tier: stores last 5 versions
- When the limit is reached, the oldest version is deleted on next publish

**View versions:**
- Web: Click "Version history" in the page editor sidebar
- MCP: `get_versions(site_id="...", page_id="...")`
- API: `GET /api/v1/sites/{site_id}/pages/{page_id}/versions`

---

## Rollback

To revert to a previous version:

**Web:** Open version history → click "Revert" next to any version.

**MCP:**
```
revert_to_version(site_id="...", page_id="...", version_id="...")
```

**API:**
```
POST /api/v1/sites/{site_id}/pages/{page_id}/revert/{version_id}
```

Rollback sets `content_draft` to the snapshot content.
**It does not auto-publish** — you still need to click Publish to make it live.
This lets you review the rolled-back content in preview before publishing.

---

## Indicators in the UI

- **"Unsaved changes"** dot: shown on sections where `content_draft != content_published`
- **"Unpublished changes"** badge: shown on the page if any draft differs from published
- **"Up to date"**: all drafts match published
- **"Never published"**: page has never been published (no public version yet)

---

## For AI Tools

When AI edits content via `update_page_content`, it always updates `content_draft`.
Visitors won't see changes until the page is published.

Typical AI workflow:
1. `describe_site` — get current content context
2. `update_page_content` — update draft sections
3. User previews in real-time via SSE in the browser
4. User clicks Publish (or AI calls `publish_page`)

AI can also publish directly with `publish_page` — useful for automated site builds.

---

## Technical Notes

### Database Schema

```sql
-- ContentSection
ALTER TABLE content_sections ADD COLUMN content_draft TEXT;
ALTER TABLE content_sections ADD COLUMN content_published TEXT;
-- content (old column) maps to content_draft during migration

-- Page
ALTER TABLE pages ADD COLUMN last_published_at TIMESTAMP;

-- New table
CREATE TABLE page_versions (
    id UUID PRIMARY KEY,
    page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    snapshot JSONB NOT NULL,  -- full page+sections state
    published_at TIMESTAMP NOT NULL DEFAULT NOW(),
    published_by UUID REFERENCES users(id),
    label VARCHAR(255),
    UNIQUE(page_id, version_number)
);
```

### SSE Implementation

Backend (FastAPI):
```python
@router.get("/pages/{page_id}/preview-stream")
async def preview_stream(page_id: str, current_user: User = Depends(get_current_user)):
    # Verify page ownership
    # Return EventSourceResponse that subscribes to page update events
    ...
```

Frontend (React):
```typescript
const eventSource = new EventSource(
  `/api/v1/pages/${pageId}/preview-stream?token=${jwt}`
);
eventSource.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Refresh preview iframe or update section in state
};
```

---

## Future Ideas

- **Scheduled publishing:** Set a future datetime to automatically publish
- **Shareable preview URLs:** Generate a token-protected URL to share draft preview (24hr expiry)
- **A/B testing:** Publish version A to 50% of visitors, version B to the other 50%
- **Site-level publish:** Publish all pages at once
- **Diff view:** Visual comparison between two versions
- **Version labels:** Allow users to name versions ("Holiday redesign", "Before A/B test")
