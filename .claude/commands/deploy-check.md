# Deployment Check

Check CI status and staging environment health.

Steps:

1. **Check CI status:**
   Run `gh run list --limit 5` to show recent GitHub Actions runs.
   Run `gh run view $(gh run list --limit 1 --json databaseId -q '.[0].databaseId')` for latest run details.

2. **Check staging health** (if deployed):
   - Frontend: `curl -s -o /dev/null -w "%{http_code}" https://aicms.docmet.systems`
   - Backend: `curl -s https://aicms.docmet.systems/api/health`
   - MCP server: `curl -s -o /dev/null -w "%{http_code}" https://aicms.docmet.systems/mcp`

3. **Check latest commits:**
   Run `git log --oneline -10` to show what's been merged to main.

4. **Report:**
   - CI: passing / failing / running
   - Staging: live / down / not deployed yet
   - Last deployed commit (if available)
   - Any failing steps with error summary

If CI is failing, suggest which step to investigate based on the error.
If staging is not live, note that Phase 6 (deployment) hasn't been completed yet.
