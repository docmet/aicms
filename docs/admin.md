# Admin Guide

This document covers the admin panel features available to platform administrators.

---

## Admin Access

Any user with `is_admin = true` in the database has admin access.
Admin users can also use the platform as regular users — they see the same dashboard
as any other user, plus an additional **Admin** section in the sidebar.

**Admin panel URL:** `/dashboard/admin`
**Visibility:** Only shown to users where `is_admin = true`

---

## User Management

### User List

View all registered users at `/dashboard/admin/users`.

Columns: Email, Tier (Free/Pro), Sites count, Last active, Status (Active/Suspended)

Available actions:
- **Search** by email or name
- **Change tier:** Free ↔ Pro (toggles paid features)
- **Suspend / Unsuspend:** Prevents login and hides all their sites from public
- **Delete user:** Hard delete of user + all their sites, pages, content (with confirmation dialog)

### User Details

Click any user to see:
- Email, created date, last login
- List of their sites (name, slug, published status)
- MCP clients connected

---

## Site Management

View all sites across all users at `/dashboard/admin/sites`.

Columns: Site name, Slug, Owner email, Pages count, Status

Available actions:
- **View site:** Opens the public URL
- **Suspend site:** Makes site invisible to public (sets `is_suspended = true` on site)
- **View as owner:** Impersonate the site owner (see Impersonation below)

---

## User Impersonation (Support Mode)

Impersonation allows an admin to log in as another user to see exactly what they see.
Use this for debugging issues or providing support.

### How to Impersonate

1. Go to Admin → Users
2. Find the user
3. Click **"View as user"** button
4. A confirmation modal shows: "You are about to view the platform as [email]. This will be logged."
5. Click Confirm
6. The admin is redirected to the dashboard as that user
7. A **red banner** appears at the top: "Support mode: viewing as [email] | Exit"

### Impersonation Rules

- Impersonation tokens expire after **1 hour**
- Every impersonation session is logged in the `audit_log` table
- The impersonated user is NOT notified
- Admin can only exit by clicking "Exit" in the banner or waiting for expiry
- Impersonated sessions cannot create new impersonation sessions

### Audit Log Entry

Each impersonation creates an entry:
```json
{
  "actor_id": "<admin_user_id>",
  "target_user_id": "<impersonated_user_id>",
  "action": "impersonate",
  "metadata": {
    "started_at": "2026-03-05T10:30:00Z",
    "duration_seconds": 423,
    "ended_by": "admin_exit"
  }
}
```

---

## Platform Stats

Dashboard showing at `/dashboard/admin`:
- Total users (all time, last 7 days, last 30 days)
- Active sites (published at least once)
- Total published pages
- MCP clients connected
- New signups chart (last 30 days)

---

## Admin API Endpoints

All admin endpoints require `is_admin = true` and valid JWT.

```
GET    /api/v1/admin/users              List all users (paginated)
PATCH  /api/v1/admin/users/{id}         Update user (tier, is_suspended)
DELETE /api/v1/admin/users/{id}         Delete user + all data
GET    /api/v1/admin/sites              List all sites
PATCH  /api/v1/admin/sites/{id}         Update site (is_suspended)
POST   /api/v1/admin/impersonate/{id}   Start impersonation session
DELETE /api/v1/admin/impersonate        End impersonation session
GET    /api/v1/admin/stats              Platform stats
GET    /api/v1/admin/audit-log          View audit log (paginated)
```

---

## Security Notes

- Admin endpoints are protected at the route level — middleware checks `is_admin` flag
- Admin actions are logged in the audit table with actor, target, action, timestamp
- Impersonation tokens are short-lived (1 hour) and stored in the database
- Admin users cannot delete themselves or remove their own admin status
- Bulk delete operations require explicit confirmation (not undoable)

---

## Database Models

### User additions
```python
class User(Base):
    is_admin: bool = False      # existing
    is_suspended: bool = False  # new: prevents login
    tier: str = "free"          # new: "free" or "pro"
    last_login_at: datetime     # new: for activity tracking
```

### AuditLog model (new)
```python
class AuditLog(Base):
    id: UUID
    actor_id: UUID              # admin who performed action
    target_user_id: UUID        # affected user (nullable)
    target_site_id: UUID        # affected site (nullable)
    action: str                 # "impersonate", "suspend", "delete", etc.
    metadata: JSON              # action-specific details
    created_at: datetime
```

---

## Future Admin Features

- **Bulk email:** Send announcements to all users or filtered segments
- **Feature flags:** Enable/disable features per user or globally (e.g., "beta_features")
- **Custom domain approval:** Review and approve custom domain requests
- **Revenue dashboard:** Stripe subscription overview, MRR, churn
- **Content moderation:** Flag sites with potential ToS violations for review
- **Multiple admin roles:**
  - `super_admin`: Full access including deleting users
  - `support`: View-only + impersonation, no destructive actions
  - `billing_admin`: Tier management and Stripe access only
