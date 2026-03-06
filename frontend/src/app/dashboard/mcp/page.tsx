'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Copy, Check, RefreshCw, ExternalLink, Eye, EyeOff, ChevronDown, ChevronUp } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

interface Credential {
  id: string;
  name: string;
  token: string;
  created_at: string;
}

function CopyField({ label, value, secret, mono = true }: { label: string; value: string; secret?: boolean; mono?: boolean }) {
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
        <span className={`flex-1 text-sm truncate ${mono ? 'font-mono' : ''}`}>{display}</span>
        {secret && (
          <button onClick={() => setRevealed((r) => !r)} className="text-muted-foreground hover:text-foreground shrink-0">
            {revealed ? <EyeOff size={14} /> : <Eye size={14} />}
          </button>
        )}
        <button onClick={copy} className="text-muted-foreground hover:text-foreground shrink-0">
          {copied ? <Check size={14} className="text-green-600" /> : <Copy size={14} />}
        </button>
      </div>
    </div>
  );
}

export default function AIToolsPage() {
  const [cred, setCred] = useState<Credential | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [showManual, setShowManual] = useState(false);
  const { toast } = useToast();

  const fetchOrCreate = useCallback(async (force = false) => {
    try {
      const listRes = await api.get<Credential[]>('/mcp/clients');
      if (listRes.data.length > 0 && !force) {
        setCred(listRes.data[0]);
        return;
      }
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

  if (loading) {
    return (
      <div className="max-w-lg mx-auto space-y-6">
        <h1 className="text-3xl font-bold">Connect AI Tools</h1>
        <Card><CardContent className="py-12 flex justify-center">
          <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </CardContent></Card>
      </div>
    );
  }

  if (!cred) return null;

  // Generic MCP endpoint — no client_id in URL.
  // Authentication is entirely via OAuth Bearer token (obtained when you add the connector).
  const mcpUrl = typeof window !== 'undefined'
    ? `${window.location.origin}/mcp`
    : '';

  return (
    <div className="max-w-lg mx-auto space-y-5">

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">Connect AI Tools</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Give Claude, Cursor, or any AI assistant access to your sites
          </p>
        </div>
        <div className="flex items-center gap-2 mt-1">
          <Badge variant="outline" className="text-green-600 border-green-300 bg-green-50">Active</Badge>
          <Button variant="ghost" size="sm" onClick={regenerate} disabled={regenerating} className="text-muted-foreground">
            <RefreshCw size={14} className={`mr-1 ${regenerating ? 'animate-spin' : ''}`} />
            Regenerate
          </Button>
        </div>
      </div>

      {/* Primary: Claude.ai one-click */}
      <Card className="border-blue-200">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            Claude.ai
            <Badge variant="secondary" className="text-xs font-normal">Recommended</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              1. Click the button below to open Claude.ai connector settings
            </p>
            <p className="text-sm text-muted-foreground">
              2. Click <strong>Add custom connector</strong> and paste this URL:
            </p>
            <CopyField label="Connection URL" value={mcpUrl} />
            <p className="text-sm text-muted-foreground">
              3. Click <strong>Add</strong> — you&apos;ll be taken to MyStorey to approve the connection
            </p>
          </div>

          <Button className="w-full gap-2" onClick={() => window.open('https://claude.ai/customize/connectors', '_blank')}>
            <ExternalLink size={15} />
            Open Claude.ai Connectors
          </Button>
        </CardContent>
      </Card>

      {/* Claude Desktop */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Claude Desktop</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Open Claude Desktop → menu → <strong>Settings</strong> → <strong>Integrations</strong> → <strong>Add custom integration</strong>, then paste:
          </p>
          <CopyField label="Connection URL" value={mcpUrl} />
          <p className="text-xs text-muted-foreground">
            Claude Desktop will open a MyStorey sign-in page to complete the connection.
          </p>
        </CardContent>
      </Card>

      {/* Manual fallback */}
      <button
        onClick={() => setShowManual((v) => !v)}
        className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground w-full justify-center"
      >
        {showManual ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        {showManual ? 'Hide' : 'Trouble connecting? Other AI tools'}
      </button>

      {showManual && (
        <Card className="border-dashed">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Other AI tools</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-xs text-muted-foreground">
              Any AI tool that supports MCP can connect using the URL below. You&apos;ll be redirected
              to approve the connection — no extra credentials needed.
            </p>
            <CopyField label="Connection URL" value={mcpUrl} />
          </CardContent>
        </Card>
      )}

      <p className="text-xs text-muted-foreground text-center pb-2">
        Keep your connection key private. Use <strong>Regenerate</strong> if you ever need to revoke access.
      </p>

    </div>
  );
}
