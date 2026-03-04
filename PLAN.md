# MCP CMS MVP Plan

Create a modern website engine with user registration, simple landing pages with switchable TailwindCSS themes, and content editing available through a web admin UI, with MCP server integration for AI tools in a future phase.

## Dev Stack (Based on Recent Projects)

### Infrastructure
- **Docker containers** with docker-compose.yml for local development
- **cli.sh tool** for all development operations (lint, test, typecheck, etc.)
- **GitHub Actions** for CI/CD with Coolify webhook integration
- **Coolify/Hetzner deployment** (following gizike, reseller patterns)

### Frontend
- **Next.js 15+** with App Router (latest stable)
- **pnpm** for package management
- **TypeScript** with strict mode
- **TailwindCSS** for styling
- **shadcn/ui** for UI components

### Backend
- **Python 3.13+** with FastAPI
- **uv** for package management
- **PostgreSQL** database with async driver
- **SQLAlchemy** (async) for ORM

### Development Tools
- **Git hooks** (.githooks/) for pre-commit checks
- **Conventional commits** with scopes (frontend, backend, mcp, infra, etc.)
- **ESLint** + **Prettier** for frontend
- **ruff** + **black** + **isort** for backend
- **pytest** for backend tests
- **Vitest** for frontend tests

## Project Structure

```
mcp_cms/
├── cli.sh                    # Main development CLI
├── docker-compose.yml        # Production compose
├── docker-compose.dev.yml    # Development compose with volumes
├── env.example              # Environment template
├── .env                     # Local environment (gitignored)
├── .githooks/               # Git hooks
│   └── pre-commit          # Format, lint, test
├── frontend/                # Next.js frontend
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   │   ├── (public)/   # Public pages
│   │   │   │   ├── login/  # Login page
│   │   │   │   ├── register/
│   │   │   │   └── page.tsx # Landing
│   │   │   ├── (dashboard)/ # Protected admin
│   │   │   │   └── dashboard/
│   │   │   │       ├── layout.tsx
│   │   │   │       └── page.tsx
│   │   │   └── [site_slug]/ # Public site routing
│   │   │       └── page.tsx
│   │   ├── components/     # React components
│   │   │   ├── ui/        # shadcn/ui components
│   │   │   └── admin/     # Admin components
│   │   ├── lib/           # Utilities
│   │   └── styles/        # Global styles + theme variants
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   └── Dockerfile
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── main.py        # FastAPI app
│   │   ├── config.py      # Settings
│   │   ├── database.py    # SQLAlchemy setup
│   │   ├── models/        # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── site.py
│   │   │   ├── page.py
│   │   │   └── content.py
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── api/           # API routes
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── sites.py
│   │   │   ├── pages.py
│   │   │   └── content.py
│   │   ├── services/      # Business logic
│   │   │   ├── auth.py
│   │   │   └── theme.py
│   │   └── tests/
│   │       ├── unit/
│   │       └── integration/
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── seeds/
│       └── seed.py
├── .github/
│   └── workflows/
│       └── deploy.yml     # CI/CD + Coolify webhook
└── README.md
```

## MVP Features (Phase 1)

### 1. User Management
- User registration (email, password)
- User authentication (JWT tokens)
- Simple user profile
- Multi-tenant: Each user manages their own sites only

### 2. Website Engine
- Each user can create one website with a single landing page
- Simple landing page with predefined sections
- Switchable themes (3-5 simple TailwindCSS variants)
- Content sections: Hero, About, Services, Contact
- Each section: Plain text input with HTML stripping

### 3. Content Management (Web Admin Only)
- Simple admin dashboard
- Edit site name and slug
- Select theme from dropdown
- Edit content for each section (plain text)
- Save/publish changes

### 4. Public Site
- Local development: Access via `/[site_slug]`
- Staging: Access via `[site_slug].aicms.docmet.systems`
- Production: Support custom domains (future)
- Theme-based rendering using TailwindCSS
- Responsive design
- SEO-friendly

## Database Schema (SQLAlchemy)

```python
# User
- id: UUID (PK)
- email: String (unique, indexed)
- password_hash: String
- is_admin: Boolean (default: False)
- created_at: DateTime
- updated_at: DateTime

# Site
- id: UUID (PK)
- user_id: UUID (FK, indexed)
- slug: String (unique, indexed)
- name: String
- domain: String (nullable, for custom domains)
- theme_slug: String (default: "default")
- created_at: DateTime
- updated_at: DateTime

# Page
- id: UUID (PK)
- site_id: UUID (FK)
- title: String
- slug: String (unique per site)
- is_published: Boolean
- order: Integer
- created_at: DateTime
- updated_at: DateTime

# ContentSection
- id: UUID (PK)
- page_id: UUID (FK)
- section_type: String (hero, about, services, contact)
- content: Text (plain text, HTML-stripped)
- order: Integer
- created_at: DateTime
- updated_at: DateTime

# Theme
- id: UUID (PK)
- name: String
- slug: String (unique)
- config: JSON (TailwindCSS theme config)
- is_active: Boolean
```

## Theme System (MVP)

Simple TailwindCSS theme variants:
- **default**: Blue/gray color scheme
- **warm**: Orange/warm gray scheme
- **nature**: Green/earth tones
- **dark**: Dark mode theme
- **minimal**: Black/white minimal

Implementation: CSS variables + TailwindCSS config
- Each theme defines color palette
- Apply via `data-theme` attribute on `<html>` tag
- TailwindCSS uses CSS variables for colors

## Content Management (MVP)

### Content Sections
Each page has sections:
- **Hero**: Headline, subheadline, CTA button text
- **About**: Title, body text (plain text)
- **Services**: Title, list of services (name + description)
- **Contact**: Title, email, phone, address

### Content Security
- HTML stripping on all user inputs
- XSS prevention
- CSRF protection on all forms
- Input validation with Pydantic

## Seed Data

### Users
- Admin user: `norbi@docmet.com` / `password123`
- Client user: `client@docmet.com` / `password123`

### Themes
- default, warm, nature, dark, minimal (all active)

### Demo Content
- Client user gets a demo site with sample content

## Deployment Strategy

### Local Development
- Docker Compose with local networking
- Access sites via `localhost:3000/[site_slug]`
- No domain configuration needed

### Staging (MVP)
- Domain: `aicms.docmet.systems`
- Wildcard subdomain: `*.aicms.docmet.systems`
- Access sites via `[site_slug].aicms.docmet.systems`
- Deployed via Coolify on Hetzner

### Production (Future)
- Custom domains for user sites
- Domain management UI
- SSL certificate automation
- CDN integration

## Implementation Plan

### Phase 1: Foundation
1. Set up project structure
2. Create cli.sh with all commands
3. Set up Docker Compose (dev + prod)
4. Configure Git hooks
5. Set up GitHub Actions CI/CD
6. Create SQLAlchemy models and migrations (Alembic)
7. Create seed data script

### Phase 2: Backend
1. Implement FastAPI app structure
2. Implement JWT authentication
3. Create user API endpoints (register, login, profile)
4. Create site API endpoints (CRUD, scoped to user)
5. Create page API endpoints (CRUD, scoped to site)
6. Create content section API endpoints (CRUD, scoped to page)
7. Implement theme service
8. Add comprehensive tests

### Phase 3: Frontend
1. Set up Next.js with App Router
2. Implement authentication (login/register pages)
3. Create admin dashboard layout with shadcn/ui
4. Implement site editor (name, slug, theme selector)
5. Implement page editor (content sections)
6. Implement theme switcher (preview)
7. Create public site rendering (dynamic route [site_slug])
8. Add TailwindCSS theme variants

### Phase 4: Integration & Testing
1. Connect frontend to backend API
2. Test multi-user isolation (user A can't access user B's data)
3. Test theme switching
4. Test content security (HTML stripping)
5. Test seed data
6. Add E2E tests
7. Local Docker stack testing

### Phase 5: Deployment (Staging)
1. Configure Coolify deployment
2. Set up DNS for aicms.docmet.systems
3. Configure wildcard subdomain *.aicms.docmet.systems
4. Deploy to staging
5. Test staging deployment

### Phase 6: MCP Server (Future)
1. Implement FastAPI-based MCP server
2. Create MCP tools for all CMS operations
3. Add stdio adapter for Claude Desktop
4. Test with ChatGPT, Claude, Cursor

## Future Roadmap (Post-MVP)

### Phase 7: Advanced Features
- Blog system with rich text editor
- Image upload and management
- Custom domain support
- SEO optimization tools
- Analytics dashboard

### Phase 8: Multilanguage
- Content translations
- AI-powered translation via MCP
- Language switcher
- Multi-language SEO

### Phase 9: AI Image Generation
- Generate headline images
- Design elements generation
- Integration with DALL-E, Midjourney
- MCP tools for image generation

### Phase 10: Admin Enhancements
- Admin dashboard for platform owner
- User management (view, suspend, delete)
- Site management and monitoring
- Usage analytics and billing

### Phase 11: Advanced Themes
- Theme builder (visual editor)
- Custom CSS support
- Component library
- Theme marketplace

## Skills to Create

Based on this project, create reusable skills:

1. **faststack-init** - Initialize fullstack project with cli.sh, Docker, etc.
2. **sqlalchemy-fastapi** - Set up FastAPI with SQLAlchemy async
3. **nextjs-admin-dashboard** - Create admin dashboards with shadcn/ui
4. **coolify-deployment** - Configure Coolify deployment with GitHub Actions
5. **conventional-commits-workflow** - Set up conventional commits with scopes
6. **mcp-server-builder** - Build MCP servers with tools, resources (future)

## Commit Convention

Use conventional commits with scopes:
- `feat(frontend): add login page`
- `feat(backend): implement user registration`
- `feat(backend): add site CRUD endpoints`
- `fix(backend): resolve auth token issue`
- `refactor(frontend): simplify theme switcher`
- `test(backend): add integration tests`
- `docs(readme): update deployment instructions`
- `chore(infra): update Docker images`
- `style(frontend): format code with prettier`
- `perf(backend): optimize database queries`

## Security Considerations

### Multi-User Isolation
- All queries scoped to authenticated user
- Row-level security in database (optional)
- Validate ownership on all operations
- No direct object ID access without ownership check

### Content Security
- HTML stripping on all user inputs
- XSS prevention
- CSRF tokens on all forms
- Rate limiting on API endpoints
- Input validation with Pydantic

### Authentication
- JWT tokens with short expiration
- Refresh token rotation
- Secure password hashing (bcrypt)
- HTTP-only cookies for tokens (optional)

## Next Steps

1. Review and approve this plan
2. Start Phase 1 implementation
3. Create reusable skills as we build
