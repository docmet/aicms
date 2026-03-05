'use client';

import { useEffect, useState, use, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import api from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Globe, Layout, Palette, Trash2, Type, Plus, X } from 'lucide-react';

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

const SECTION_TEMPLATES: Record<string, string> = {
  hero: '# Welcome to {site_name}\n\nYour compelling headline here.',
  body: 'Add your content here. You can use **markdown** formatting.',
  features: '## Features\n\n- Feature 1\n- Feature 2\n- Feature 3',
  cta: '## Ready to get started?\n\nContact us today!',
  footer: '© 2024 {site_name}. All rights reserved.',
};

export default function SiteEditorPage({ params }: { params: Promise<{ site_id: string }> }) {
  const { site_id } = use(params);
  const [site, setSite] = useState<Site | null>(null);
  const [pages, setPages] = useState<Page[]>([]);
  const [currentPage, setCurrentPage] = useState<Page | null>(null);
  const [sections, setSections] = useState<ContentSection[]>([]);
  const [themes, setThemes] = useState<Theme[]>([]);
  const [loading, setLoading] = useState(true);
  const [newSectionType, setNewSectionType] = useState('body');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isAddPageDialogOpen, setIsAddPageDialogOpen] = useState(false);
  const [newPageTitle, setNewPageTitle] = useState('');
  const [newPageSlug, setNewPageSlug] = useState('');
  const { toast } = useToast();
  const router = useRouter();

  const createInitialPage = useCallback(async () => {
    try {
      const response = await api.post(`/sites/${site_id}/pages`, {
        title: 'Home',
        slug: 'home',
        is_published: true,
        order: 0,
      });
      setCurrentPage(response.data);
      setSections([]);
    } catch (error) {
      console.error('Failed to create initial page', error);
    }
  }, [site_id]);

  const fetchData = useCallback(async () => {
    try {
      const [siteRes, pagesRes, themesRes] = await Promise.all([
        api.get(`/sites/${site_id}`),
        api.get(`/sites/${site_id}/pages`),
        api.get('/themes/'),
      ]);

      setSite(siteRes.data);
      setThemes(themesRes.data);

      if (pagesRes.data.length > 0) {
        const firstPage = pagesRes.data[0];
        setCurrentPage(firstPage);
        const sectionsRes = await api.get(`/sites/${site_id}/pages/${firstPage.id}/content`);
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
  }, [site_id, toast, createInitialPage]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleUpdateField = async (field: 'name' | 'slug', value: string) => {
    if (!site) return;
    try {
      await api.patch(`/sites/${site_id}`, {
        name: field === 'name' ? value : site.name,
        slug: field === 'slug' ? value : site.slug,
        theme_slug: site.theme_slug,
      });
      setSite({ ...site, [field]: value });
      toast({
        title: 'Saved',
        description: `${field === 'name' ? 'Site name' : 'URL slug'} updated.`,
      });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      toast({
        title: 'Error',
        description: error.response?.data?.detail || `Failed to update ${field}.`,
        variant: 'destructive',
      });
    }
  };

  const handleAddSection = async () => {
    if (!currentPage || !site) return;
    try {
      const template = SECTION_TEMPLATES[newSectionType] || SECTION_TEMPLATES.body;
      const content = template.replace(/{site_name}/g, site.name);
      const response = await api.post(`/sites/${site_id}/pages/${currentPage.id}/content`, {
        section_type: newSectionType,
        content,
        order: sections.length,
      });
      setSections([...sections, response.data]);
      setIsAddDialogOpen(false);
      toast({ title: 'Success', description: `${newSectionType} section added.` });
    } catch (error) {
      console.error('Failed to add section', error);
      toast({ title: 'Error', description: 'Failed to add section.', variant: 'destructive' });
    }
  };

  const handleDeleteSection = async (sectionId: string) => {
    if (!currentPage) return;
    if (!confirm('Are you sure you want to delete this section?')) return;
    try {
      await api.delete(`/sites/${site_id}/pages/${currentPage.id}/content/${sectionId}`);
      
      // Remove section and reorder remaining sections
      const deletedIndex = sections.findIndex((s) => s.id === sectionId);
      const remainingSections = sections.filter((s) => s.id !== sectionId);
      
      // Update order values for remaining sections
      const reorderedSections = remainingSections.map((s, i) => ({ ...s, order: i }));
      
      // Update backend for sections that changed order
      const updatePromises = remainingSections.map((s, i) => {
        if (i >= deletedIndex && s.order !== i) {
          return api.patch(`/sites/${site_id}/pages/${currentPage.id}/content/${s.id}`, {
            order: i,
          });
        }
        return Promise.resolve();
      });
      
      await Promise.all(updatePromises);
      setSections(reorderedSections);
      toast({ title: 'Deleted', description: 'Section removed and order updated.' });
    } catch (error) {
      console.error('Failed to delete section', error);
      toast({ title: 'Error', description: 'Failed to delete section.', variant: 'destructive' });
    }
  };

  const handleMoveSection = async (sectionId: string, direction: 'up' | 'down') => {
    if (!currentPage) return;
    const index = sections.findIndex((s) => s.id === sectionId);
    if (index === -1) return;
    
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= sections.length) return;
    
    // Get the other section being swapped
    const otherSectionId = sections[newIndex].id;
    
    // Swap sections locally
    const newSections = [...sections];
    [newSections[index], newSections[newIndex]] = [newSections[newIndex], newSections[index]];
    
    // Update order values locally
    const updatedSections = newSections.map((s, i) => ({ ...s, order: i }));
    setSections(updatedSections);
    
    // Update BOTH sections' order in backend
    try {
      await Promise.all([
        api.patch(`/sites/${site_id}/pages/${currentPage.id}/content/${sectionId}`, {
          order: newIndex,
        }),
        api.patch(`/sites/${site_id}/pages/${currentPage.id}/content/${otherSectionId}`, {
          order: index,
        })
      ]);
      toast({ title: 'Success', description: `Section moved ${direction}.` });
    } catch (error) {
      console.error('Failed to move section', error);
      toast({ title: 'Error', description: 'Failed to move section.', variant: 'destructive' });
      // Revert on error
      setSections(sections);
    }
  };

  const handleAddPage = async () => {
    if (!newPageTitle || !newPageSlug) return;
    try {
      const response = await api.post(`/sites/${site_id}/pages`, {
        title: newPageTitle,
        slug: newPageSlug.toLowerCase().replace(/ /g, '-'),
        is_published: true,
        order: pages.length,
      });
      const newPage = response.data;
      setPages([...pages, newPage]);
      setCurrentPage(newPage);
      setSections([]);
      setIsAddPageDialogOpen(false);
      setNewPageTitle('');
      setNewPageSlug('');
      toast({ title: 'Success', description: `Page "${newPageTitle}" created.` });
    } catch (error) {
      console.error('Failed to create page', error);
      toast({ title: 'Error', description: 'Failed to create page.', variant: 'destructive' });
    }
  };

  const handleSwitchPage = async (page: Page) => {
    setCurrentPage(page);
    try {
      const sectionsRes = await api.get(`/sites/${site_id}/pages/${page.id}/content`);
      setSections(sectionsRes.data);
    } catch (error) {
      console.error('Failed to fetch page content', error);
      setSections([]);
    }
  };

  const handleDeletePage = async (pageId: string) => {
    if (!confirm('Are you sure you want to delete this page?')) return;
    try {
      await api.delete(`/sites/${site_id}/pages/${pageId}`);
      const updatedPages = pages.filter((p) => p.id !== pageId);
      setPages(updatedPages);
      if (currentPage?.id === pageId) {
        setCurrentPage(updatedPages[0] || null);
        if (updatedPages[0]) {
          const sectionsRes = await api.get(
            `/sites/${site_id}/pages/${updatedPages[0].id}/content`
          );
          setSections(sectionsRes.data);
        } else {
          setSections([]);
        }
      }
      toast({ title: 'Deleted', description: 'Page removed.' });
    } catch (error) {
      console.error('Failed to delete page', error);
      toast({ title: 'Error', description: 'Failed to delete page.', variant: 'destructive' });
    }
  };

  const handleUpdateContent = async (sectionId: string, content: string) => {
    if (!currentPage) return;
    try {
      await api.patch(`/sites/${site_id}/pages/${currentPage.id}/content/${sectionId}`, {
        content,
      });
      setSections(sections.map((s) => (s.id === sectionId ? { ...s, content } : s)));
      toast({ title: 'Saved', description: 'Content updated.' });
    } catch {
      toast({ title: 'Error', description: 'Failed to save content.', variant: 'destructive' });
    }
  };

  const handleDeleteSite = async () => {
    if (!confirm('Are you sure you want to delete this site? This action cannot be undone.'))
      return;
    try {
      await api.delete(`/sites/${site_id}`);
      toast({ title: 'Site deleted' });
      router.push('/dashboard');
    } catch {
      toast({ title: 'Error', description: 'Failed to delete site.', variant: 'destructive' });
    }
  };

  if (loading)
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  if (!site) return <div>Site not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => router.push('/dashboard')}>
            Back
          </Button>
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
          <TabsTrigger value="content" className="gap-2">
            <Type size={16} /> Content
          </TabsTrigger>
          <TabsTrigger value="theme" className="gap-2">
            <Palette size={16} /> Theme
          </TabsTrigger>
          <TabsTrigger value="settings" className="gap-2">
            <Layout size={16} /> Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="content" className="mt-6 space-y-6">
          {/* Page Selector */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Pages</CardTitle>
                <Dialog open={isAddPageDialogOpen} onOpenChange={setIsAddPageDialogOpen}>
                  <DialogTrigger asChild>
                    <Button size="sm" className="gap-2">
                      <Plus size={16} /> Add Page
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New Page</DialogTitle>
                      <DialogDescription>Add a new page to your site.</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="pageTitle">Page Title</Label>
                        <Input
                          id="pageTitle"
                          value={newPageTitle}
                          onChange={(e) => setNewPageTitle(e.target.value)}
                          placeholder="e.g., About Us"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="pageSlug">URL Slug</Label>
                        <Input
                          id="pageSlug"
                          value={newPageSlug}
                          onChange={(e) => setNewPageSlug(e.target.value)}
                          placeholder="e.g., about"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button onClick={handleAddPage}>Create Page</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {pages.map((page) => (
                  <div key={page.id} className="flex items-center gap-1">
                    <Button
                      variant={currentPage?.id === page.id ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => handleSwitchPage(page)}
                    >
                      {page.title}
                      {page.is_published ? (
                        <span className="ml-2 w-2 h-2 rounded-full bg-green-500" />
                      ) : (
                        <span className="ml-2 w-2 h-2 rounded-full bg-gray-400" />
                      )}
                    </Button>
                    {pages.length > 1 && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={() => handleDeletePage(page.id)}
                      >
                        <X size={14} />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Content Sections */}
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              {currentPage ? `"${currentPage.title}" Content` : 'Content'}
            </h2>
            <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2">
                  <Plus size={16} /> Add Section
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Content Section</DialogTitle>
                  <DialogDescription>Choose a section type to add to your page.</DialogDescription>
                </DialogHeader>
                <div className="py-4">
                  <Select value={newSectionType} onValueChange={setNewSectionType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select section type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hero">Hero (Header)</SelectItem>
                      <SelectItem value="body">Body Text</SelectItem>
                      <SelectItem value="features">Features List</SelectItem>
                      <SelectItem value="cta">Call to Action</SelectItem>
                      <SelectItem value="footer">Footer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <DialogFooter>
                  <Button onClick={handleAddSection}>Add Section</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {sections.length === 0 ? (
            <Card className="p-12 text-center">
              <p className="text-gray-500 mb-4">No content sections yet.</p>
              <Button onClick={() => setIsAddDialogOpen(true)} variant="outline">
                <Plus size={16} className="mr-2" /> Add Your First Section
              </Button>
            </Card>
          ) : (
            sections.map((section) => (
              <Card key={section.id}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <div className="space-y-1">
                    <CardTitle className="text-sm font-medium capitalize">
                      {section.section_type} Section
                    </CardTitle>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => handleMoveSection(section.id, 'up')}
                      disabled={sections.indexOf(section) === 0}
                    >
                      ↑
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => handleMoveSection(section.id, 'down')}
                      disabled={sections.indexOf(section) === sections.length - 1}
                    >
                      ↓
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteSection(section.id)}
                    >
                      <Trash2 size={16} className="text-red-500" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <textarea
                    className="w-full min-h-[100px] p-3 border rounded-md font-mono text-sm"
                    defaultValue={section.content}
                    onBlur={(e) => handleUpdateContent(section.id, e.target.value)}
                  />
                  <p className="text-[10px] text-gray-400 mt-1 italic text-right">
                    Changes auto-save on blur
                  </p>
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
                {themes.map((t) => {
                  const themeColors = {
                    default: { bg: 'bg-blue-500', light: 'bg-blue-100', border: 'border-blue-600' },
                    warm: {
                      bg: 'bg-orange-500',
                      light: 'bg-orange-100',
                      border: 'border-orange-600',
                    },
                    nature: {
                      bg: 'bg-green-500',
                      light: 'bg-green-100',
                      border: 'border-green-600',
                    },
                    dark: { bg: 'bg-slate-800', light: 'bg-slate-700', border: 'border-slate-600' },
                    minimal: { bg: 'bg-gray-600', light: 'bg-gray-100', border: 'border-gray-600' },
                  };
                  const colors =
                    themeColors[t.slug as keyof typeof themeColors] || themeColors.default;

                  return (
                    <button
                      key={t.id}
                      onClick={async () => {
                        setSite({ ...site, theme_slug: t.slug });
                        try {
                          await api.patch(`/sites/${site_id}`, {
                            name: site.name,
                            slug: site.slug,
                            theme_slug: t.slug,
                          });
                          toast({ title: 'Success', description: `Theme changed to ${t.name}.` });
                        } catch (err: unknown) {
                          const error = err as { response?: { data?: { detail?: string } } };
                          toast({
                            title: 'Error',
                            description: error.response?.data?.detail || 'Failed to update theme.',
                            variant: 'destructive',
                          });
                          // Revert on error
                          setSite({ ...site, theme_slug: site.theme_slug });
                        }
                      }}
                      className={`p-4 border-2 rounded-lg text-center transition-all ${
                        site.theme_slug === t.slug
                          ? `${colors.border} ${colors.light}`
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div
                        className={`w-full aspect-video ${colors.light} rounded mb-2 flex items-center justify-center relative overflow-hidden`}
                      >
                        <div className={`absolute inset-0 ${colors.bg} opacity-20`}></div>
                        <div className="relative flex gap-1">
                          <div className={`w-4 h-4 ${colors.bg} rounded-full`}></div>
                          <div className={`w-4 h-4 ${colors.bg} rounded-full opacity-60`}></div>
                          <div className={`w-4 h-4 ${colors.bg} rounded-full opacity-30`}></div>
                        </div>
                      </div>
                      <span className="text-sm font-medium capitalize">{t.name}</span>
                    </button>
                  );
                })}
              </div>
              <p className="text-[10px] text-gray-400 mt-4 italic">Changes auto-save on click</p>
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
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Site Name</Label>
                  <Input
                    id="name"
                    defaultValue={site.name}
                    onBlur={(e) => handleUpdateField('name', e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="slug">URL Slug</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="slug"
                      defaultValue={site.slug}
                      onBlur={(e) =>
                        handleUpdateField('slug', e.target.value.toLowerCase().replace(/ /g, '-'))
                      }
                      required
                    />
                    <span className="text-sm text-gray-500">.aicms.docmet.systems</span>
                  </div>
                </div>
              </div>
              <p className="text-[10px] text-gray-400 mt-4 italic">Changes auto-save on blur</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
