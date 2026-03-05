'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Globe, Edit, Trash2 } from 'lucide-react';

interface Site {
  id: string;
  name: string;
  slug: string;
  theme_slug: string;
  is_deleted?: boolean;
  deleted_at?: string;
  created_at: string;
}

export default function DashboardPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [deletedSites, setDeletedSites] = useState<Site[]>([]);
  const [showDeleted, setShowDeleted] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchSites = useCallback(async () => {
    try {
      const [activeRes, deletedRes] = await Promise.all([
        api.get('/sites/'),
        api.get('/sites/?include_deleted=true'),
      ]);
      const allSites = deletedRes.data as Site[];
      setSites(activeRes.data as Site[]);
      setDeletedSites(allSites.filter((s) => s.is_deleted));
    } catch (error) {
      console.error('Failed to fetch sites', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSites();
  }, [fetchSites]);

  const handleDeleteSite = async (siteId: string) => {
    if (!confirm('Are you sure you want to delete this site?')) return;

    try {
      await api.delete(`/sites/${siteId}`);
      fetchSites();
    } catch (error) {
      console.error('Failed to delete site', error);
    }
  };

  const handleRestoreSite = async (siteId: string) => {
    try {
      await api.patch(`/sites/${siteId}`, { is_deleted: false, deleted_at: null });
      fetchSites();
    } catch (error) {
      console.error('Failed to restore site', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Sites</h1>
          <p className="text-gray-600">Manage your websites</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setShowDeleted(!showDeleted)}
          >
            {showDeleted ? 'Hide' : 'Show'} Deleted ({deletedSites.length})
          </Button>
          <Link href="/dashboard/sites/new">
            <Button className="gap-2">
              <Plus size={20} />
              New Site
            </Button>
          </Link>
        </div>
      </div>

      {sites.length === 0 ? (
        <Card className="p-12 text-center">
          <Globe className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No sites yet</h3>
          <p className="text-gray-600 mb-4">Create your first site to get started</p>
          <Link href="/dashboard/sites/new">
            <Button>Create Site</Button>
          </Link>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sites.map((site) => (
            <Card key={site.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-xl">{site.name}</CardTitle>
                    <CardDescription>/{site.slug}</CardDescription>
                  </div>
                  <div className="flex gap-1">
                    <Link href={`/dashboard/sites/${site.id}`}>
                      <Button variant="outline" size="sm">
                        <Edit size={16} />
                      </Button>
                    </Link>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteSite(site.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 size={16} />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Theme:</span>
                    <span className="capitalize">{site.theme_slug}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Created:</span>
                    <span>{new Date(site.created_at).toLocaleDateString()}</span>
                  </div>
                  <Link href={`/${site.slug}`} target="_blank">
                    <Button variant="outline" className="w-full gap-2">
                      <Globe size={16} />
                      View Site
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showDeleted && deletedSites.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-gray-500 mb-4">Deleted Sites</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 opacity-60">
            {deletedSites.map((site) => (
              <Card key={site.id} className="hover:shadow-lg transition-shadow border-red-200">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-xl text-gray-500">{site.name}</CardTitle>
                      <CardDescription>/{site.slug}</CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRestoreSite(site.id)}
                      className="text-green-600 hover:text-green-700"
                    >
                      Restore
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Theme:</span>
                      <span className="capitalize">{site.theme_slug}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Deleted:</span>
                      <span>{site.deleted_at ? new Date(site.deleted_at).toLocaleDateString() : 'Unknown'}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
