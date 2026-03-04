# AI CMS

A modern website engine with user registration, landing pages with switchable themes, content editing through web admin UI, and full MCP (Model Context Protocol) server integration for AI tools like Claude, ChatGPT, and Cursor.

## 🎯 Project Overview

AI CMS is a multi-tenant content management system that allows users to create and manage their own websites through both a web interface and AI assistants via MCP. Features include multiple pages per site, theme switching, content section management, and complete AI tool integration.

### Key Features

- ✅ User registration and authentication (JWT)
- ✅ Multi-tenant architecture (each user manages their own sites)
- ✅ Multiple pages per site with content sections
- ✅ 5 switchable TailwindCSS themes (default, warm, nature, dark, minimal)
- ✅ Content editing with section templates (hero, body, features, cta, footer)
- ✅ Web admin dashboard for site/page/content management
- ✅ Public site rendering with theme support
- ✅ **Full MCP server for AI tool integration** (Claude, ChatGPT, Cursor)
- ✅ **13 MCP tools for complete CMS control via AI**
- ✅ Instant save (Mac-style) across all fields

### MCP Tools Available

The MCP server exposes these tools to AI assistants:

**Site Management:**
- `list_sites` - List all your sites with UUIDs
- `create_site` - Create new site (name, slug, theme)
- `get_site_info` - Get site details including pages
- `update_site` - Update site name/slug/theme
- `delete_site` - Delete a site

**Page Management:**
- `list_pages` - List pages for a site
- `create_page` - Create new page (title, slug, published)
- `get_page_content` - Get content sections
- `update_page` - Update page metadata
- `delete_page` - Delete a page

**Content & Themes:**
- `update_page_content` - Add/update content sections (hero, body, features, cta, footer)
- `list_themes` - List available themes
- `apply_theme` - Change site theme

### Future Features

- 🔄 Blog system with rich text editor
- 🔄 Multilanguage support with AI translation
- 🔄 AI image generation
- 🔄 Custom domain support
- 🔄 Advanced analytics

## 🏗️ Tech Stack

### Frontend
- **Next.js 15+** with App Router
- **TypeScript** with strict mode
- **TailwindCSS** for styling
- **shadcn/ui** for UI components
- **pnpm** for package management

### Backend
- **Python 3.13+** with FastAPI
- **SQLAlchemy** (async) for ORM
- **PostgreSQL** database
- **JWT** for authentication
- **uv** for package management

### Infrastructure
- **Docker** containers
- **Docker Compose** for local development
- **GitHub Actions** for CI/CD
- **Coolify** for deployment on Hetzner
- **cli.sh** for development operations

## 📁 Project Structure

```
mcp_cms/
├── cli.sh                    # Main development CLI
├── docker-compose.yml        # Production compose
├── docker-compose.dev.yml    # Development compose
├── env.example              # Environment template
├── .env                     # Local environment (gitignored)
├── .githooks/               # Git hooks
│   └── pre-commit          # Format, lint, test
├── frontend/                # Next.js frontend
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/     # React components
│   │   ├── lib/           # Utilities
│   │   └── styles/        # Global styles
│   ├── package.json
│   └── Dockerfile
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── main.py        # FastAPI app
│   │   ├── config.py      # Settings
│   │   ├── database.py    # SQLAlchemy setup
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── api/           # API routes
│   │   ├── services/      # Business logic
│   │   └── tests/         # Tests
│   ├── pyproject.toml
│   └── Dockerfile
├── mcp_server/              # MCP server for AI tools
│   ├── src/
│   │   ├── main.py         # FastAPI with SSE transport
│   │   ├── aicms_mcp_server/
│   │   │   └── server.py   # MCP server implementation
│   │   └── models.py       # MCP client model
│   ├── pyproject.toml
│   └── Dockerfile
├── nginx/                   # Nginx reverse proxy config
├── .github/
│   └── workflows/
│       └── deploy.yml     # CI/CD + Coolify webhook
├── docs/                   # Documentation
├── README.md
└── ROADMAP.md
```

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 22+
- Python 3.13+
- pnpm
- uv

### Quick Start

1. Clone the repository:
```bash
git clone git@github.com:docmet/aicms.git
cd aicms
```

2. Initialize the environment:
```bash
./cli.sh init
```

3. Start the development stack:
```bash
./cli.sh start
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Dashboard: http://localhost:3000/dashboard
- Help/Setup: http://localhost:3000/dashboard/help

### Quick Start with MCP Server

1. Start the stack:
```bash
./cli.sh start
```

2. Go to AI Tools in dashboard: http://localhost:3000/dashboard/mcp

3. Register your AI tool (Claude, ChatGPT, or Cursor)

4. Copy the configuration and follow the setup instructions

The MCP server runs automatically at http://localhost:8001

### Development Commands

```bash
./cli.sh init          # Initialize environment
./cli.sh start         # Start all services
./cli.sh stop          # Stop all services
./cli.sh restart       # Restart services
./cli.sh lint          # Run linters
./cli.sh format        # Format code
./cli.sh test          # Run tests
./cli.sh typecheck     # Type check
./cli.sh db:migrate    # Run database migrations
./cli.sh db:seed       # Seed database
./cli.sh db:reset      # Reset database
./cli.sh verify        # Verify tools installed
./cli.sh clean         # Clean everything
./cli.sh mcp:install   # Install MCP server
./cli.sh mcp:run       # Run MCP server (requires token)
```

## 📚 Documentation

- [Implementation Plan](PLAN.md) - Detailed implementation plan
- [Roadmap](ROADMAP.md) - Future features and timeline
- [Development Guide](docs/development.md) - Development setup and workflows
- [API Documentation](docs/api.md) - Backend API reference
- [MCP Server Guide](mcp_server/README.md) - MCP server setup and usage
- [Deployment Guide](docs/deployment.md) - Deployment instructions

## 🔐 Seed Data

The application comes with seed data for testing:

### Users
- **Admin**: norbi@docmet.com / password123
- **Client**: client@docmet.com / password123

### Themes
- default (Blue/gray)
- warm (Orange/warm gray)
- nature (Green/earth tones)
- dark (Dark mode)
- minimal (Black/white)

## 🌐 Deployment

### Local Development
Access user sites via: `http://localhost:3000/[site_slug]`

### Staging
- Domain: aicms.docmet.systems
- User sites: [site_slug].aicms.docmet.systems
- Platform: Coolify on Hetzner

### Production (Future)
- Custom domains for user sites
- CDN integration
- Advanced monitoring

## 🤝 Contributing

This project uses conventional commits with scopes:

- `feat(frontend): add login page`
- `feat(backend): implement user registration`
- `fix(backend): resolve auth token issue`
- `refactor(frontend): simplify theme switcher`
- `test(backend): add integration tests`
- `docs(readme): update deployment instructions`
- `chore(infra): update Docker images`

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built following the established patterns from:
- gizike project (cli.sh, Docker, Coolify)
- reseller project (Next.js + FastAPI architecture)
- bkk-mcp-server (MCP server patterns)

## 📞 Contact

- Project: https://github.com/docmet/aicms
- Issues: https://github.com/docmet/aicms/issues
