'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Copy, Plus, Trash2, Bot, Key, Download } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/lib/auth-context';
import api from '@/lib/api';
import { ClaudeConnect } from '@/components/claude-connect';

interface MCPClient {
  id: string;
  name: string;
  tool_type: 'claude' | 'chatgpt' | 'cursor';
  token: string;
  expires_at: string;
  created_at: string;
}

export default function MCPSettingsPage() {
  const [clients, setClients] = useState<MCPClient[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newClient, setNewClient] = useState<{
    name: string;
    tool_type: 'claude' | 'chatgpt' | 'cursor';
  }>({
    name: '',
    tool_type: 'claude',
  });
  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await api.get('/mcp/clients');
      setClients(response.data);
    } catch (error) {
      toast({ title: 'Failed to fetch clients', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const createClient = async () => {
    if (!newClient.name) {
      toast({ title: 'Please enter a name', variant: 'destructive' });
      return;
    }

    try {
      const response = await api.post('/mcp/register', {
        ...newClient,
        user_id: user?.id,
      });

      setClients([response.data, ...clients]);
      setNewClient({ name: '', tool_type: 'claude' });
      setShowCreate(false);
      toast({ title: 'Client created successfully' });
    } catch (error: any) {
      toast({ title: 'Failed to create client', variant: 'destructive' });
    }
  };

  const deleteClient = async (clientId: string) => {
    try {
      await api.delete(`/mcp/clients/${clientId}`);
      setClients(clients.filter((c) => c.id !== clientId));
      toast({ title: 'Client deleted successfully' });
    } catch (error) {
      toast({ title: 'Failed to delete client', variant: 'destructive' });
    }
  };

  const copyToken = (token: string) => {
    navigator.clipboard.writeText(token);
    toast({ title: 'Token copied to clipboard' });
  };

  const getToolIcon = (type: string) => {
    switch (type) {
      case 'claude':
        return '🤖';
      case 'chatgpt':
        return '💬';
      case 'cursor':
        return '👆';
      default:
        return '🔌';
    }
  };

  const getInstructions = (type: string, token: string) => {
    const baseUrl = window.location.origin;
    switch (type) {
      case 'claude':
        const ngrokUrl = 'https://82c1-2a02-ab88-1510-ce80-4e7-66a0-7852-a87c.ngrok-free.app'; // Update with your ngrok URL
        return {
          title: 'Claude Desktop Setup',
          config: JSON.stringify(
            {
              mcpServers: {
                aicms: {
                  command: 'node',
                  args: ['/path/to/mcp_cms/mcp-proxy-server.js'],
                  env: {
                    API_URL: `${ngrokUrl}/api`,
                    AUTH_TOKEN: token,
                  },
                },
              },
            },
            null,
            2
          ),
          note: `1. Download the MCP proxy file from your dashboard\n2. Save it somewhere on your computer\n3. Update the path in the config above\n4. Copy and paste this configuration into Claude Desktop\n\nNo Docker required!`,
        };
      case 'chatgpt':
        return {
          title: 'ChatGPT Custom Instructions',
          instructions: `Add this to your ChatGPT custom instructions:
You have access to the AI CMS MCP server at ${baseUrl}:8001
Use this token: ${token}
Available tools: list_sites, get_site, update_theme, get_content, update_content`,
        };
      case 'cursor':
        return {
          title: 'Cursor Setup',
          config: `Name: AI CMS
URL: ${baseUrl}:8001
Token: ${token}`,
        };
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Tool Integration</h1>
        <p className="text-muted-foreground mt-2">
          Manage MCP clients for AI tools like Claude, ChatGPT, and Cursor
        </p>
      </div>

      {/* Quick Connect for Claude Desktop */}
      <ClaudeConnect
        token={clients.find((c) => c.tool_type === 'claude')?.token || ''}
        ngrokUrl="https://033a-45-155-40-197.ngrok-free.app"
      />

      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                MCP Clients
              </CardTitle>
              <CardDescription>Registered clients for AI tool integration</CardDescription>
            </div>
            <Button onClick={() => setShowCreate(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Client
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Loading...</p>
          ) : clients.length === 0 ? (
            <p className="text-muted-foreground">No clients registered yet</p>
          ) : (
            <div className="space-y-4">
              {clients.map((client) => {
                const instructions = getInstructions(client.tool_type, client.token);
                return (
                  <div key={client.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{getToolIcon(client.tool_type)}</span>
                        <div>
                          <h3 className="font-semibold">{client.name}</h3>
                          <Badge variant="outline">{client.tool_type}</Badge>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => deleteClient(client.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2">
                        <Key className="h-4 w-4" />
                        <span className="font-mono text-xs bg-muted px-2 py-1 rounded">
                          {client.token.substring(0, 20)}...
                        </span>
                        <Button variant="ghost" size="sm" onClick={() => copyToken(client.token)}>
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>

                      {instructions && (
                        <div className="mt-4">
                          <h4 className="font-semibold mb-2">{instructions.title}</h4>
                          {client.tool_type === 'claude' && (
                            <Button
                              variant="outline"
                              size="sm"
                              className="mb-2"
                              onClick={() => {
                                const link = document.createElement('a');
                                link.href = '/mcp-proxy-server.js';
                                link.download = 'mcp-proxy-server.js';
                                link.click();
                              }}
                            >
                              <Download className="h-4 w-4 mr-2" />
                              Download MCP Proxy Server
                            </Button>
                          )}
                          <pre className="bg-slate-100 dark:bg-slate-800 p-3 rounded text-xs overflow-x-auto mb-2">
                            {instructions.config || instructions.instructions}
                          </pre>
                          {instructions.note && (
                            <p className="text-xs text-muted-foreground whitespace-pre-line">
                              {instructions.note}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle>Create New MCP Client</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="name">Client Name</Label>
              <Input
                id="name"
                placeholder="e.g., My Claude Desktop"
                value={newClient.name}
                onChange={(e) => setNewClient({ ...newClient, name: e.target.value })}
              />
            </div>

            <div>
              <Label htmlFor="tool">AI Tool</Label>
              <Select
                value={newClient.tool_type}
                onValueChange={(value: string) =>
                  setNewClient({
                    ...newClient,
                    tool_type: value as 'claude' | 'chatgpt' | 'cursor',
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="claude">🤖 Claude Desktop</SelectItem>
                  <SelectItem value="chatgpt">💬 ChatGPT</SelectItem>
                  <SelectItem value="cursor">👆 Cursor</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex gap-2">
              <Button onClick={createClient}>Create Client</Button>
              <Button variant="outline" onClick={() => setShowCreate(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
