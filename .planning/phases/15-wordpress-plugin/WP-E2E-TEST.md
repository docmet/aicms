# WordPress Plugin E2E Test Playbook

Phase 15 — WP-09 validation

## Prerequisites

- A running WordPress 6.x instance (local or remote). Local options: wp-env, LocalWP, or a staging site.
- MyStorey running locally (`./cli.sh start`) or pointed at staging.
- A MyStorey account (norbi@docmet.com / password123 for local dev).
- Claude.ai account OR ChatGPT Plus with GPT-4 (for Developer mode / Actions testing).

## Test Sequence

### 1. Plugin Installation

1. Run `cd wp-plugin && bash build.sh` to generate `mystorey-connector.zip`
2. In WordPress Admin → Plugins → Add New → Upload Plugin
3. Upload `mystorey-connector.zip` → Install → Activate
4. Expected: "MyStorey AI" appears under Settings menu
5. Go to Settings → MyStorey AI → verify 3-step instructions render correctly

### 2. Application Password Creation

1. In WordPress Admin → Users → Profile → scroll to Application Passwords
2. Name: `MyStorey` → click "Add New Application Password"
3. Copy the password (format: `XXXX XXXX XXXX XXXX XXXX XXXX`)
4. Expected: Password displayed once, then masked

### 3. MyStorey Site Registration

1. Go to `http://localhost:3000/dashboard/wordpress`
2. Enter:
   - WordPress Site URL: your WP site URL (e.g. `http://localhost:8080`)
   - Application Username: your WP admin username
   - Application Password: the password copied above
3. Click Register
4. Expected: Site card appears with MCP URL and MCP Token

### 4. Claude.ai Connection Test

1. Copy the MCP URL (`http://localhost:3000/mcp` or prod URL)
2. In Claude.ai → Settings → Integrations → Add MCP Server
3. Enter MCP URL, use MCP Token as the API key/token
4. Expected: Claude connects and lists WP tools including `wp_list_posts`, `wp_create_post`, etc.

**Tool smoke tests (in Claude chat):**
- "List my WordPress posts" → `wp_list_posts` called, returns post list or "no posts"
- "Create a draft blog post titled 'Hello from AI' with content 'This was written by Claude.'" → `wp_create_post` called, returns post id
- "Publish that post" → `wp_publish_post` called with the post id
- Verify in WP Admin → Posts → post is visible and published
- "Create a WordPress page called 'About' with content 'We are a team of...'" → `wp_create_page` called
- "What is my WordPress site info?" → `wp_get_site_info` returns site name and description

### 5. ChatGPT Connection Test

1. In ChatGPT → Explore GPTs → Create a GPT → Configure → Actions
2. Import OpenAPI schema from `http://localhost:3000/mcp` (or use the manual MCP URL approach if ChatGPT supports it in developer mode)
   Note: ChatGPT uses OpenAI Plugins / Actions format, not MCP directly. Test via ChatGPT's MCP support if available, or document that ChatGPT requires the OpenAI Actions approach (separate work if needed).
3. Expected: At minimum, MCP URL connection succeeds in ChatGPT Developer mode

### 6. Pass Criteria

All of the following must be true to mark WP-09 complete:

- [ ] Plugin zip installs without errors on WP 6.x
- [ ] Settings page renders all 3 steps correctly
- [ ] MyStorey registration form accepts URL + Application Password and creates a site
- [ ] `tools/list` via MCP returns all 10 WP tools
- [ ] `wp_create_post` creates a draft post visible in WP Admin
- [ ] `wp_publish_post` changes post status to published
- [ ] `wp_create_page` creates a draft page
- [ ] `wp_get_site_info` returns site name
- [ ] Claude.ai connection flow completes (MCP URL → token auth → tools list)
- [ ] ChatGPT connection flow completes (if MCP supported) OR documented as ChatGPT Actions approach required

## Known Limitations (v1.0)

- Plugin zip is ~5 KB (pure PHP, no build step needed)
- Application Password auth transmits credentials to MyStorey — add encryption at-rest in v1.1
- ChatGPT MCP support varies by account tier and region — test with Developer mode
