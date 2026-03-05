# Test MCP Tools

Run a complete smoke test of all MCP tools using the seed client credentials.

Steps:
1. Get a JWT token:
   ```
   curl -s -X POST http://localhost/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=client@docmet.com&password=password123"
   ```
   Extract `access_token` from response.

2. Register a test MCP client:
   ```
   curl -s -X POST http://localhost/api/mcp/register \
     -H "Authorization: Bearer {JWT_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"name":"CLI Test","tool_type":"custom"}'
   ```
   Extract `token` from response.

3. Test each tool via the MCP server at `http://localhost:8001`:
   - `list_sites` — should return sites for client@docmet.com
   - `describe_site` with the first site's ID — should return narrative
   - `list_themes` — should return 5 themes
   - `get_versions` with a page ID — should return version list

4. Report: which tools worked (green checkmark), which failed (with error details).

If MCP server is unreachable, check `./cli.sh logs` for mcp_server container errors.
