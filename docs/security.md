# Security Guide

This document covers the security model, implemented protections, and future hardening plans.

---

## Core Security Principles

1. **Multi-tenant isolation:** Users can only access and modify their own data
2. **Public sites are read-only:** No authentication needed to view published sites
3. **Input is never trusted:** All user input is validated and sanitized before storage
4. **Secrets never leak:** Password hashes, tokens, and keys are never returned in API responses
5. **Defense in depth:** Multiple layers — validation, auth, ORM, Nginx headers

---

## Authentication

### JWT Tokens
- Algorithm: HS256
- Default expiry: 30 minutes
- Secret: configured via `JWT_SECRET_KEY` environment variable (must be strong in production)
- Tokens are sent as `Authorization: Bearer {token}` header
- **No password hashes are ever returned in any API response**

### Password Storage
- Passwords hashed with bcrypt (via passlib)
- Bcrypt work factor: 12 (configurable)
- Passwords never logged, never returned in responses, never stored in plain text

### MCP Client Tokens
- Each AI client connection gets a unique token
- Tokens are scoped to the owning user
- Tokens are revocable (delete MCP client → token invalidated)
- Token usage is logged (`last_used` field on MCPClient)
- Tokens expire (configurable, default: 90 days)

### Rate Limiting
- Auth endpoints (`/auth/login`, `/auth/register`) are rate limited
- Limits: 10 requests / minute per IP
- Implemented via Nginx `limit_req_zone` in production
- Returns `429 Too Many Requests` when exceeded

---

## Authorization (Multi-Tenant Isolation)

Every API endpoint that reads or modifies data must verify ownership:

```python
# Pattern used on all protected endpoints
site = await db.get(Site, site_id)
if not site or site.user_id != current_user.id:
    raise HTTPException(status_code=404)  # 404, not 403 (don't leak existence)
```

Rules:
- `GET /sites` only returns sites owned by the current user
- `GET /sites/{id}` returns 404 if site doesn't belong to current user
- MCP tools verify ownership at every step
- Admin users bypass ownership checks (`is_admin = true`)
- Public endpoints (`/public/sites/{slug}`) return only `content_published`, never `content_draft`

---

## Input Validation

### Backend (Pydantic)
- All API request bodies validated via Pydantic models
- String fields have `max_length` constraints
- No direct SQL — all queries use SQLAlchemy ORM (parameterized, injection-safe)
- Content stored as plain JSON strings (no HTML injection risk for structured content)
- `custom` section type content is plain text only (no HTML)

### Frontend (TypeScript + Zod)
- Form inputs validated before submission
- Zod schemas mirror backend Pydantic schemas
- No client-side rendering of raw user HTML (all content rendered through React components)

### HTML/Script Stripping
- Content stored via the API is passed through a sanitizer before storage
- Any `<script>`, `<iframe>`, `<object>`, event attributes are stripped
- Applies to all section content regardless of type
- Using `bleach` (Python) on the backend

---

## CORS Configuration

Development:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8001
```

Production:
```
CORS_ORIGINS=https://aicms.docmet.systems,https://*.aicms.docmet.systems
```

Unknown origins receive `403 Forbidden` for non-GET requests.

---

## Security Headers (Nginx)

Applied to all responses in production:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com; img-src 'self' data:;" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

---

## Environment Variables (Secrets)

Never commit secrets to git. Use environment variables for:

| Variable | Description | Notes |
|----------|-------------|-------|
| `JWT_SECRET_KEY` | JWT signing secret | Min 32 chars, random |
| `POSTGRES_PASSWORD` | Database password | Strong random password |
| `DATABASE_URL` | Full DB connection string | Includes password |
| `COOLIFY_TOKEN` | Deployment token | GitHub secret |
| `COOLIFY_WEBHOOK_URL` | Deploy webhook | GitHub secret |

The `.env` file is in `.gitignore`. Copy `env.example` to `.env` to get started.

---

## Public Site Security

Public sites at `[slug].aicms.docmet.systems`:
- Served via Next.js SSR — no client-side auth
- Only `content_published` is served (never draft)
- No API keys or user tokens in public HTML
- Static-like rendering: minimal JavaScript
- User-provided content rendered in React components (no `dangerouslySetInnerHTML`)
- Suspended sites return 404

---

## MCP Security

- Each MCP client has its own token (not the user's JWT)
- Tokens are specific to one AI client connection
- All MCP tool calls verify the token's user ownership
- Token revocation is immediate (delete client → token invalid)
- MCP server is behind Nginx which enforces HTTPS in production

---

## Checklist for New Endpoints

When adding any new authenticated endpoint:

- [ ] Requires `current_user: User = Depends(get_current_user)`
- [ ] Verifies resource ownership before returning or modifying data
- [ ] Returns 404 (not 403) when resource not found or not owned (don't leak existence)
- [ ] Input validated via Pydantic
- [ ] No password hashes or secrets in response
- [ ] Admin-only routes check `current_user.is_admin`

---

## Known Limitations (To Fix)

- [ ] Rate limiting is configured in Nginx but not yet tested end-to-end
- [ ] No refresh token rotation yet (JWT tokens must be manually refreshed)
- [ ] No CSRF protection on form submissions (mitigated by same-origin JWT bearer auth)
- [ ] MCP token expiry not enforced in all code paths

---

## Future Hardening

- **2FA:** TOTP-based two-factor authentication for admin users (and optional for all users)
- **Audit log:** Full log of all data-modifying actions (who changed what, when)
- **IP allowlist:** Restrict admin routes to known IPs in production
- **Penetration testing:** Formal security review before public launch
- **Security.txt:** `/.well-known/security.txt` with disclosure contact
- **Dependency audits:** Automated in CI (`npm audit`, `uv audit`)
- **Secrets scanning:** GitHub secret scanning enabled on repo
