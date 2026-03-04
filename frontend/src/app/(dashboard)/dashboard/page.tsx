'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Globe, Plus, Pencil } from 'lucide-react';
import { Button } from '@/components/ui/button';
import api from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import Link from 'next/link';

interface Site {
  id: string;
  name: string;
  slug: string;
  theme_slug: string;
  created_at: string;
}

export default function DashboardPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchSites();
  }, [toast]);

  const fetchSites = async () => {
    try {
      const response = await api.get('/sites/');
      setSites(response.data);
    } catch (error) {
      console.error('Failed to fetch sites', error);
      toast({
        title: 'Error',
        description: 'Failed to load sites. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-gray-200 animate-pulse rounded"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 bg-gray-200 animate-pulse rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">Welcome back! Manage your websites here.</p>
        </div>
        <Button className="gap-2" asChild>
          <Link href="/dashboard/sites/new">
            <Plus size={18} />
            Create New Site
          </Link>
        </Button>
      </div>

      {sites.length === 0 ? (
        <Card className="bg-white border-dashed border-2">
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-4">
              <Globe size={24} />
            </div>
            <CardTitle className="text-xl mb-2">No sites found</CardTitle>
            <CardDescription className="max-w-xs mb-6">
              You haven&apos;t created any websites yet. Start by creating your first landing page!
            </CardDescription>
            <Button asChild>
              <Link href="/dashboard/sites/new">Create First Site</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sites.map((site) => (
            <Card key={site.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center mb-2">
                    <Globe size={20} />
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
                      <Link href={`/dashboard/sites/${site.id}`}>
                        <Pencil size={16} />
                      </Link>
                    </Button>
                  </div>
                </div>
                <CardTitle>{site.name}</CardTitle>
                <CardDescription className="font-mono text-xs">
                  {site.slug}.aicms.docmet.systems
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center pt-2">
                  <span className="text-xs text-gray-400">
                    Theme: <span className="font-medium text-gray-600 capitalize">{site.theme_slug}</span>
                  </span>
                  <Button variant="outline" size="sm" asChild>
                    <a href={`/${site.slug}`} target="_blank" rel="noopener noreferrer">
                      View Site
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
