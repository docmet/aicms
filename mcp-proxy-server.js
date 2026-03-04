#!/usr/bin/env node

const http = require('http');
const { spawn } = require('child_process');

// Configuration from environment
const API_URL = process.env.API_URL || 'http://localhost/api';
const AUTH_TOKEN = process.env.AUTH_TOKEN;
const PORT = process.env.PORT || 3001;

if (!AUTH_TOKEN) {
  console.error('AUTH_TOKEN environment variable is required');
  process.exit(1);
}

// MCP Server implementation
class MCPServer {
  constructor() {
    this.tools = [
      {
        name: 'list_sites',
        description: 'List all sites you have access to',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'get_site',
        description: 'Get site details including theme',
        inputSchema: {
          type: 'object',
          properties: {
            site_id: { type: 'string', description: 'Site ID' }
          },
          required: ['site_id']
        }
      },
      {
        name: 'update_theme',
        description: 'Change site theme',
        inputSchema: {
          type: 'object',
          properties: {
            site_id: { type: 'string', description: 'Site ID' },
            theme: { type: 'string', description: 'Theme name' }
          },
          required: ['site_id', 'theme']
        }
      },
      {
        name: 'get_content',
        description: 'Get page content',
        inputSchema: {
          type: 'object',
          properties: {
            site_id: { type: 'string', description: 'Site ID' },
            page_slug: { type: 'string', description: 'Page slug' }
          },
          required: ['site_id', 'page_slug']
        }
      },
      {
        name: 'update_content',
        description: 'Update page content',
        inputSchema: {
          type: 'object',
          properties: {
            site_id: { type: 'string', description: 'Site ID' },
            page_slug: { type: 'string', description: 'Page slug' },
            content: { type: 'string', description: 'Page content' }
          },
          required: ['site_id', 'page_slug', 'content']
        }
      },
      {
        name: 'list_themes',
        description: 'List available themes',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      }
    ];
  }

  async makeRequest(path, method = 'GET', data = null) {
    const url = `${API_URL}${path}`;
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AUTH_TOKEN}`
      }
    };

    return new Promise((resolve, reject) => {
      const req = http.request(url, options, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(body);
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(json);
            } else {
              reject(new Error(json.detail || `HTTP ${res.statusCode}`));
            }
          } catch (e) {
            reject(new Error(`Invalid response: ${body}`));
          }
        });
      });

      req.on('error', reject);
      if (data) {
        req.write(JSON.stringify(data));
      }
      req.end();
    });
  }

  async handleListTools() {
    return {
      tools: this.tools
    };
  }

  async handleCallTool(name, args) {
    try {
      switch (name) {
        case 'list_sites':
          const sites = await this.makeRequest('/sites/');
          return {
            content: [{
              type: 'text',
              text: JSON.stringify(sites, null, 2)
            }]
          };

        case 'get_site':
          const site = await this.makeRequest(`/sites/${args.site_id}`);
          return {
            content: [{
              type: 'text',
              text: JSON.stringify(site, null, 2)
            }]
          };

        case 'update_theme':
          await this.makeRequest(`/sites/${args.site_id}`, 'PATCH', { theme: args.theme });
          return {
            content: [{
              type: 'text',
              text: `Theme updated to ${args.theme}`
            }]
          };

        case 'get_content':
          const content = await this.makeRequest(`/sites/${args.site_id}/pages/${args.page_slug}`);
          return {
            content: [{
              type: 'text',
              text: JSON.stringify(content, null, 2)
            }]
          };

        case 'update_content':
          await this.makeRequest(`/sites/${args.site_id}/pages/${args.page_slug}`, 'PUT', { content: args.content });
          return {
            content: [{
              type: 'text',
              text: 'Content updated successfully'
            }]
          };

        case 'list_themes':
          const themes = await this.makeRequest('/themes/');
          return {
            content: [{
              type: 'text',
              text: JSON.stringify(themes, null, 2)
            }]
          };

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Error: ${error.message}`
        }],
        isError: true
      };
    }
  }
}

// HTTP Server for MCP
const server = http.createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.method !== 'POST' || req.url !== '/mcp') {
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));
    return;
  }

  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', async () => {
    try {
      const request = JSON.parse(body);
      const mcpServer = new MCPServer();
      let response;

      switch (request.method) {
        case 'initialize':
          response = {
            jsonrpc: '2.0',
            id: request.id,
            result: {
              protocolVersion: '2025-11-25',
              capabilities: {
                tools: {}
              },
              serverInfo: {
                name: 'aicms-mcp',
                version: '1.0.0'
              }
            }
          };
          break;

        case 'tools/list':
          const tools = await mcpServer.handleListTools();
          response = {
            jsonrpc: '2.0',
            id: request.id,
            result: tools
          };
          break;

        case 'tools/call':
          const result = await mcpServer.handleCallTool(request.params.name, request.params.arguments);
          response = {
            jsonrpc: '2.0',
            id: request.id,
            result
          };
          break;

        default:
          response = {
            jsonrpc: '2.0',
            id: request.id,
            error: { code: -32601, message: 'Method not found' }
          };
      }

      res.writeHead(200);
      res.end(JSON.stringify(response));
    } catch (error) {
      console.error('Error:', error);
      res.writeHead(500);
      res.end(JSON.stringify({ error: error.message }));
    }
  });
});

server.listen(PORT, () => {
  console.log(`MCP Server listening on port ${PORT}`);
  console.log(`API URL: ${API_URL}`);
});
