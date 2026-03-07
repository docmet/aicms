'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { registerWordPressSite, WordPressSite } from '@/lib/api/wordpress';
import { useToast } from '@/hooks/use-toast';
import { Globe } from 'lucide-react';

interface RegisterWordPressSiteProps {
  onSuccess: (site: WordPressSite) => void;
}

export function RegisterWordPressSite({ onSuccess }: RegisterWordPressSiteProps) {
  const [siteUrl, setSiteUrl] = useState('');
  const [appUsername, setAppUsername] = useState('');
  const [appPassword, setAppPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const site = await registerWordPressSite(siteUrl, appUsername, appPassword);
      toast({ title: 'WordPress site connected successfully' });
      onSuccess(site);
    } catch (err: unknown) {
      const message =
        err &&
        typeof err === 'object' &&
        'response' in err &&
        err.response &&
        typeof err.response === 'object' &&
        'data' in err.response &&
        err.response.data &&
        typeof err.response.data === 'object' &&
        'detail' in err.response.data
          ? String((err.response.data as { detail: unknown }).detail)
          : 'Failed to connect WordPress site. Check your credentials and try again.';
      toast({ title: 'Connection failed', description: message, variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-md w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe size={20} className="text-violet-600" />
          Connect WordPress Site
        </CardTitle>
        <CardDescription>
          Enter your WordPress site URL and Application Password to connect it for AI control.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="siteUrl">WordPress Site URL</Label>
            <Input
              id="siteUrl"
              type="url"
              placeholder="https://yoursite.com"
              value={siteUrl}
              onChange={(e) => setSiteUrl(e.target.value)}
              required
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="appUsername">WordPress Username</Label>
            <Input
              id="appUsername"
              type="text"
              placeholder="admin"
              value={appUsername}
              onChange={(e) => setAppUsername(e.target.value)}
              required
            />
            <p className="text-xs text-muted-foreground">
              Your WordPress login username — the one you use to sign in to WP admin (e.g.{' '}
              <code className="bg-muted px-1 rounded">admin</code>). Not the name you give the Application Password.
            </p>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="appPassword">Application Password</Label>
            <Input
              id="appPassword"
              type="password"
              placeholder="xxxx xxxx xxxx xxxx xxxx xxxx"
              value={appPassword}
              onChange={(e) => setAppPassword(e.target.value)}
              required
            />
            <p className="text-xs text-muted-foreground">
              Go to WordPress Admin &rarr; Users &rarr; Profile &rarr; Application Passwords. Enter any
              name (e.g. <code className="bg-muted px-1 rounded">MyStorey</code>), click{' '}
              <strong>Add New</strong>, and paste the generated password here.
            </p>
          </div>

          <Button type="submit" className="w-full bg-violet-600 hover:bg-violet-700" disabled={loading}>
            {loading ? 'Connecting...' : 'Connect Site'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
