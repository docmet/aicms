"use client";

import { useEffect, useState, use, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import api from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  Globe,
  Layout,
  Palette,
  Trash2,
  Type,
  Plus,
  X,
  Send,
  History,
  ChevronUp,
  ChevronDown,
  RotateCcw,
} from "lucide-react";
import {
  HeroEditor,
  FeaturesEditor,
  TestimonialsEditor,
  AboutEditor,
  ContactEditor,
  CtaEditor,
  PricingEditor,
  CustomEditor,
} from "@/components/admin/section-editors";
import { usePreviewSSE, SSESection } from "@/hooks/use-preview-sse";

// ── Types ─────────────────────────────────────────────────────────────────────

interface Site {
  id: string;
  name: string;
  slug: string;
  theme_slug: string;
  theme_slug_draft: string | null;
}

interface Page {
  id: string;
  title: string;
  slug: string;
  is_published: boolean;
  last_published_at?: string;
}

interface ContentSection {
  id: string;
  section_type: string;
  content_draft: string | null;
  content_published: string | null;
  has_unpublished_changes: boolean;
  order: number;
}

interface Theme {
  id: string;
  name: string;
  slug: string;
}

interface PageVersion {
  id: string;
  version_number: number;
  published_at: string;
  label?: string;
}

// ── Section type config ────────────────────────────────────────────────────────

const SECTION_TYPES = [
  { value: "hero", label: "Hero" },
  { value: "features", label: "Features" },
  { value: "testimonials", label: "Testimonials" },
  { value: "about", label: "About" },
  { value: "contact", label: "Contact" },
  { value: "cta", label: "Call to Action" },
  { value: "pricing", label: "Pricing" },
  { value: "custom", label: "Custom" },
];

const SECTION_DEFAULTS: Record<string, object> = {
  hero: { headline: "", subheadline: "", badge: "", cta_primary: { label: "Get Started", href: "#" }, cta_secondary: { label: "Learn More", href: "#" } },
  features: { headline: "", subheadline: "", items: [{ icon: "⭐", title: "", description: "" }] },
  testimonials: { headline: "", items: [{ quote: "", name: "", role: "", company: "" }] },
  about: { headline: "", body: "", stats: [] },
  contact: { headline: "Get in Touch", email: "", phone: "", address: "", hours: "" },
  cta: { headline: "", subheadline: "", button_label: "Get Started", button_href: "#" },
  pricing: { headline: "", subheadline: "", plans: [] },
  custom: { title: "", content: "" },
};

// ── Helpers ────────────────────────────────────────────────────────────────────

function parseContent(raw: string | null): Record<string, unknown> {
  if (!raw) return {};
  try { return JSON.parse(raw) as Record<string, unknown>; }
  catch { return {}; }
}

const THEME_COLORS: Record<string, { ring: string; swatch: string }> = {
  modern:  { ring: "ring-blue-500",  swatch: "bg-blue-500" },
  warm:    { ring: "ring-orange-500", swatch: "bg-orange-500" },
  startup: { ring: "ring-emerald-500", swatch: "bg-emerald-500" },
  minimal: { ring: "ring-zinc-500",  swatch: "bg-zinc-600" },
  dark:    { ring: "ring-violet-500", swatch: "bg-violet-700" },
};

// ── Section editor dispatcher ─────────────────────────────────────────────────

function SectionEditorDispatch({
  section,
  siteId,
  pageId,
  onSaved,
}: {
  section: ContentSection;
  siteId: string;
  pageId: string;
  onSaved: (updated: ContentSection) => void;
}) {
  const { toast } = useToast();
  const [data, setData] = useState<Record<string, unknown>>(
    parseContent(section.content_draft)
  );
  const [saving, setSaving] = useState(false);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isDirty = useRef(false);

  // Sync data when section.content_draft changes externally (SSE, revert, publish)
  // Only applies when there's no in-progress local edit.
  useEffect(() => {
    if (!isDirty.current) {
      setData(parseContent(section.content_draft));
    }
  }, [section.content_draft]);

  // Debounced auto-save on every data change
  const handleChange = useCallback(
    (next: Record<string, unknown>) => {
      isDirty.current = true;
      setData(next);
      if (saveTimer.current) clearTimeout(saveTimer.current);
      saveTimer.current = setTimeout(async () => {
        setSaving(true);
        try {
          const res = await api.patch(
            `/sites/${siteId}/pages/${pageId}/content/${section.id}`,
            { content_draft: JSON.stringify(next) }
          );
          onSaved(res.data as ContentSection);
        } catch {
          toast({ title: "Save failed", variant: "destructive" });
        } finally {
          setSaving(false);
          isDirty.current = false;
        }
      }, 800);
    },
    [siteId, pageId, section.id, onSaved, toast]
  );

  const editorProps = { content: data as never, onChange: handleChange as never };

  return (
    <div className="relative">
      {saving && (
        <span className="absolute top-0 right-0 text-[10px] text-muted-foreground animate-pulse">
          saving…
        </span>
      )}
      {section.section_type === "hero" && <HeroEditor {...editorProps} />}
      {section.section_type === "features" && <FeaturesEditor {...editorProps} />}
      {section.section_type === "testimonials" && <TestimonialsEditor {...editorProps} />}
      {section.section_type === "about" && <AboutEditor {...editorProps} />}
      {section.section_type === "contact" && <ContactEditor {...editorProps} />}
      {section.section_type === "cta" && <CtaEditor {...editorProps} />}
      {section.section_type === "pricing" && <PricingEditor {...editorProps} />}
      {section.section_type === "custom" && <CustomEditor {...editorProps} />}
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function SiteEditorPage({
  params,
}: {
  params: Promise<{ site_id: string }>;
}) {
  const { site_id } = use(params);
  const [site, setSite] = useState<Site | null>(null);
  const [pages, setPages] = useState<Page[]>([]);
  const [currentPage, setCurrentPage] = useState<Page | null>(null);
  const [sections, setSections] = useState<ContentSection[]>([]);
  const [themes, setThemes] = useState<Theme[]>([]);
  const [versions, setVersions] = useState<PageVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [newSectionType, setNewSectionType] = useState("hero");
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isAddPageDialogOpen, setIsAddPageDialogOpen] = useState(false);
  const [newPageTitle, setNewPageTitle] = useState("");
  const [newPageSlug, setNewPageSlug] = useState("");
  const { toast } = useToast();
  const router = useRouter();

  // ── BroadcastChannel: push updates to preview tab ────────────────────────
  // Refs always hold the latest values — no stale-closure issues.
  const sectionsRef = useRef<ContentSection[]>(sections);
  sectionsRef.current = sections;
  const siteRef = useRef<Site | null>(site);
  siteRef.current = site;
  const currentPageRef = useRef<Page | null>(currentPage);
  currentPageRef.current = currentPage;

  // Persistent channel — created once per page, kept open while editor is mounted.
  // Avoids the timing issue of creating+closing a channel on every broadcast.
  const broadcastChannelRef = useRef<BroadcastChannel | null>(null);
  const currentPageId = currentPage?.id;
  useEffect(() => {
    if (!currentPageId) return;
    broadcastChannelRef.current?.close();
    broadcastChannelRef.current = new BroadcastChannel(`preview-${currentPageId}`);
    return () => {
      broadcastChannelRef.current?.close();
      broadcastChannelRef.current = null;
    };
  }, [currentPageId]);

  const broadcastToPreview = useCallback((
    overrideSections?: ContentSection[],
    overrideTheme?: string,
  ) => {
    const ch = broadcastChannelRef.current;
    if (!ch) return;
    ch.postMessage({
      type: 'preview_updated',
      sections: overrideSections ?? sectionsRef.current,
      theme: overrideTheme ?? (siteRef.current?.theme_slug_draft ?? siteRef.current?.theme_slug ?? 'default'),
    });
  }, []); // stable — reads from refs at call time

  // ── Data fetching ────────────────────────────────────────────────────────

  const fetchSections = useCallback(
    async (pageId: string) => {
      const res = await api.get(
        `/sites/${site_id}/pages/${pageId}/content?include_deleted=false`
      );
      const data = res.data as ContentSection[];
      setSections(data);
      broadcastToPreview(data);
    },
    [site_id, broadcastToPreview]
  );

  const fetchVersions = useCallback(
    async (pageId: string) => {
      try {
        const res = await api.get(`/sites/${site_id}/pages/${pageId}/versions`);
        setVersions(res.data as PageVersion[]);
      } catch {
        setVersions([]);
      }
    },
    [site_id]
  );

  const fetchData = useCallback(async () => {
    try {
      const [siteRes, pagesRes, themesRes] = await Promise.all([
        api.get(`/sites/${site_id}`),
        api.get(`/sites/${site_id}/pages`),
        api.get("/themes/"),
      ]);
      setSite(siteRes.data as Site);
      setThemes(themesRes.data as Theme[]);

      const fetchedPages = pagesRes.data as Page[];
      if (fetchedPages.length > 0) {
        setPages(fetchedPages);
        setCurrentPage(fetchedPages[0]);
        await fetchSections(fetchedPages[0].id);
        await fetchVersions(fetchedPages[0].id);
      } else {
        // Auto-create home page
        const res = await api.post(`/sites/${site_id}/pages`, {
          title: "Home", slug: "home", is_published: true, order: 0,
        });
        const newPage = res.data as Page;
        setPages([newPage]);
        setCurrentPage(newPage);
        setSections([]);
      }
    } catch {
      toast({ title: "Error", description: "Failed to load site.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  }, [site_id, fetchSections, fetchVersions, toast]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // ── SSE: pick up MCP edits in real-time ──────────────────────────────────
  const handleSSESections = useCallback((updated: SSESection[]) => {
    const prevMap = new Map(sectionsRef.current.map((s) => [s.id, s]));
    const next: ContentSection[] = updated.map((s) => ({
      ...s,
      content_published: prevMap.get(s.id)?.content_published ?? null,
      content_draft: s.content_draft,
    }));
    setSections(next);
    broadcastToPreview(next);
  }, [broadcastToPreview]);

  const handleSSETheme = useCallback((themeSlugDraft: string | null, themeSlug: string | null) => {
    setSite((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        theme_slug_draft: themeSlugDraft,
        ...(themeSlug ? { theme_slug: themeSlug } : {}),
      };
    });
    // Broadcast outside the state setter — side effects must not run inside setSite
    broadcastToPreview(undefined, themeSlugDraft ?? themeSlug ?? siteRef.current?.theme_slug ?? 'default');
  }, [broadcastToPreview]);

  usePreviewSSE({
    pageId: currentPage?.id,
    onSectionsUpdated: handleSSESections,
    onThemeUpdated: handleSSETheme,
  });

  // ── Publish ──────────────────────────────────────────────────────────────

  const handlePublish = async () => {
    if (!currentPage) return;
    setPublishing(true);
    try {
      const res = await api.post(
        `/sites/${site_id}/pages/${currentPage.id}/publish`
      );
      setCurrentPage(res.data as Page);
      // Refresh sections, versions, and site (publish clears theme_slug_draft)
      const [, , siteRes] = await Promise.all([
        fetchSections(currentPage.id),
        fetchVersions(currentPage.id),
        api.get(`/sites/${site_id}`),
      ]);
      setSite(siteRes.data as Site);
      toast({ title: "Published!", description: "All changes are now live." });
    } catch {
      toast({ title: "Publish failed", variant: "destructive" });
    } finally {
      setPublishing(false);
    }
  };

  // ── Revert to version ────────────────────────────────────────────────────

  const handleRevert = async (versionId: string) => {
    if (!currentPage) return;
    if (!confirm("Revert to this version? All draft changes (content + theme) will be overwritten.")) return;
    try {
      await api.post(`/sites/${site_id}/pages/${currentPage.id}/revert/${versionId}`);
      // Clear theme draft in parallel with section fetch so preview gets the right theme
      const clearTheme = site?.theme_slug_draft
        ? api.patch(`/sites/${site_id}`, { theme_slug_draft: null })
        : Promise.resolve();
      const [sectionsData] = await Promise.all([
        api.get(`/sites/${site_id}/pages/${currentPage.id}/content?include_deleted=false`),
        clearTheme,
      ]);
      const data = sectionsData.data as ContentSection[];
      setSections(data);
      if (site?.theme_slug_draft) {
        setSite((prev) => prev ? { ...prev, theme_slug_draft: null } : prev);
      }
      const publishedTheme = site?.theme_slug ?? 'default';
      broadcastToPreview(data, publishedTheme);
      toast({ title: "Reverted", description: "Draft restored from version. Publish to go live." });
    } catch {
      toast({ title: "Revert failed", variant: "destructive" });
    }
  };

  // ── Section CRUD ─────────────────────────────────────────────────────────

  const handleAddSection = async () => {
    if (!currentPage) return;
    try {
      const defaults = SECTION_DEFAULTS[newSectionType] || {};
      const res = await api.post(
        `/sites/${site_id}/pages/${currentPage.id}/content`,
        {
          section_type: newSectionType,
          content_draft: JSON.stringify(defaults),
          order: sections.length,
        }
      );
      setSections([...sections, res.data as ContentSection]);
      setIsAddDialogOpen(false);
      toast({ title: "Section added" });
    } catch {
      toast({ title: "Error", description: "Failed to add section.", variant: "destructive" });
    }
  };

  const handleDeleteSection = async (sectionId: string) => {
    if (!currentPage) return;
    if (!confirm("Delete this section?")) return;
    try {
      await api.delete(
        `/sites/${site_id}/pages/${currentPage.id}/content/${sectionId}`
      );
      const remaining = sections
        .filter((s) => s.id !== sectionId)
        .map((s, i) => ({ ...s, order: i }));
      setSections(remaining);
      toast({ title: "Section deleted" });
    } catch {
      toast({ title: "Error", description: "Failed to delete section.", variant: "destructive" });
    }
  };

  const handleMove = async (sectionId: string, direction: "up" | "down") => {
    if (!currentPage) return;
    const idx = sections.findIndex((s) => s.id === sectionId);
    const newIdx = direction === "up" ? idx - 1 : idx + 1;
    if (newIdx < 0 || newIdx >= sections.length) return;

    const next = [...sections];
    [next[idx], next[newIdx]] = [next[newIdx], next[idx]];
    const updated = next.map((s, i) => ({ ...s, order: i }));
    setSections(updated);

    try {
      await Promise.all([
        api.patch(`/sites/${site_id}/pages/${currentPage.id}/content/${sectionId}`, { order: newIdx }),
        api.patch(`/sites/${site_id}/pages/${currentPage.id}/content/${sections[newIdx].id}`, { order: idx }),
      ]);
    } catch {
      setSections(sections); // revert
      toast({ title: "Failed to reorder", variant: "destructive" });
    }
  };

  // ── Page management ──────────────────────────────────────────────────────

  const handleSwitchPage = async (page: Page) => {
    setCurrentPage(page);
    await fetchSections(page.id);
    await fetchVersions(page.id);
  };

  const handleAddPage = async () => {
    if (!newPageTitle || !newPageSlug) return;
    try {
      const res = await api.post(`/sites/${site_id}/pages`, {
        title: newPageTitle,
        slug: newPageSlug.toLowerCase().replace(/ /g, "-"),
        is_published: true,
        order: pages.length,
      });
      const page = res.data as Page;
      setPages([...pages, page]);
      await handleSwitchPage(page);
      setIsAddPageDialogOpen(false);
      setNewPageTitle("");
      setNewPageSlug("");
      toast({ title: `Page "${newPageTitle}" created` });
    } catch {
      toast({ title: "Error", description: "Failed to create page.", variant: "destructive" });
    }
  };

  const handleDeletePage = async (pageId: string) => {
    if (!confirm("Delete this page?")) return;
    try {
      await api.delete(`/sites/${site_id}/pages/${pageId}`);
      const remaining = pages.filter((p) => p.id !== pageId);
      setPages(remaining);
      if (currentPage?.id === pageId) {
        if (remaining.length > 0) await handleSwitchPage(remaining[0]);
        else { setCurrentPage(null); setSections([]); }
      }
      toast({ title: "Page deleted" });
    } catch {
      toast({ title: "Error", description: "Failed to delete page.", variant: "destructive" });
    }
  };

  // ── Site settings ────────────────────────────────────────────────────────

  const handleUpdateSiteField = async (field: "name" | "slug", value: string) => {
    if (!site) return;
    try {
      await api.patch(`/sites/${site_id}`, { ...site, [field]: value });
      setSite({ ...site, [field]: value });
      toast({ title: "Saved" });
    } catch {
      toast({ title: "Error", description: `Failed to update ${field}.`, variant: "destructive" });
    }
  };

  const handleThemeChange = async (slug: string) => {
    if (!site) return;
    // Clicking the already-published theme restores (clears the draft)
    const newDraft = slug === site.theme_slug ? null : slug;
    setSite({ ...site, theme_slug_draft: newDraft });
    broadcastToPreview(undefined, newDraft ?? site.theme_slug);
    try {
      await api.patch(`/sites/${site_id}`, { theme_slug_draft: newDraft });
      toast({
        title: newDraft ? "Theme staged" : "Theme restored",
        description: newDraft ? "Publish to make this theme live." : "Draft cleared — back to published theme.",
      });
    } catch {
      setSite(site);
      broadcastToPreview(undefined, site.theme_slug_draft ?? site.theme_slug);
      toast({ title: "Error", description: "Failed to update theme.", variant: "destructive" });
    }
  };

  // ── Derived state ────────────────────────────────────────────────────────

  const hasUnpublished =
    sections.some((s) => s.has_unpublished_changes) ||
    (!!site?.theme_slug_draft && site.theme_slug_draft !== site.theme_slug);

  if (loading)
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" />
      </div>
    );
  if (!site) return <div>Site not found</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={() => router.push("/dashboard")}>
            Back
          </Button>
          <h1 className="text-2xl font-bold">{site.name}</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <a
              href={currentPage ? `/preview/${site_id}/${currentPage.id}` : `/${site.slug}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Globe size={16} className="mr-2" /> Preview Draft
            </a>
          </Button>
          <Button
            onClick={handlePublish}
            disabled={publishing || !currentPage || !hasUnpublished}
            className="gap-2"
            variant={hasUnpublished ? "default" : "outline"}
          >
            <Send size={16} />
            {publishing ? "Publishing…" : hasUnpublished ? "Publish Changes" : "Published"}
          </Button>
        </div>
      </div>

      <Tabs
        defaultValue="content"
        className="w-full"
        onValueChange={(tab) => {
          if (tab === "content" && currentPage) {
            fetchSections(currentPage.id);
            api.get(`/sites/${site_id}`).then((r) => setSite(r.data as Site)).catch(() => {});
          } else if (tab === "theme") {
            api.get(`/sites/${site_id}`).then((r) => setSite(r.data as Site)).catch(() => {});
          }
        }}
      >
        <TabsList className="grid w-full max-w-sm grid-cols-3">
          <TabsTrigger value="content">
            <Type size={14} className="mr-1.5" /> Content
          </TabsTrigger>
          <TabsTrigger value="theme">
            <Palette size={14} className="mr-1.5" /> Theme
          </TabsTrigger>
          <TabsTrigger value="settings">
            <Layout size={14} className="mr-1.5" /> Settings
          </TabsTrigger>
        </TabsList>

        {/* ── Content tab ──────────────────────────────────────────────── */}
        <TabsContent value="content" className="mt-6 space-y-6">

          {/* Page tabs */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Pages</CardTitle>
                <Dialog open={isAddPageDialogOpen} onOpenChange={setIsAddPageDialogOpen}>
                  <DialogTrigger asChild>
                    <Button size="sm" variant="outline">
                      <Plus size={14} className="mr-1" /> Add Page
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New Page</DialogTitle>
                      <DialogDescription>Add a new page to your site.</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label>Page Title</Label>
                        <Input value={newPageTitle} onChange={(e) => setNewPageTitle(e.target.value)} placeholder="About Us" />
                      </div>
                      <div className="space-y-2">
                        <Label>URL Slug</Label>
                        <Input value={newPageSlug} onChange={(e) => setNewPageSlug(e.target.value)} placeholder="about" />
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
                      variant={currentPage?.id === page.id ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleSwitchPage(page)}
                    >
                      {page.title}
                      <span className={`ml-2 w-2 h-2 rounded-full ${page.is_published ? "bg-green-400" : "bg-muted-foreground"}`} />
                    </Button>
                    {pages.length > 1 && (
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleDeletePage(page.id)}>
                        <X size={13} />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Publish bar */}
          {currentPage && (
            <div className="flex items-center justify-between p-3 rounded-lg border bg-muted/40">
              <div className="flex items-center gap-3">
                <div>
                  {hasUnpublished ? (
                    <Badge variant="secondary" className="bg-amber-100 text-amber-800 border-amber-200">
                      Unpublished changes
                    </Badge>
                  ) : (
                    <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-200">
                      All changes published
                    </Badge>
                  )}
                </div>
                {currentPage.last_published_at && (
                  <span className="text-xs text-muted-foreground">
                    Last published {new Date(currentPage.last_published_at).toLocaleDateString()}
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                {versions.length > 0 && (
                  <Button variant="ghost" size="sm" onClick={() => setShowVersions((v) => !v)}>
                    <History size={14} className="mr-1.5" /> History ({versions.length})
                  </Button>
                )}
                <Button size="sm" onClick={handlePublish} disabled={publishing || !hasUnpublished}>
                  <Send size={14} className="mr-1.5" />
                  {publishing ? "Publishing…" : "Publish"}
                </Button>
              </div>
            </div>
          )}

          {/* Version history panel */}
          {showVersions && versions.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Version History</CardTitle>
                <CardDescription>Up to 5 versions kept. Reverting updates the draft — publish to go live.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {versions.map((v) => (
                    <div key={v.id} className="flex items-center justify-between p-2 rounded-md border">
                      <div>
                        <span className="text-sm font-medium">v{v.version_number}</span>
                        <span className="ml-2 text-xs text-muted-foreground">
                          {new Date(v.published_at).toLocaleString()}
                        </span>
                        {v.label && <span className="ml-2 text-xs text-muted-foreground">— {v.label}</span>}
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRevert(v.id)}
                      >
                        <RotateCcw size={13} className="mr-1.5" /> Restore
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Sections */}
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">
              {currentPage ? `"${currentPage.title}" Sections` : "Sections"}
            </h2>
            <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus size={14} className="mr-1.5" /> Add Section
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Section</DialogTitle>
                  <DialogDescription>Choose a section type to add to this page.</DialogDescription>
                </DialogHeader>
                <div className="py-4">
                  <Select value={newSectionType} onValueChange={setNewSectionType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {SECTION_TYPES.map((t) => (
                        <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <DialogFooter>
                  <Button onClick={handleAddSection}>Add</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {sections.length === 0 ? (
            <Card className="p-12 text-center">
              <p className="text-muted-foreground mb-4">No sections yet.</p>
              <Button onClick={() => setIsAddDialogOpen(true)} variant="outline">
                <Plus size={14} className="mr-2" /> Add First Section
              </Button>
            </Card>
          ) : (
            sections.map((section, idx) => (
              <Card key={section.id} className={section.has_unpublished_changes ? "border-amber-300" : ""}>
                <CardHeader className="flex flex-row items-center justify-between py-3 px-4">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold capitalize">{section.section_type}</span>
                    {section.has_unpublished_changes && (
                      <Badge variant="secondary" className="text-[10px] bg-amber-100 text-amber-700 border-amber-200 py-0">
                        draft
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleMove(section.id, "up")} disabled={idx === 0}>
                      <ChevronUp size={14} />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleMove(section.id, "down")} disabled={idx === sections.length - 1}>
                      <ChevronDown size={14} />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive" onClick={() => handleDeleteSection(section.id)}>
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="px-4 pb-4">
                  <SectionEditorDispatch
                    section={section}
                    siteId={site_id}
                    pageId={currentPage!.id}
                    onSaved={(updated) => {
                      const next = sectionsRef.current.map((s) => (s.id === updated.id ? updated : s));
                      setSections(next);
                      broadcastToPreview(next);
                    }}
                  />
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        {/* ── Theme tab ─────────────────────────────────────────────────── */}
        <TabsContent value="theme" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Choose a Theme</CardTitle>
              <CardDescription>Select a visual style for your public site.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                {themes.map((t) => {
                  const colors = THEME_COLORS[t.slug] || THEME_COLORS.modern;
                  const effectiveTheme = site.theme_slug_draft ?? site.theme_slug;
                  const active = effectiveTheme === t.slug;
                  const isDraft = site.theme_slug_draft === t.slug && site.theme_slug !== t.slug;
                  return (
                    <button
                      key={t.id}
                      onClick={() => handleThemeChange(t.slug)}
                      className={`p-4 border-2 rounded-xl text-center transition-all hover:shadow-md ${active ? `${colors.ring} ring-2` : "border-border hover:border-muted-foreground"}`}
                    >
                      <div className={`w-8 h-8 rounded-full mx-auto mb-2 ${colors.swatch}`} />
                      <span className="text-sm font-medium">{t.name}</span>
                      {isDraft && (
                        <span className="block text-[9px] text-amber-600 font-semibold mt-0.5">draft</span>
                      )}
                    </button>
                  );
                })}
              </div>
              <p className="text-[11px] text-muted-foreground mt-4">
                {site.theme_slug_draft && site.theme_slug_draft !== site.theme_slug
                  ? `Draft: "${site.theme_slug_draft}" — publish to make live, or revert via Version History to undo all changes.`
                  : "Click a theme to stage it as a draft. Publish to make it live."}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Settings tab ──────────────────────────────────────────────── */}
        <TabsContent value="settings" className="mt-6 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Site Settings</CardTitle>
              <CardDescription>Update your site name and public URL slug.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Site Name</Label>
                <Input
                  defaultValue={site.name}
                  onBlur={(e) => handleUpdateSiteField("name", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>URL Slug</Label>
                <div className="flex items-center gap-2">
                  <Input
                    defaultValue={site.slug}
                    onBlur={(e) =>
                      handleUpdateSiteField("slug", e.target.value.toLowerCase().replace(/\s+/g, "-"))
                    }
                  />
                  <span className="text-sm text-muted-foreground whitespace-nowrap">.aicms.docmet.systems</span>
                </div>
              </div>
              <p className="text-[11px] text-muted-foreground">Saves automatically on blur</p>
            </CardContent>
          </Card>
          <Card className="border-destructive/50">
            <CardHeader>
              <CardTitle className="text-destructive">Danger Zone</CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                variant="destructive"
                onClick={async () => {
                  if (!confirm("Delete this site permanently?")) return;
                  await api.delete(`/sites/${site_id}`);
                  router.push("/dashboard");
                }}
              >
                <Trash2 size={16} className="mr-2" /> Delete Site
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
