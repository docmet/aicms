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

// ── Provider SVG icons ────────────────────────────────────────────────────────

function ClaudeIcon({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="6" fill="#D97757" />
      <path d="M9.5 7L6 17h2l.8-2.5h4.4l.8 2.5h2L12.5 7H9.5zm-.3 5.5L10.9 9h.2l1.7 3.5H9.2z" fill="white" />
    </svg>
  );
}

function ChatGPTIcon({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="6" fill="#10A37F" />
      <path d="M12 4.5a4.5 4.5 0 00-4.242 6.004A4.5 4.5 0 0012 19.5a4.5 4.5 0 004.242-8.996A4.5 4.5 0 0012 4.5zm0 1.5a3 3 0 012.83 2h-5.66A3 3 0 0112 6zm-3 3.5h6a3 3 0 010 5H9a3 3 0 010-5z" fill="white" fillOpacity="0.9" />
    </svg>
  );
}

function PerplexityIcon({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="6" fill="#6B7280" />
      <path d="M12 5l2 4h4l-3 3 1 4-4-2.5L8 16l1-4-3-3h4l2-4z" fill="white" fillOpacity="0.7" />
    </svg>
  );
}

// ── Copy field ────────────────────────────────────────────────────────────────

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

// ── Step list ─────────────────────────────────────────────────────────────────

function Steps({ steps }: { steps: (string | React.ReactNode)[] }) {
  return (
    <ol className="space-y-2">
      {steps.map((step, i) => (
        <li key={i} className="flex gap-3 text-sm text-muted-foreground">
          <span className="shrink-0 w-5 h-5 rounded-full bg-muted flex items-center justify-center text-[11px] font-semibold text-foreground mt-0.5">
            {i + 1}
          </span>
          <span className="leading-relaxed">{step}</span>
        </li>
      ))}
    </ol>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function AIToolsPage() {
  const [cred, setCred] = useState<Credential | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [showOther, setShowOther] = useState(false);
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
      <div className="max-w-xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold">Connect AI Tools</h1>
        <Card><CardContent className="py-12 flex justify-center">
          <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </CardContent></Card>
      </div>
    );
  }

  if (!cred) return null;

  const mcpUrl = typeof window !== 'undefined' ? `${window.location.origin}/mcp` : '';

  return (
    <div className="max-w-xl mx-auto space-y-5">

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Connect AI Tools</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Give your favourite AI assistant direct access to build and edit your sites.
          </p>
        </div>
        <div className="flex items-center gap-2 mt-1">
          <Badge variant="outline" className="text-green-600 border-green-300 bg-green-50">Active</Badge>
          <Button variant="ghost" size="sm" onClick={regenerate} disabled={regenerating} className="text-muted-foreground">
            <RefreshCw size={13} className={`mr-1 ${regenerating ? 'animate-spin' : ''}`} />
            Regenerate
          </Button>
        </div>
      </div>

      {/* URL field — always visible */}
      <CopyField label="Your MCP URL — paste this into any AI connector" value={mcpUrl} />

      {/* ── Claude.ai ─────────────────────────────────────────────────────── */}
      <Card className="border-orange-200">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <ClaudeIcon size={22} />
            Claude.ai
            <Badge variant="secondary" className="text-xs font-normal ml-1">Recommended</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Steps steps={[
            <>Go to <strong>claude.ai</strong> → click your initials (top right) → <strong>Settings</strong></>,
            <>Select <strong>Integrations</strong> in the left sidebar</>,
            <>Under <em>Custom integrations</em>, click <strong>Add more</strong></>,
            <>Paste the URL above → click <strong>Add</strong></>,
            <>You&apos;ll be redirected to MyStorey — log in and click <strong>Approve</strong></>,
            <>Done. In any new conversation, the MyStorey tools are automatically available — just ask Claude to work on your site.</>,
          ]} />
          <Button className="w-full gap-2" onClick={() => window.open('https://claude.ai/settings/integrations', '_blank')}>
            <ExternalLink size={14} />
            Open Claude Integrations
          </Button>
          <p className="text-[11px] text-muted-foreground">
            💡 Once connected on claude.ai, the Claude desktop app picks up the same connector automatically — no extra setup.
          </p>
        </CardContent>
      </Card>

      {/* ── ChatGPT ───────────────────────────────────────────────────────── */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <ChatGPTIcon size={22} />
            ChatGPT
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Steps steps={[
            <>Go to <strong>chatgpt.com</strong> → click your profile picture (top right) → <strong>Settings</strong></>,
            <>Select <strong>Connectors</strong> in the left sidebar</>,
            <>Click <strong>Add connector</strong> → <strong>Add custom connector</strong></>,
            <>Paste the URL above → click <strong>Save</strong></>,
            <>Click <strong>Connect</strong> → you&apos;ll be redirected to MyStorey to approve</>,
            <>In any conversation, click the <strong>tools icon</strong> (⊕ next to the message box) → enable <em>MyStorey</em> to activate it</>,
          ]} />
          <Button variant="outline" className="w-full gap-2" onClick={() => window.open('https://chatgpt.com', '_blank')}>
            <ExternalLink size={14} />
            Open ChatGPT
          </Button>
          <p className="text-[11px] text-muted-foreground">
            ⚠️ If you already added the connector with an old URL, remove it and re-add with the URL above to pick up the latest tools.
          </p>
        </CardContent>
      </Card>

      {/* ── Perplexity — coming soon ──────────────────────────────────────── */}
      <Card className="opacity-60">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <PerplexityIcon size={22} />
            Perplexity
            <Badge variant="secondary" className="text-xs font-normal ml-1 bg-gray-100 text-gray-500">Coming soon</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            MCP connector support in Perplexity is not stable yet. We&apos;ll enable this once their implementation is reliable.
          </p>
        </CardContent>
      </Card>

      {/* Other tools */}
      <button
        onClick={() => setShowOther((v) => !v)}
        className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground w-full justify-center"
      >
        {showOther ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        {showOther ? 'Hide' : 'Using a different AI tool?'}
      </button>

      {showOther && (
        <Card className="border-dashed">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Other MCP-compatible tools</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-xs text-muted-foreground">
              Any AI tool that supports the MCP protocol (Cursor, Windsurf, Zed, etc.) can connect using the URL above.
              Look for a <strong>Add MCP server</strong> or <strong>Custom connector</strong> option in settings,
              paste the URL, and follow the OAuth flow.
            </p>
            <CopyField label="MCP URL" value={mcpUrl} />
          </CardContent>
        </Card>
      )}

      <p className="text-xs text-muted-foreground text-center pb-2">
        Keep your connection private — use <strong>Regenerate</strong> to revoke all existing AI access at any time.
      </p>

    </div>
  );
}
