# AI Platform MCP Integration Research

**Researched:** 2026-03-06
**Domain:** MCP protocol compatibility across AI assistant platforms
**Confidence:** MEDIUM-HIGH (ChatGPT: HIGH, Perplexity: MEDIUM, Rube: HIGH)

---

## Summary (3-line TL;DR)

ChatGPT fully supports MCP with OAuth 2.1 + DCR — our existing server is ~90% compatible, needing only PKCE verification and one scope tweak. Perplexity supports remote MCP for Pro/Max users with OAuth 2.0 and auto-discovers our `.well-known` endpoints, requiring near-zero backend changes. Rube is an MCP SERVER (not a client) that connects AI tools to 500+ pre-built apps — it cannot connect TO our MCP server, making it irrelevant to this integration goal.

---

## ChatGPT

### Protocol Support

**Verdict: Full native MCP support (in beta, rolling out)**

- Transport: Streamable HTTP (recommended) and SSE (both supported). Our `/mcp` HTTP streaming endpoint is compatible.
- Auth: OAuth 2.1 with authorization-code + PKCE (S256 required). Uses DCR (RFC 7591) to self-register.
- Availability: Developer Mode required to add custom connectors. Available on **Plus, Pro, Business, Enterprise, Education** plans — NOT free tier.
- Surface: Web app (ChatGPT.com) and (announced, coming) desktop app.

**How ChatGPT's OAuth flow works (verified against official docs):**

1. ChatGPT fetches `GET /.well-known/oauth-protected-resource` to find your auth server.
2. ChatGPT self-registers via `POST /oauth/register` (DCR, RFC 7591) and gets a `client_id`.
3. On first tool invocation, launches Authorization Code + PKCE flow (redirect to your `/authorize`).
4. Exchanges code at `POST /token`.
5. Attaches Bearer token to all subsequent MCP requests.

**Critical requirement:** Your `/.well-known/oauth-authorization-server` discovery metadata MUST include `"code_challenge_methods_supported": ["S256"]`. If absent, ChatGPT refuses to proceed. Our server already advertises `["S256", "plain"]` — this is satisfied.

**Scope gotcha:** ChatGPT requests specific scopes including `openid`, `email`, `profile`, `offline_access`, `model.request`, `model.read`, `organization.read`, `organization.write` in addition to your custom scopes. Our server currently only declares `mcp` scope — this needs verification of whether ChatGPT hard-fails on unrecognized scopes or gracefully accepts what's available.

**Publishing path:** Individual users can add custom connectors in Developer Mode for personal use. Organization-wide publishing (so all MyStorey users see a "Connect to ChatGPT" button) requires Business/Enterprise admin publishing — not self-service by end users.

### Integration Path

Our existing server already has:
- `/.well-known/oauth-authorization-server` with `code_challenge_methods_supported: ["S256", "plain"]` ✓
- `/.well-known/oauth-protected-resource` ✓
- `POST /oauth/register` (DCR) that echoes back `redirect_uris` ✓
- `GET /authorize` that passes `code_challenge` and `code_challenge_method` through ✓
- `POST /token` endpoint ✓
- Streamable HTTP at `/mcp` ✓

**Gaps to close:**

1. **PKCE S256 verification in token endpoint** — Currently the token endpoint forwards the code to the backend but it is unclear whether it validates the `code_verifier` against the stored `code_challenge`. If the backend consent flow doesn't verify, ChatGPT's tokens could succeed without actual PKCE enforcement (a security hole) or fail if ChatGPT validates server-side. Needs code audit.

2. **Scope handling** — Test whether ChatGPT hard-fails when requesting `openid`/`profile`/`offline_access` scopes that our server doesn't explicitly support. May need to add these as accepted (no-op) scopes to the auth server metadata.

3. **`client_secret_expires_at` in DCR response** — Our `/oauth/register` does not return this field. Without it, ChatGPT/MCP clients will cache the `client_id` indefinitely (correct behavior per MCP spec — do NOT add expiry unless you want re-registration).

4. **User-facing connector URL** — The "one-click connector" flow like Claude's `claude.ai/customize/connectors` equivalent for ChatGPT requires being listed on OpenAI's connector marketplace or providing users with the MCP URL to enter manually in Developer Mode. There is no ChatGPT equivalent of Claude's sharing URL yet for end users.

### Effort

**Small-Medium (1-3 days)**

- Day 1: Audit PKCE code_verifier validation in token exchange; add scope passthrough for OpenAI-requested scopes.
- Day 1-2: Test the actual ChatGPT connection manually in Developer Mode.
- Day 2-3: Build user-facing setup documentation or a guided setup page (since there's no one-click equivalent yet).

**Auth compatibility:** Our OAuth 2.0 + DCR is substantially compatible. The main question is PKCE enforcement completeness on the backend.

---

## Perplexity

### Protocol Support

**Verdict: Native MCP support (remote HTTP, Pro/Max subscribers only)**

- Transport: Streamable HTTP or SSE (both supported). Our `/mcp` endpoint is compatible.
- Auth: OAuth 2.0 supported. Perplexity auto-discovers `.well-known` endpoints. If DCR is supported, no Client ID/Secret is needed upfront. Alternatively supports API Key or no-auth.
- Availability: Available in the **web app, iOS, and Android** for **Pro, Max, and Enterprise Pro/Max** subscribers. Not available on free tier.
- Discovery: If your server has `/.well-known/oauth-authorization-server`, Perplexity auto-detects endpoints and scopes.

**How Perplexity's MCP connection works:**

1. User goes to Settings → Connectors → "+ Custom connector" → "Remote".
2. User enters MCP server URL (e.g., `https://mystorey.io/mcp`).
3. Selects auth type: None / API Key / OAuth 2.0.
4. If OAuth and server has `.well-known` discovery, endpoints are auto-populated.
5. User clicks through OAuth consent flow.
6. Connector is enabled and appears as a "Source" in the Perplexity chat UI.

**Key difference from ChatGPT:** Perplexity's OAuth implementation may not require PKCE (it's more lenient). It accepts a manually provided Client ID + Client Secret if DCR is not supported. This is actually EASIER to integrate than ChatGPT.

### Integration Path

Our existing server is ready. No backend changes needed for Perplexity.

**What exists and works:**
- HTTPS `/mcp` endpoint ✓
- `/.well-known/oauth-authorization-server` ✓
- `/.well-known/oauth-protected-resource` ✓
- DCR at `/oauth/register` ✓
- Standard OAuth authorization code flow ✓

**Only needed:**
1. **Documentation / setup guide** for MyStorey users explaining how to add the connector in Perplexity settings.
2. **Scope compatibility test** — verify Perplexity's OAuth client request works with our `mcp` scope.
3. **Optional:** Add a "Connect to Perplexity" button/page in the MyStorey dashboard with step-by-step instructions and the MCP URL pre-filled.

### Effort

**Small (hours to 1 day)**

- No backend changes required.
- Test the connection manually end-to-end.
- Write user documentation or build a guided setup page.

**Auth compatibility:** HIGH. Our existing OAuth + DCR is more than sufficient. Perplexity even supports manual Client ID/Secret as fallback.

---

## Rube

### What is Rube

Rube is a **Composio-built MCP SERVER** — not an MCP client or integration hub for external MCP servers.

It exposes 500+ pre-built app integrations (Gmail, Slack, Notion, GitHub, Linear, etc.) to AI assistants via the MCP protocol. AI tools (Claude Desktop, Cursor, VS Code) connect TO Rube. Rube does NOT connect to other MCP servers.

**In plain terms:** Rube = "an MCP server that lets your AI talk to Gmail, Slack, etc." It is a COMPETITOR to MCP servers like ours in the ecosystem, not a gateway or hub that could route to our server.

The query in the research request was likely referring to Rube as a potential "connector hub" that might let ChatGPT or Perplexity reach our MCP server. That is not what Rube does.

### Protocol Support

N/A — Rube IS an MCP server; it doesn't consume other MCP servers.

### Integration Path

**Not applicable.** Rube cannot connect TO our `/mcp` endpoint.

If the goal was "let MyStorey users automate things using Rube's 500+ apps FROM within MyStorey" — that would require us becoming a Rube CLIENT (adding MCP client support that calls Rube). That is a different product feature, not an AI platform integration.

### Effort

**N/A** — Wrong tool for this integration goal.

**Alternative:** If you want MyStorey to appear in Composio's ecosystem (which underlies Rube), you'd need to submit to Composio's app catalog — a different and longer-term path.

---

## Recommendation

### Priority Order with Rationale

**1. Perplexity — Do this first (hours)**

Near-zero backend work. Our server is already compatible. The only task is testing the connection and writing user documentation. Perplexity has a motivated, research-oriented user base that aligns with content creators who would use MyStorey. This is a quick win.

**2. ChatGPT — Do this second (1-3 days)**

The largest addressable market. ChatGPT's MCP integration requires some work (PKCE audit, scope handling, user flow design) but our server architecture is correct. The main risk is the user-facing flow — there's no "one-click connect" equivalent on ChatGPT yet, so users must manually enter the MCP URL in Developer Mode, which limits mainstream adoption. That said, getting it working now positions us well for when OpenAI ships a proper connector marketplace.

**3. Rube — Do not pursue**

Rube is architecturally incapable of connecting to our MCP server. It is a different kind of product. Skip entirely.

### What to Build First and Why

**Immediate (today/this week): Perplexity**

1. Manually test: add `https://[your-domain]/mcp` as a remote connector in Perplexity with OAuth 2.0.
2. Verify the full OAuth → tool invocation flow works end-to-end.
3. Add a "Connect to Perplexity" section to the MyStorey dashboard with:
   - Pre-filled MCP URL
   - Step-by-step screenshots
   - Auth type: OAuth 2.0

**Next (this sprint): ChatGPT audit**

1. Audit the `/token` endpoint: confirm `code_verifier` is validated against the stored `code_challenge` (PKCE enforcement).
2. Test ChatGPT Developer Mode → add custom connector → paste `/mcp` URL → walk through OAuth flow.
3. Observe what scopes ChatGPT requests; add them as accepted scopes in the discovery metadata if the flow fails.
4. Build user setup documentation for ChatGPT (manual Developer Mode steps).

**Later: ChatGPT publishing**

When OpenAI ships a proper connector marketplace or sharing mechanism (announced but not yet available as of March 2026), publish the MyStorey connector for one-click installation by end users.

---

## Sources

### Primary (HIGH confidence)
- [OpenAI Apps SDK — MCP Server Concepts](https://developers.openai.com/apps-sdk/concepts/mcp-server/) — transport, OAuth requirements
- [OpenAI Apps SDK — Authentication](https://developers.openai.com/apps-sdk/build/auth/) — DCR, PKCE S256 requirement, token flow
- [OpenAI Developer Community — DCR Discussion](https://community.openai.com/t/dynamic-client-registration-should-be-optional-for-custom-connectors/1356365) — DCR behavior details
- [OpenAI X/Twitter — MCP + Agents SDK announcement](https://x.com/OpenAIDevs/status/1904957755829481737) — ChatGPT desktop MCP confirmed coming
- [Rube GitHub README](https://github.com/W3JDev/Rube-smartest-connector) — confirmed Rube is an MCP server, not client

### Secondary (MEDIUM confidence)
- [Perplexity Help Center — Custom Remote Connectors](https://www.perplexity.ai/help-center/en/articles/13915507-adding-custom-remote-connectors) — transport, OAuth, plan availability
- [Perplexity Help Center — Local and Remote MCPs](https://www.perplexity.ai/help-center/en/articles/11502712-local-and-remote-mcps-for-perplexity) — plan availability (Pro/Max/Enterprise)
- [ChatGPT MCP Server Setup article (Medium, Feb 2026)](https://bhavyansh001.medium.com/chatgpt-mcp-server-setup-developer-mode-oauth-explained-mcp-deepdive-06-76b5a652a3ea) — practical setup walkthrough
- [InfoQ — OpenAI adds full MCP support to ChatGPT Developer Mode](https://www.infoq.com/news/2025/10/chat-gpt-mcp/) — confirmed rollout

### Tertiary (LOW confidence — needs validation)
- [WorkOS — DCR in MCP](https://workos.com/blog/dynamic-client-registration-dcr-mcp-oauth) — scope behavior details
- [MCP typescript-sdk issue #832](https://github.com/modelcontextprotocol/typescript-sdk/issues/832) — PKCE metadata validation strictness

---

## Metadata

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (ChatGPT MCP is actively evolving — recheck monthly)

**Confidence breakdown:**
- ChatGPT protocol support: HIGH — Multiple official OpenAI sources confirm MCP + OAuth 2.1 + DCR
- ChatGPT gap analysis: MEDIUM — Based on reading our source code + OAuth spec; PKCE enforcement audit requires hands-on testing
- Perplexity support: MEDIUM — Help center describes the feature but direct testing not done; feature confirmed as shipping
- Rube classification: HIGH — GitHub README is unambiguous; Rube is an MCP server, not a routing hub
