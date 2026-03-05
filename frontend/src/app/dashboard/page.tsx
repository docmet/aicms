'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import { Plus, Globe, Edit, Trash2, Sparkles, ArrowRight, Zap } from 'lucide-react';

interface Site {
  id: string;
  name: string;
  slug: string;
  theme_slug: string;
  is_deleted?: boolean;
  deleted_at?: string;
  created_at: string;
}

const PLAN_LIMITS = { free: 1, pro: 3, agency: 15 };
const PLAN_LABELS = { free: 'Free', pro: 'Pro', agency: 'Agency' };

export default function DashboardPage() {
  const { user } = useAuth();
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
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchSites(); }, [fetchSites]);

  const handleDeleteSite = async (siteId: string) => {
    if (!confirm('Delete this site?')) return;
    try {
      await api.delete(`/sites/${siteId}`);
      fetchSites();
    } catch { /* ignore */ }
  };

  const handleRestoreSite = async (siteId: string) => {
    try {
      await api.patch(`/sites/${siteId}`, { is_deleted: false, deleted_at: null });
      fetchSites();
    } catch { /* ignore */ }
  };

  const plan = user?.plan ?? 'free';
  const limit = PLAN_LIMITS[plan];
  const atLimit = sites.length >= limit;

  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <div className="w-6 h-6 border-2 border-violet-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Sites</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {sites.length} of {limit} site{limit !== 1 ? 's' : ''} used
            {' · '}<span className="font-medium text-gray-700">{PLAN_LABELS[plan]} plan</span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          {deletedSites.length > 0 && (
            <Button variant="outline" size="sm" onClick={() => setShowDeleted(!showDeleted)}>
              {showDeleted ? 'Hide' : 'Trash'} ({deletedSites.length})
            </Button>
          )}
          {atLimit ? (
            <Link href="/#pricing">
              <Button size="sm" className="gap-1.5 bg-violet-600 hover:bg-violet-700">
                <Zap size={14} />
                Upgrade
              </Button>
            </Link>
          ) : (
            <Link href="/dashboard/sites/new">
              <Button size="sm" className="gap-1.5 bg-violet-600 hover:bg-violet-700">
                <Plus size={14} />
                New Site
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Plan limit banner */}
      {atLimit && plan === 'free' && (
        <div className="flex items-center justify-between gap-4 bg-gradient-to-r from-violet-50 to-indigo-50 border border-violet-200 rounded-xl px-5 py-4">
          <div className="flex items-start gap-3">
            <Sparkles size={18} className="text-violet-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-gray-900">Free plan limit reached</p>
              <p className="text-xs text-gray-500 mt-0.5">Upgrade to Pro for 3 sites, custom domains, and no badge — just $9.99/mo.</p>
            </div>
          </div>
          <Link href="/#pricing">
            <Button size="sm" className="gap-1.5 bg-violet-600 hover:bg-violet-700 whitespace-nowrap">
              See plans <ArrowRight size={13} />
            </Button>
          </Link>
        </div>
      )}

      {/* Sites grid */}
      {sites.length === 0 ? (
        <div className="border-2 border-dashed border-gray-200 rounded-2xl p-16 text-center bg-gray-50/50">
          <div className="w-12 h-12 rounded-2xl bg-violet-100 flex items-center justify-center mx-auto mb-4">
            <Globe size={22} className="text-violet-600" />
          </div>
          <h3 className="text-base font-semibold text-gray-900 mb-1">No sites yet</h3>
          <p className="text-sm text-gray-500 mb-5">Create your first site and connect your AI assistant to start building.</p>
          <Link href="/dashboard/sites/new">
            <Button className="gap-2 bg-violet-600 hover:bg-violet-700">
              <Plus size={15} />
              Create your first site
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {sites.map((site) => (
            <div key={site.id} className="group bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all hover:-translate-y-0.5">
              {/* Site preview strip */}
              <div className="h-24 bg-gradient-to-br from-violet-50 to-indigo-100 flex items-center justify-center border-b border-gray-100">
                <Globe size={28} className="text-violet-300" />
              </div>

              <div className="p-5">
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div className="min-w-0">
                    <h3 className="font-semibold text-gray-900 truncate">{site.name}</h3>
                    <p className="text-xs text-gray-400 mt-0.5">/{site.slug}</p>
                  </div>
                  <div className="flex gap-1 flex-shrink-0">
                    <Link href={`/dashboard/sites/${site.id}`}>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-gray-400 hover:text-gray-700">
                        <Edit size={14} />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-gray-400 hover:text-red-500"
                      onClick={() => handleDeleteSite(site.id)}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-400 mb-4">
                  <span className="capitalize bg-gray-100 px-2 py-0.5 rounded-md font-medium text-gray-500">{site.theme_slug}</span>
                  <span>{new Date(site.created_at).toLocaleDateString()}</span>
                </div>

                <Link href={`/${site.slug}`} target="_blank">
                  <Button variant="outline" size="sm" className="w-full gap-1.5 text-xs h-8">
                    <Globe size={12} />
                    View site
                  </Button>
                </Link>
              </div>
            </div>
          ))}

          {/* Add site card (only if under limit) */}
          {!atLimit && (
            <Link href="/dashboard/sites/new" className="group border-2 border-dashed border-gray-200 rounded-2xl flex flex-col items-center justify-center p-8 hover:border-violet-300 hover:bg-violet-50/30 transition-all min-h-[220px]">
              <div className="w-10 h-10 rounded-xl bg-gray-100 group-hover:bg-violet-100 flex items-center justify-center mb-3 transition-colors">
                <Plus size={18} className="text-gray-400 group-hover:text-violet-600 transition-colors" />
              </div>
              <p className="text-sm font-medium text-gray-500 group-hover:text-violet-600 transition-colors">New site</p>
            </Link>
          )}
        </div>
      )}

      {/* Deleted sites */}
      {showDeleted && deletedSites.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">Trash</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 opacity-60">
            {deletedSites.map((site) => (
              <div key={site.id} className="bg-white border border-red-100 rounded-2xl p-5">
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-500 truncate">{site.name}</h3>
                    <p className="text-xs text-gray-400 mt-0.5">/{site.slug}</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => handleRestoreSite(site.id)} className="text-xs h-7 px-2">
                    Restore
                  </Button>
                </div>
                <p className="text-xs text-gray-400">
                  Deleted {site.deleted_at ? new Date(site.deleted_at).toLocaleDateString() : '—'}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
