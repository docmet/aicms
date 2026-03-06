'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Copy, Check, Plus, Settings } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useState } from 'react';

interface AIToolsConnectProps {
  clients: Array<{
    id: string;
    name: string;
    tool_type: string;
    token: string;
  }>;
  onCreateClient: (toolType: string) => void;
}

interface AIPlatform {
  id: string;
  name: string;
  icon: string;
  description: string;
  connectionType: 'mcp' | 'api' | 'oauth';
  configTemplate?: Record<string, string>;
}

const AI_PLATFORMS: AIPlatform[] = [
  {
    id: 'claude',
    name: 'Claude Desktop',
    icon: '🤖',
    description: 'Native MCP support - just copy the server URL',
    connectionType: 'mcp',
    configTemplate: {
      'Server URL': 'auto',
      'Authorization Token': 'auto',
    }
  },
  {
    id: 'chatgpt',
    name: 'ChatGPT',
    icon: '💬',
    description: 'Connect via MCP server or custom plugin',
    connectionType: 'mcp',
    configTemplate: {
      'Server URL': 'auto',
      'Authorization Token': 'auto',
    }
  },
  {
    id: 'cursor',
    name: 'Cursor',
    icon: '📝',
    description: 'Built-in MCP support',
    connectionType: 'mcp',
    configTemplate: {
      'Server URL': 'auto',
      'Authorization Token': 'auto',
    }
  },
  {
    id: 'perplexity',
    name: 'Perplexity',
    icon: '🔍',
    description: 'API integration available',
    connectionType: 'api',
    configTemplate: {
      'API Endpoint': 'auto',
      'API Key': 'auto',
    }
  },
  {
    id: 'custom',
    name: 'Custom Tool',
    icon: '🔧',
    description: 'For other AI tools with MCP support',
    connectionType: 'mcp',
    configTemplate: {
      'Server URL': 'auto',
      'Authorization Token': 'auto',
    }
  }
];

export function AIToolsConnect({ clients, onCreateClient }: AIToolsConnectProps) {
  const { toast } = useToast();
  const [copied, setCopied] = useState<string | null>(null);

  const getClient = (platformId: string) => 
    clients.find(c => c.tool_type === platformId);

  const copyToClipboard = async (text: string, key: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(key);
    toast({ title: 'Copied to clipboard' });
    setTimeout(() => setCopied(null), 2000);
  };

  const getConnectionParams = (platform: AIPlatform, client?: { id: string; token: string }) => {
    if (!client) return {};

    const baseUrl = window.location.origin;
    const params: Record<string, string> = {};

    if (platform.connectionType === 'mcp') {
      params['Server URL'] = `${baseUrl}/sse/${client.id}`;
      params['Authorization Token'] = client.token;
      params['Name'] = 'MyStorey';
    } else if (platform.connectionType === 'api') {
      params['API Endpoint'] = `${baseUrl}/api/mcp/${client.id}`;
      params['API Key'] = client.token;
    }

    return params;
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {AI_PLATFORMS.map((platform) => {
          const client = getClient(platform.id);
          const connectionParams = client ? getConnectionParams(platform, client) : {};

          return (
            <Card key={platform.id} className={client ? 'border-green-200 bg-green-50/50' : ''}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{platform.icon}</span>
                    <div>
                      <CardTitle className="text-lg">{platform.name}</CardTitle>
                      <CardDescription className="text-sm">
                        {platform.description}
                      </CardDescription>
                    </div>
                  </div>
                  {client ? (
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-xs text-green-600">Connected</span>
                    </div>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => onCreateClient(platform.id)}
                      className="text-xs"
                    >
                      <Plus className="h-3 w-3 mr-1" />
                      Connect
                    </Button>
                  )}
                </div>
              </CardHeader>

              {client && (
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-muted-foreground">
                        Connection Details
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                      >
                        <Settings className="h-3 w-3" />
                      </Button>
                    </div>
                    {Object.entries(connectionParams).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-2 bg-background rounded border">
                        <span className="text-xs font-medium">{key}:</span>
                        <div className="flex items-center gap-1">
                          <code className="text-xs bg-muted px-1 rounded max-w-[120px] truncate">
                            {value}
                          </code>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0"
                            onClick={() => copyToClipboard(value, `${platform.id}-${key}`)}
                          >
                            {copied === `${platform.id}-${key}` ? (
                              <Check className="h-3 w-3 text-green-600" />
                            ) : (
                              <Copy className="h-3 w-3" />
                            )}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>

      <Card className="border-blue-200 bg-blue-50/50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <span>💡</span>
            Quick Setup Guide
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-sm space-y-2">
            <p><strong>Claude Desktop:</strong> Settings → Developer → Add Server → Paste parameters</p>
            <p><strong>ChatGPT:</strong> Use MCP plugin or custom integration</p>
            <p><strong>Cursor:</strong> Settings → MCP Servers → Add Server</p>
            <p><strong>Perplexity:</strong> Settings → API Integrations → Add Custom</p>
          </div>
          <div className="text-xs text-muted-foreground bg-background p-3 rounded">
            <p>All connections use the same MCP server. The server URL and token are automatically generated for each platform.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
