# AI Platform Integration Options

## Supported Platforms

### 1. Claude Desktop 🤖
- **Integration**: Native MCP support
- **Setup**: Settings → Developer → Add Server
- **Connection Type**: MCP Server
- **Status**: ✅ Fully supported

### 2. ChatGPT 💬
- **Integration**: MCP plugin or custom integration
- **Setup**: 
  - Option A: Use MCP plugin (if available)
  - Option B: Custom API integration
- **Connection Type**: MCP Server / API
- **Status**: ✅ Supported (requires plugin)

### 3. Cursor 👆
- **Integration**: Built-in MCP support
- **Setup**: Settings → MCP Servers → Add Server
- **Connection Type**: MCP Server
- **Status**: ✅ Fully supported

### 4. Perplexity 🔍
- **Integration**: API integration
- **Setup**: Settings → API Integrations → Add Custom
- **Connection Type**: REST API
- **Status**: ✅ Supported (API endpoint)

### 5. Custom Tools 🔧
- **Integration**: Any MCP-compatible tool
- **Setup**: Use provided server URL and token
- **Connection Type**: MCP Server
- **Status**: ✅ Flexible integration

## Connection Methods

### MCP Server (Recommended)
- **Platforms**: Claude, Cursor, ChatGPT (with plugin), Custom
- **Protocol**: HTTP + Server-Sent Events (SSE)
- **Authentication**: Token-based
- **Endpoint**: `/sse/{client_id}`

### REST API
- **Platforms**: Perplexity, Custom tools
- **Protocol**: HTTP REST
- **Authentication**: Bearer token
- **Endpoint**: `/api/mcp/{client_id}`

## Implementation Notes

1. **Single Server**: All platforms connect to the same MCP server
2. **Unique Tokens**: Each platform gets its own authentication token
3. **Automatic Generation**: Server URLs and tokens are generated automatically
4. **No Configuration**: Users just need to click "Connect" and copy parameters

## Future Expansions

Potential platforms to add:
- **GitHub Copilot** - MCP support in development
- **Replit AI** - Custom integration possible
- **Codeium** - API-based integration
- **Tabnine** - Plugin-based integration
- **Sourcegraph Cody** - MCP support planned

## Technical Architecture

```
AI CMS Frontend
    ↓
MCP Server (Single instance)
    ↓
Multiple AI Platforms
  ├─ Claude Desktop (MCP)
  ├─ ChatGPT (MCP/API)
  ├─ Cursor (MCP)
  ├─ Perplexity (API)
  └─ Custom Tools (MCP)
```
