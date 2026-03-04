'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Copy } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface ClaudeConnectProps {
  token: string;
  clientId: string;
}

export function ClaudeConnect({ token, clientId }: ClaudeConnectProps) {
  const { toast } = useToast();

  if (!token) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span>🤖</span>
            Claude Desktop Connection
          </CardTitle>
          <CardDescription>Create an MCP client first to connect Claude Desktop</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg">
            <h4 className="font-semibold text-amber-800 dark:text-amber-200 mb-2">
              ⚠️ No Claude Client Found
            </h4>
            <p className="text-sm text-amber-700 dark:text-amber-300">
              You need to create a Claude Desktop MCP client first. Click &quot;Add Client&quot;
              below and select &quot;Claude Desktop&quot; as the tool type.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const connectionParams = {
    Name: 'AI CMS',
    'Server URL': clientId ? `${window.location.origin}/sse/${clientId}` : `${window.location.origin}/sse`,
    'authorization_token': token,
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>🤖</span>
          Claude Desktop Connection
        </CardTitle>
        <CardDescription>
          Enter these parameters in Claude Desktop&apos;s MCP Server configuration form
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
          <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2">
            ✅ Server is ready!
          </h4>
          <p className="text-sm text-green-700 dark:text-green-300">
            Your MCP server is accessible at:{' '}
            <code className="bg-green-100 dark:bg-green-800 px-1 rounded">{window.location.origin}</code>
          </p>
        </div>

        <div className="space-y-3">
          <h4 className="font-semibold">Connection Parameters</h4>
          {Object.entries(connectionParams).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <span className="font-medium">{key}:</span>
              <div className="flex items-center gap-2">
                <code className="text-sm bg-background px-2 py-1 rounded">{value}</code>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(value);
                    toast({ title: `${key} copied!` });
                  }}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-2">
          <h4 className="font-semibold">How to connect</h4>
          <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
            <li>Open Claude Desktop</li>
            <li>Go to Settings &gt; Developer</li>
            <li>Click &quot;Add Server&quot; or &quot;Edit Config&quot;</li>
            <li>Enter the parameters above</li>
            <li>Save and restart Claude Desktop</li>
          </ol>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">💡 Note</h4>
          <p className="text-sm text-blue-700 dark:text-blue-300">
            Make sure Docker is running and the ngrok tunnel is active. The connection uses HTTP
            transport with token authentication.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
