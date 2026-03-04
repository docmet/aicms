'use client';

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import api from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Globe, Save, Trash2, Layout, Type, Palette } from 'lucide-react';

interface Site {
  id: string;
  name: string;
  slug: string;
  theme_slug: string;
}

interface Page {
  id: string;
  title: string;
  slug: string;
  is_published: boolean;
}

interface ContentSection {
  id: string;
  section_type: string;
  content: string;
  order: number;
}

interface Theme {
  id: string;
  name: string;
  slug: string;
}

export default function SiteEditorPage({ params }: { params: Promise<{ site_id: string }> }) {
  const { site_id } = use(params);
  const [site, setSite] = useState<Site | null>(null);
  const [pages, setPages] = useState<Page[]>([]);
  const [currentPage, setCurrentPage] = useState<Page | null>(null);
  const [sections, setSections] = useState<ContentSection[]>([]);
  const [themes, setThemes] = useState<Theme[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  useEffect(() => {
    fetchData();
  }, [site_id, toast]);

  const fetchData = async () => {
    try {
      const [siteRes, pagesRes, themesRes] = await Promise.all([
        api.get(`/sites/${site_id}`),
        api.get(`/api/v1/sites/${site_id}/pages`),
        api.get('/api/v1/themes/'),
      ]);

      setSite(siteRes.data);
      setPages(pagesRes.data);
      setThemes(themesRes.data);

      if (pagesRes.data.length > 0) {
        const firstPage = pagesRes.data[0];
        setCurrentPage(firstPage);
        const sectionsRes = await api.get(`/api/v1/sites/${site_id}/pages/${firstPage.id}/content`);
        setSections(sectionsRes.data);
      } else {
        // Create initial landing page if none exists
        await createInitialPage();
      }
    } catch (error) {
      console.error('Failed to fetch site data', error);
      toast({
        title: 'Error',
        description: 'Failed to load site data.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const createInitialPage = async () => {
    try {
      const response = await api.post(`/api/v1/sites/${site_id}/pages`, {
        title: 'Home',
        slug: 'home',
        is_published: true,
        order: 0,
      });
      setPages([response.data]);
      setCurrentPage(response.data);
      setSections([]);
    } catch (error) {
      console.error('Failed to create initial page', error);
    }
  };

  const handleUpdateSite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!site) return;
    setSaving(true);

    try {
      await api.patch(`/sites/${site_id}`, {
        name: site.name,
        slug: site.slug,
        theme_slug: site.theme_slug,
      });
      toast({ title: 'Success', description: 'Site settings updated.' });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update site.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateContent = async (sectionId: string, content: string) => {
    if (!currentPage) return;
    try {
      await api.patch(`/api/v1/sites/${site_id}/pages/${currentPage.id}/content/${sectionId}`, {
        content,
      });
      setSections(sections.map(s => s.id === sectionId ? { ...s, content } : s));
      toast({ title: 'Saved', description: 'Content updated.' });
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to save content.', variant: 'destructive' });
    }
  };

  const handleDeleteSite = async () => {
    if (!confirm('Are you sure you want to delete this site? This action cannot be undone.')) return;
    try {
      await api.delete(`/sites/${site_id}`);
      toast({ title: 'Site deleted' });
      router.push('/dashboard');
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to delete site.', variant: 'destructive' });
    }
  };

  if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (!site) return <div>Site not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => router.push('/dashboard')}>Back</Button>
          <h1 className="text-3xl font-bold text-gray-900">{site.name}</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <a href={`/${site.slug}`} target="_blank" rel="noopener noreferrer" className="gap-2">
              <Globe size={18} /> View Public Site
            </a>
          </Button>
          <Button variant="destructive" size="icon" onClick={handleDeleteSite}>
            <Trash2 size={18} />
          </Button>
        </div>
      </div>

      <Tabs defaultValue="content" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-3">
          <TabsTrigger value="content" className="gap-2"><Type size={16} /> Content</TabsTrigger>
          <TabsTrigger value="theme" className="gap-2"><Palette size={16} /> Theme</TabsTrigger>
          <TabsTrigger value="settings" className="gap-2"><Layout size={16} /> Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="content" className="mt-6 space-y-6">
          {sections.length === 0 ? (
            <Card className="p-12 text-center">
              <p className="text-gray-500 mb-4">No content sections yet.</p>
              <Button variant="outline">Add Hero Section</Button>
            </Card>
          ) : (
            sections.map((section) => (
              <Card key={section.id}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <div className="space-y-1">
                    <CardTitle className="text-sm font-medium capitalize">{section.section_type} Section</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <textarea
                    className="w-full min-h-[100px] p-3 border rounded-md font-mono text-sm"
                    defaultValue={section.content}
                    onBlur={(e) => handleUpdateContent(section.id, e.target.value)}
                  />
                  <p className="text-[10px] text-gray-400 mt-1 italic text-right">Changes auto-save on blur</p>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="theme" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Choose a Theme</CardTitle>
              <CardDescription>Select a visual style for your landing page.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {themes.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setSite({ ...site, theme_slug: t.slug })}
                    className={`p-4 border-2 rounded-lg text-center transition-all ${
                      site.theme_slug === t.slug ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="w-full aspect-video bg-gray-100 rounded mb-2 flex items-center justify-center">
                      <Palette className={site.theme_slug === t.slug ? 'text-blue-600' : 'text-gray-400'} />
                    </div>
                    <span className="text-sm font-medium capitalize">{t.name}</span>
                  </button>
                ))}
              </div>
              <div className="mt-6 flex justify-end">
                <Button onClick={handleUpdateSite} disabled={saving} className="gap-2">
                  <Save size={18} /> {saving ? 'Saving...' : 'Save Theme'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Site Settings</CardTitle>
              <CardDescription>Update your site name and public URL slug.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateSite} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Site Name</Label>
                  <Input
                    id="name"
                    value={site.name}
                    onChange={(e) => setSite({ ...site, name: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="slug">URL Slug</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="slug"
                      value={site.slug}
                      onChange={(e) => setSite({ ...site, slug: e.target.value.toLowerCase().replace(/ /g, '-') })}
                      required
                    />
                    <span className="text-sm text-gray-500">.aicms.docmet.systems</span>
                  </div>
                </div>
                <div className="pt-4 flex justify-end">
                  <Button type="submit" disabled={saving} className="gap-2">
                    <Save size={18} /> {saving ? 'Saving...' : 'Save Settings'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
