'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Copy, Check, RefreshCw, ExternalLink, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

interface Credential {
  id: string;
  name: string;
  token: string;
  created_at: string;
}

function CopyField({ label, value, secret }: { label: string; value: string; secret?: boolean }) {
  const [copied, setCopied] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const { toast } = useToast();

  const copy = async () => {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    toast({ title: `${label} copied` });
    setTimeout(() => setCopied(false), 2000);
  };

  const display = secret && !revealed ? '••••••••••••••••' : value;

  return (
    <div className="space-y-1">
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</p>
      <div className="flex items-center gap-2 bg-muted/50 border rounded-lg px-3 py-2">
        <code className="flex-1 text-sm font-mono truncate">{display}</code>
        {secret && (
          <button
            onClick={() => setRevealed((r) => !r)}
            className="text-muted-foreground hover:text-foreground shrink-0"
          >
            {revealed ? <EyeOff size={14} /> : <Eye size={14} />}
          </button>
        )}
        <button
          onClick={copy}
          className="text-muted-foreground hover:text-foreground shrink-0"
        >
          {copied ? <Check size={14} className="text-green-600" /> : <Copy size={14} />}
        </button>
      </div>
    </div>
  );
}

function Step({ n, children }: { n: number; children: React.ReactNode }) {
  return (
    <div className="flex gap-3">
      <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-bold shrink-0 mt-0.5">
        {n}
      </div>
      <div className="flex-1">{children}</div>
    </div>
  );
}

export default function AIToolsPage() {
  const [cred, setCred] = useState<Credential | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const { toast } = useToast();

  const fetchOrCreate = useCallback(async (force = false) => {
    try {
      const listRes = await api.get<Credential[]>('/mcp/clients');
      if (listRes.data.length > 0 && !force) {
        setCred(listRes.data[0]);
        return;
      }
      // Delete old ones if regenerating
      if (force) {
        for (const c of listRes.data) {
          await api.delete(`/mcp/clients/${c.id}`);
        }
      }
      const createRes = await api.post<Credential>('/mcp/register', {
        name: 'My AI Connection',
        tool_type: 'claude',
      });
      setCred(createRes.data);
    } catch {
      toast({ title: 'Failed to load connection details', variant: 'destructive' });
    } finally {
      setLoading(false);
      setRegenerating(false);
    }
  }, [toast]);

  useEffect(() => { fetchOrCreate(); }, [fetchOrCreate]);

  const regenerate = async () => {
    setRegenerating(true);
    await fetchOrCreate(true);
    toast({ title: 'New connection key generated' });
  };

  // nginx proxies /sse/, /authorize, /token, /.well-known/ to mcp_server
  // so the MCP server URL is the same origin as the dashboard
  const mcpUrl = typeof window !== 'undefined' ? window.location.origin : '';

  const openClaudeAi = () => {
    window.open('https://claude.ai/customize/connectors', '_blank');
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Connect AI Tools</h1>
          <p className="text-muted-foreground mt-1">Setting up your connection...</p>
        </div>
        <Card>
          <CardContent className="py-12 flex justify-center">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!cred) return null;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">Connect AI Tools</h1>
          <p className="text-muted-foreground mt-1">
            Use Claude, Cursor, or any AI assistant to manage your sites
          </p>
        </div>
        <div className="flex items-center gap-2 mt-1">
          <Badge variant="outline" className="text-green-600 border-green-300 bg-green-50">
            Active
          </Badge>
          <Button
            variant="ghost"
            size="sm"
            onClick={regenerate}
            disabled={regenerating}
            className="text-muted-foreground"
          >
            <RefreshCw size={14} className={`mr-1 ${regenerating ? 'animate-spin' : ''}`} />
            Regenerate
          </Button>
        </div>
      </div>

      {/* ── Connection fields (same for all tools) ───────────────────── */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Your connection details</CardTitle>
          <p className="text-sm text-muted-foreground">
            Copy these into your AI tool&apos;s settings — works with Claude, Cursor, and any MCP-compatible assistant.
          </p>
        </CardHeader>
        <CardContent className="space-y-3">
          <CopyField label="Name" value="AI CMS" />
          <CopyField label="MCP Server URL" value={mcpUrl} />
          <CopyField label="OAuth Client ID" value={cred.id} />
          <CopyField label="OAuth Client Secret" value={cred.token} secret />
        </CardContent>
      </Card>

      <Tabs defaultValue="claude-ai">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="claude-ai">Claude.ai</TabsTrigger>
          <TabsTrigger value="claude-desktop">Claude Desktop</TabsTrigger>
        </TabsList>

        {/* ── Claude.ai ─────────────────────────────────────────────── */}
        <TabsContent value="claude-ai" className="mt-4">
          <Card>
            <CardContent className="pt-5 space-y-4">
              <Step n={1}>
                <p className="text-sm font-medium mb-1">Open Claude.ai integration settings</p>
                <Button size="sm" onClick={openClaudeAi} className="gap-2">
                  <ExternalLink size={14} />
                  Open Claude.ai Settings
                </Button>
                <p className="text-xs text-muted-foreground mt-1">
                  Then go to <strong>Integrations</strong> → <strong>Add Integration</strong>
                </p>
              </Step>

              <Step n={2}>
                <p className="text-sm font-medium">Paste the fields from above and save</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Try asking: <em>&ldquo;List my sites&rdquo;</em>
                </p>
              </Step>

              <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
                <AlertCircle size={14} className="shrink-0 mt-0.5" />
                <p>
                  Claude.ai connects from Anthropic&apos;s servers so this URL must be publicly
                  accessible. Works automatically in production; for local dev use Claude Desktop instead.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Claude Desktop ─────────────────────────────────────────── */}
        <TabsContent value="claude-desktop" className="mt-4">
          <Card>
            <CardContent className="pt-5 space-y-4">
              <Step n={1}>
                <p className="text-sm font-medium mb-1">Open Claude Desktop settings</p>
                <p className="text-xs text-muted-foreground">
                  Click the menu icon → <strong>Settings</strong> → <strong>Integrations</strong> → <strong>Add custom integration</strong>
                </p>
              </Step>

              <Step n={2}>
                <p className="text-sm font-medium">Paste the fields from above and save</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Restart Claude Desktop if needed, then try: <em>&ldquo;List my sites&rdquo;</em>
                </p>
              </Step>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card className="border-muted">
        <CardContent className="py-4">
          <p className="text-xs text-muted-foreground text-center">
            Your connection key is tied to your account. Keep it private.
            If compromised, use <strong>Regenerate</strong> above to invalidate it.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
