# Check Stack Health

Verify all AI CMS services are running and healthy.

Run these checks:

1. Run `./cli.sh verify` to confirm all required tools are installed
2. Run `docker compose -f docker-compose.dev.yml ps` to show service status
3. Check each service health:
   - Frontend: `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000`
   - Backend: `curl -s http://localhost:8000/health`
   - MCP Server: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8001`
   - Nginx: `curl -s -o /dev/null -w "%{http_code}" http://localhost`
4. If any service is unhealthy, show the last 20 lines of its logs with `./cli.sh logs`

Report: which services are healthy (green), which have issues (red), and suggest fixes if any are down.
