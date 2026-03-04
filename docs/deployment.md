# Deployment Guide

This guide covers the deployment of AI CMS to staging and production environments using Coolify.

## 🚀 Staging Deployment (Coolify)

The staging environment is hosted on Hetzner and managed by Coolify.

### Domain Information
- **Main Domain**: `aicms.docmet.systems`
- **User Sites**: `*.aicms.docmet.systems`

### Prerequisites
- Coolify instance access
- GitHub repository access
- `COOLIFY_WEBHOOK_URL` secret configured in GitHub Actions
- `COOLIFY_TOKEN` secret configured in GitHub Actions

### Automatic Deployment
Pushing to the `main` branch automatically triggers a deployment to staging via GitHub Actions after all tests pass.

### Manual Deployment via Coolify
1. Log in to your Coolify dashboard.
2. Navigate to the AI CMS project.
3. Click "Deploy" on the relevant service (frontend or backend).

## 🌍 Production Deployment (Future)

Production will follow a similar pattern but with a dedicated `production` branch and custom domain support.

### Custom Domains
Users will eventually be able to point their own domains to their sites. This will require:
1. CNAME record pointing to our load balancer.
2. Backend update to store and verify custom domains.
3. Dynamic SSL certificate generation (Coolify/Traefik handles this automatically).

## 🔧 Infrastructure Configuration

### Environment Variables
Ensure the following variables are set in the Coolify environment settings:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `POSTGRES_PASSWORD` | Database password |
| `JWT_SECRET` | Secret key for JWT (generate with `openssl rand -hex 32`) |
| `FRONTEND_URL` | Public URL of the frontend |
| `BACKEND_URL` | Public URL of the backend API |
| `DOMAIN` | Main domain (e.g., `aicms.docmet.systems`) |

### Docker Configuration
Coolify uses the root `docker-compose.yml` for deployment. Ensure this file is always up to date with the latest service requirements.
