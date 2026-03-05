'use client';

import { useEffect, useState, use, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { usePreviewSSE } from '@/hooks/use-preview-sse';
import { HeroSection } from '@/components/sections/HeroSection';
import { FeaturesSection } from '@/components/sections/FeaturesSection';
import { TestimonialsSection } from '@/components/sections/TestimonialsSection';
import { AboutSection } from '@/components/sections/AboutSection';
import { ContactSection } from '@/components/sections/ContactSection';
import { CtaSection } from '@/components/sections/CtaSection';
import { PricingSection } from '@/components/sections/PricingSection';
import { CustomSection } from '@/components/sections/CustomSection';

interface ContentSection {
  id: string;
  section_type: string;
  content_draft: string | null;
}

interface Site {
  id: string;
  name: string;
  slug: string;
  theme_slug: string;
  theme_slug_draft: string | null;
}

const SECTION_COMPONENTS: Record<string, React.ComponentType<{ content: string }>> = {
  hero: HeroSection,
  features: FeaturesSection,
  testimonials: TestimonialsSection,
  about: AboutSection,
  contact: ContactSection,
  cta: CtaSection,
  pricing: PricingSection,
  custom: CustomSection,
};

export default function DraftPreviewPage({
  params,
}: {
  params: Promise<{ site_id: string; page_id: string }>;
}) {
  const { site_id, page_id } = use(params);
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [site, setSite] = useState<Site | null>(null);
  const [sections, setSections] = useState<ContentSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.replace('/login');
      return;
    }

    Promise.all([
      api.get<Site>(`/sites/${site_id}`),
      api.get<ContentSection[]>(`/sites/${site_id}/pages/${page_id}/content`),
    ])
      .then(([siteRes, contentRes]) => {
        setSite(siteRes.data);
        setSections(contentRes.data);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [site_id, page_id, user, authLoading, router]);

  // Live SSE updates — re-renders instantly on any draft change
  const handleSSEUpdate = useCallback((updated: ContentSection[]) => {
    setSections(updated);
  }, []);

  usePreviewSSE({
    pageId: page_id,
    onSectionsUpdated: handleSSEUpdate,
    enabled: !!user && !authLoading,
  });

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !site) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-300 mb-2">Error</h1>
          <p className="text-gray-500">Could not load preview.</p>
        </div>
      </div>
    );
  }

  const visibleSections = sections.filter(
    (s) => s.content_draft && s.content_draft.trim().length > 0
  );

  return (
    <div
      className="min-h-screen"
      data-theme={site.theme_slug_draft ?? site.theme_slug ?? 'default'}
      style={{
        background: 'var(--color-bg, #ffffff)',
        color: 'var(--color-text, #0f172a)',
        fontFamily: 'var(--font-sans)',
      }}
    >
      {/* Draft banner */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-amber-400 text-amber-900 text-sm font-semibold text-center py-2 flex items-center justify-center gap-3">
        <span>DRAFT PREVIEW — changes not yet published</span>
        <button
          onClick={() => window.close()}
          className="px-3 py-0.5 rounded bg-amber-900/20 hover:bg-amber-900/30 text-xs"
        >
          Close
        </button>
      </div>

      {/* Spacer for banner */}
      <div className="h-9" />

      {visibleSections.length === 0 ? (
        <div className="min-h-[60vh] flex items-center justify-center">
          <div className="text-center">
            <p className="text-2xl font-semibold text-gray-400 mb-2">No draft content yet</p>
            <p className="text-gray-400 text-sm">Add sections in the editor to see a preview.</p>
          </div>
        </div>
      ) : (
        visibleSections.map((section) => {
          const Component = SECTION_COMPONENTS[section.section_type] || CustomSection;
          return (
            <Component key={section.id} content={section.content_draft!} />
          );
        })
      )}

      <footer
        className="py-8 text-center"
        style={{
          borderTop: '1px solid var(--color-card-border, #e2e8f0)',
          background: 'var(--color-card, #f8fafc)',
          color: 'var(--color-text-muted, #64748b)',
        }}
      >
        <p className="text-sm">
          &copy; {new Date().getFullYear()} {site.name}. Powered by{' '}
          <span style={{ color: 'var(--color-primary)' }}>AI CMS</span>
        </p>
      </footer>
    </div>
  );
}
