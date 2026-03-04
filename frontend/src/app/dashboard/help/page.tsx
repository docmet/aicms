'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Code } from '@/components/ui/code';
import { Check, Copy, Terminal, Bot } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function HelpPage() {
  const [copied, setCopied] = useState<string | null>(null);
  const { toast } = useToast();

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(id);
      toast({ title: 'Copied to clipboard' });
      setTimeout(() => setCopied(null), 2000);
    } catch {
      toast({ title: 'Failed to copy', variant: 'destructive' });
    }
  };

  const claudeConfig = {
    mcpServers: {
      aicms: {
        command: 'aicms-mcp',
        args: ['--api-url', '/api'],
        env: {
          AICMS_API_TOKEN: 'your-jwt-token-here'
        }
      }
    }
  };

  const claudeConfigJson = JSON.stringify(claudeConfig, null, 2);

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 text-center">
            <h1 className="text-4xl font-bold mb-2">AI CMS MCP Server Setup</h1>
            <p className="text-muted-foreground text-lg">
              Connect your AI CMS to AI tools like ChatGPT, Claude, and Cursor
            </p>
          </div>

          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="claude">Claude Desktop</TabsTrigger>
              <TabsTrigger value="chatgpt">ChatGPT</TabsTrigger>
              <TabsTrigger value="cursor">Cursor</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5" />
                    What is the MCP Server?
                  </CardTitle>
                  <CardDescription>
                    The Model Context Protocol (MCP) server lets AI tools manage your CMS content and themes
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Available Operations:</h3>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-500" />
                        List and view your sites
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-500" />
                        Change site themes (default, warm, nature, dark, minimal)
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-500" />
                        Read and update page content
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-500" />
                        Manage content sections
                      </li>
                    </ul>
                  </div>

                  <div className="bg-muted p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">Prerequisites:</h4>
                    <ul className="space-y-1 text-sm">
                      <li>• AI CMS backend running</li>
                      <li>• Python 3.13+ installed</li>
                      <li>• Your JWT authentication token</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="claude" className="mt-6">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Step 1: Install the MCP Server</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <p>1. Go to <Link href="/dashboard/mcp" className="text-primary hover:underline">AI Tools in dashboard</Link></p>
                      <p>2. Click &quot;Add Client&quot; and select &quot;Claude Desktop&quot;</p>
                      <p>3. Give it a name (e.g., &quot;My Claude&quot;)</p>
                      <p>4. Copy the generated configuration</p>
                      <p>5. Paste it into your Claude Desktop config file</p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Step 2: Get Your JWT Token</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <p>1. Log in to your AI CMS at <Link href="/dashboard" className="text-primary hover:underline">/dashboard</Link></p>
                      <p>2. Open browser dev tools (F12)</p>
                      <p>3. Go to Application → Local Storage → Your domain</p>
                      <p>4. Copy the <Code>token</Code> value</p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Step 3: Configure Claude Desktop</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <p>Find and edit your Claude Desktop config file:</p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <Badge variant="outline">macOS</Badge>
                          <pre className="mt-1 bg-muted p-2 rounded">~/Library/Application Support/Claude/claude_desktop_config.json</pre>
                        </div>
                        <div>
                          <Badge variant="outline">Windows</Badge>
                          <pre className="mt-1 bg-muted p-2 rounded">%APPDATA%\Claude\claude_desktop_config.json</pre>
                        </div>
                      </div>
                      
                      <p>The configuration will be generated for you in the AI Tools dashboard.</p>
                      
                      <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                        <p className="text-sm"><strong>Note:</strong> The MCP server runs in the Docker stack.</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Step 4: Restart Claude</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p>Restart Claude Desktop and you&apos;ll see &quot;AI CMS&quot; in the chat interface. You can now:</p>
                    <ul className="mt-2 space-y-1 text-sm">
                      <li>• &quot;Show me my sites&quot;</li>
                      <li>• &quot;Change my demo-site theme to warm&quot;</li>
                      <li>• &quot;Update the hero section content on demo-site&quot;</li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="chatgpt" className="mt-6">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>ChatGPT Custom Instructions</CardTitle>
                    <CardDescription>
                      <p>Use ChatGPT&apos;s custom instructions to enable MCP server access</p>
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h3 className="font-semibold mb-2">Option 1: Direct API Access</h3>
                      <p>Add this to your custom instructions:</p>
                      <div className="relative">
                        <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg text-sm">
                          <code>{`You have access to the AI CMS MCP server for managing website content. 
The server is running in Docker.

When I ask to:
- View or change sites/themes: Use the list_sites, get_site, and update_theme tools
- Update content: Use get_content and update_content tools
- The API endpoint is: /api
- Use JWT token: [PASTE_YOUR_TOKEN_HERE]`}</code>
                        </pre>
                        <button
                          onClick={() => copyToClipboard(`You have access to the AI CMS MCP server for managing website content. 
The server is running in Docker.

When I ask to:
- View or change sites/themes: Use the list_sites, get_site, and update_theme tools
- Update content: Use get_content and update_content tools
- The API endpoint is: /api
- Use JWT token: [PASTE_YOUR_TOKEN_HERE]`, 'chatgpt')}
                          className="absolute top-2 right-2 p-2 bg-slate-700 hover:bg-slate-600 rounded"
                        >
                          {copied === 'chatgpt' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                        </button>
                      </div>
                    </div>

                    <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                      <h4 className="font-semibold mb-2">Example Interactions:</h4>
                      <ul className="space-y-2 text-sm">
                        <li>• &quot;Show me all my websites&quot;</li>
                        <li>• &quot;Change the theme to dark for my site&quot;</li>
                        <li>• &quot;Update the headline on my homepage&quot;</li>
                        <li>• &quot;What themes are available?&quot;</li>
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="cursor" className="mt-6">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Cursor MCP Integration</CardTitle>
                    <CardDescription>
                      <p>Use Cursor&apos;s MCP support to manage your CMS content</p>
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h3 className="font-semibold mb-2">Setup Steps:</h3>
                      <ol className="space-y-2 text-sm">
                        <li>1. Install the MCP server: <Code>cd mcp_server && pip install -e .</Code></li>
                        <li>2. Open Cursor Settings → MCP</li>
                        <li>3. Add new MCP server with these settings:</li>
                      </ol>
                      
                      <div className="bg-muted p-4 rounded-lg mt-2">
                        <pre className="text-sm">
                          <code>{`Name: AI CMS
Command: aicms-mcp
Args: --api-url /api
Env: AICMS_API_TOKEN=your-jwt-token-here`}</code>
                        </pre>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Usage in Cursor:</h3>
                      <p>Use Cmd+Shift+P and type &quot;AI CMS&quot; to see available commands, or simply ask in chat:</p>
                      <ul className="mt-2 space-y-1 text-sm">
                        <li>• &quot;AI CMS: list my sites&quot;</li>
                        <li>• &quot;AI CMS: update theme to nature&quot;</li>
                        <li>• &quot;AI CMS: show homepage content&quot;</li>
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>

          <div className="mt-8 text-center">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-center gap-2">
                  <Terminal className="h-5 w-5" />
                  Running the MCP Server
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p>The MCP server runs automatically in Docker at port 8001.</p>
                  <div className="bg-muted p-4 rounded-lg">
                    <pre className="text-sm">
                      <code>MCP Server: http://localhost:8001
Status: Running (when Docker is started)</code>
                    </pre>
                  </div>
                  
                  <div className="text-sm text-muted-foreground">
                    <p>No need to run anything manually - it&apos;s all handled by Docker!</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
