'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, EyeOff, Copy, Check, Trash2, Plus, Zap, CheckCircle2, XCircle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import {
  listWordPressSites,
  deleteWordPressSite,
  testWordPressSiteConnection,
  WordPressSite,
} from '@/lib/api/wordpress';
import { RegisterWordPressSite } from '@/components/wordpress/RegisterWordPressSite';

// ── Copy/reveal field ─────────────────────────────────────────────────────────

function CopyField({
  label,
  value,
  secret,
}: {
  label: string;
  value: string;
  secret?: boolean;
}) {
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
        <span className="flex-1 text-sm truncate font-mono">{display}</span>
        {secret && (
          <button
            onClick={() => setRevealed((r) => !r)}
            className="text-muted-foreground hover:text-foreground shrink-0"
            title={revealed ? 'Hide' : 'Reveal'}
          >
            {revealed ? <EyeOff size={14} /> : <Eye size={14} />}
          </button>
        )}
        <button
          onClick={copy}
          className="text-muted-foreground hover:text-foreground shrink-0"
          title="Copy"
        >
          {copied ? <Check size={14} className="text-green-600" /> : <Copy size={14} />}
        </button>
      </div>
    </div>
  );
}

// ── Site card ─────────────────────────────────────────────────────────────────

type TestStatus = 'idle' | 'loading' | 'ok' | 'error';

function SiteCard({
  site,
  onDelete,
}: {
  site: WordPressSite;
  onDelete: (id: string) => void;
}) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [testStatus, setTestStatus] = useState<TestStatus>('idle');
  const [testMessage, setTestMessage] = useState('');
  const mcpUrl =
    typeof window !== 'undefined' ? `${window.location.origin}/mcp` : '';

  const runTest = async () => {
    setTestStatus('loading');
    setTestMessage('');
    const result = await testWordPressSiteConnection(site.id);
    if (result.ok) {
      setTestStatus('ok');
      setTestMessage(result.site_name ? `Connected — "${result.site_name}"` : 'Connected');
    } else {
      setTestStatus('error');
      setTestMessage(result.error ?? 'Connection failed');
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <CardTitle className="text-base truncate">
              {site.site_name ?? site.site_url}
            </CardTitle>
            {site.site_name && (
              <p className="text-xs text-muted-foreground mt-0.5 truncate">{site.site_url}</p>
            )}
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Badge
              variant="outline"
              className={
                site.is_active
                  ? 'text-green-600 border-green-300 bg-green-50'
                  : 'text-gray-500 border-gray-300'
              }
            >
              {site.is_active ? 'Active' : 'Inactive'}
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              className="text-red-500 hover:text-red-600 hover:bg-red-50 h-8 w-8 p-0"
              onClick={() => setConfirmOpen(true)}
            >
              <Trash2 size={15} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <CopyField
          label="MCP URL — paste this into your AI client"
          value={mcpUrl}
        />
        <CopyField
          label="MCP Token — use as password / API key in your AI client"
          value={site.mcp_token}
          secret
        />
        <p className="text-xs text-muted-foreground">
          In Claude.ai or ChatGPT: add the MCP URL as a custom connector, then use your MCP Token as
          the credential when prompted.
        </p>

        {/* Test connection */}
        <div className="flex items-center gap-3 pt-1">
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 text-xs h-8"
            onClick={runTest}
            disabled={testStatus === 'loading'}
          >
            {testStatus === 'loading' ? (
              <span className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
            ) : (
              <Zap size={13} />
            )}
            {testStatus === 'loading' ? 'Testing…' : 'Test connection'}
          </Button>
          {testStatus === 'ok' && (
            <span className="flex items-center gap-1 text-xs text-green-600 font-medium">
              <CheckCircle2 size={13} /> {testMessage}
            </span>
          )}
          {testStatus === 'error' && (
            <span className="flex items-center gap-1 text-xs text-red-500 font-medium">
              <XCircle size={13} /> {testMessage}
            </span>
          )}
        </div>
      </CardContent>

      {/* Delete confirmation dialog */}
      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Remove WordPress site?</DialogTitle>
            <DialogDescription>
              This will disconnect <strong>{site.site_name ?? site.site_url}</strong> from MyStorey.
              Your WordPress site will not be affected, but AI assistants will lose access to it.
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setConfirmOpen(false)}>
              Cancel
            </Button>
            <Button
              className="bg-red-600 hover:bg-red-700 text-white"
              onClick={() => {
                setConfirmOpen(false);
                onDelete(site.id);
              }}
            >
              Remove site
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function WordPressPage() {
  const [sites, setSites] = useState<WordPressSite[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const { toast } = useToast();

  const fetchSites = useCallback(async () => {
    try {
      const data = await listWordPressSites();
      setSites(data);
    } catch {
      toast({ title: 'Failed to load WordPress sites', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchSites();
  }, [fetchSites]);

  const handleRegistered = (site: WordPressSite) => {
    setSites((prev) => [...prev, site]);
    setShowAddForm(false);
  };

  const handleDelete = async (siteId: string) => {
    try {
      await deleteWordPressSite(siteId);
      setSites((prev) => prev.filter((s) => s.id !== siteId));
      toast({ title: 'WordPress site removed' });
    } catch {
      toast({ title: 'Failed to remove site', variant: 'destructive' });
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold">WordPress Sites</h1>
        <Card>
          <CardContent className="py-12 flex justify-center">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">WordPress Sites</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          Connect your WordPress sites to control content via AI chat.
        </p>
      </div>

      {/* Empty state: show registration form */}
      {sites.length === 0 && !showAddForm && (
        <div className="flex flex-col items-center gap-6 py-8">
          <p className="text-sm text-muted-foreground text-center max-w-sm">
            No WordPress sites connected yet. Add your first site to start controlling it with AI.
          </p>
          <RegisterWordPressSite onSuccess={handleRegistered} />
        </div>
      )}

      {/* Site list */}
      {sites.length > 0 && (
        <div className="space-y-4">
          {sites.map((site) => (
            <SiteCard key={site.id} site={site} onDelete={handleDelete} />
          ))}

          {/* Add another */}
          {!showAddForm ? (
            <Button
              variant="outline"
              className="w-full gap-2"
              onClick={() => setShowAddForm(true)}
            >
              <Plus size={16} />
              Add another site
            </Button>
          ) : (
            <div className="flex flex-col items-center gap-4">
              <RegisterWordPressSite onSuccess={handleRegistered} />
              <Button variant="ghost" size="sm" onClick={() => setShowAddForm(false)}>
                Cancel
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Show form if user clicked cancel on empty state somehow */}
      {sites.length === 0 && showAddForm && (
        <div className="flex flex-col items-center gap-4">
          <RegisterWordPressSite onSuccess={handleRegistered} />
          <Button variant="ghost" size="sm" onClick={() => setShowAddForm(false)}>
            Cancel
          </Button>
        </div>
      )}
    </div>
  );
}
