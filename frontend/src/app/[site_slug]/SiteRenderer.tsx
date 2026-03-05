"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { SiteNavBar } from "@/components/sections/SiteNavBar";
import { HeroSection } from "@/components/sections/HeroSection";
import { FeaturesSection } from "@/components/sections/FeaturesSection";
import { TestimonialsSection } from "@/components/sections/TestimonialsSection";
import { AboutSection } from "@/components/sections/AboutSection";
import { ContactSection } from "@/components/sections/ContactSection";
import { CtaSection } from "@/components/sections/CtaSection";
import { PricingSection } from "@/components/sections/PricingSection";
import { CustomSection } from "@/components/sections/CustomSection";

interface NavPage {
  title: string;
  slug: string;
}

interface ContentSection {
  id: string;
  section_type: string;
  content: string;
}

interface SiteData {
  name: string;
  theme_slug: string;
  pages: NavPage[];
  page_title?: string;
  page_slug?: string;
  sections: ContentSection[];
  show_badge?: boolean;
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

interface SiteRendererProps {
  siteSlug: string;
  pageSlug?: string; // undefined = homepage
}

export function SiteRenderer({ siteSlug, pageSlug }: SiteRendererProps) {
  const [data, setData] = useState<SiteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const endpoint = pageSlug
      ? `/public/sites/${siteSlug}/pages/${pageSlug}`
      : `/public/sites/${siteSlug}`;

    api
      .get(endpoint)
      .then((r) => setData(r.data as SiteData))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [siteSlug, pageSlug]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div
          className="w-8 h-8 border-4 rounded-full animate-spin"
          style={{
            borderColor: "var(--color-card-border, #e2e8f0)",
            borderTopColor: "var(--color-primary, #3b82f6)",
          }}
        />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-gray-300 mb-4">404</h1>
          <p className="text-xl text-gray-500">Page not found.</p>
        </div>
      </div>
    );
  }

  const hasNav = data.pages.length > 1;

  return (
    <div
      className="min-h-screen"
      data-theme={data.theme_slug || "default"}
      style={{
        background: "var(--color-bg, #ffffff)",
        color: "var(--color-text, #0f172a)",
        fontFamily: "var(--font-sans)",
      }}
    >
      {hasNav && (
        <SiteNavBar
          siteName={data.name}
          siteSlug={siteSlug}
          pages={data.pages}
          currentPageSlug={pageSlug ?? data.page_slug}
        />
      )}

      {/* Spacer for fixed nav */}
      {hasNav && <div className="h-16" />}

      {data.sections
        .filter((s) => s.content && s.content.trim().length > 0)
        .map((section) => {
          const Component = SECTION_COMPONENTS[section.section_type] || CustomSection;
          return <Component key={section.id} content={section.content} />;
        })}

      <footer
        className="py-8 text-center"
        style={{
          borderTop: "1px solid var(--color-card-border, #e2e8f0)",
          background: "var(--color-card, #f8fafc)",
          color: "var(--color-text-muted, #64748b)",
        }}
      >
        <p className="text-sm">
          &copy; {new Date().getFullYear()} {data.name}
        </p>
        {data.show_badge && (
          <a
            href="https://mystorey.io"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 mt-3 px-3 py-1.5 rounded-full text-xs font-medium border transition-opacity hover:opacity-80"
            style={{
              borderColor: "var(--color-card-border, #e2e8f0)",
              color: "var(--color-text-muted, #64748b)",
              background: "var(--color-bg, #ffffff)",
            }}
          >
            <span style={{ color: "#7c3aed" }}>✦</span>
            Made with MyStorey
          </a>
        )}
      </footer>
    </div>
  );
}
