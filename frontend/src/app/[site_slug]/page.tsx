"use client";

import { useEffect, useState, use } from "react";
import api from "@/lib/api";
import { HeroSection } from "@/components/sections/HeroSection";
import { FeaturesSection } from "@/components/sections/FeaturesSection";
import { TestimonialsSection } from "@/components/sections/TestimonialsSection";
import { AboutSection } from "@/components/sections/AboutSection";
import { ContactSection } from "@/components/sections/ContactSection";
import { CtaSection } from "@/components/sections/CtaSection";
import { PricingSection } from "@/components/sections/PricingSection";
import { CustomSection } from "@/components/sections/CustomSection";

interface ContentSection {
  id: string;
  section_type: string;
  content: string;
}

interface SiteData {
  name: string;
  theme_slug: string;
  page_title?: string;
  sections: ContentSection[];
}

const SECTION_COMPONENTS: Record<
  string,
  React.ComponentType<{ content: string }>
> = {
  hero: HeroSection,
  features: FeaturesSection,
  testimonials: TestimonialsSection,
  about: AboutSection,
  contact: ContactSection,
  cta: CtaSection,
  pricing: PricingSection,
  custom: CustomSection,
};

export default function PublicSitePage({
  params,
}: {
  params: Promise<{ site_slug: string }>;
}) {
  const { site_slug } = use(params);
  const [data, setData] = useState<SiteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchSite = async () => {
      try {
        const response = await api.get(`/public/sites/${site_slug}`);
        setData(response.data);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchSite();
  }, [site_slug]);

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
          <p className="text-xl text-gray-500">Site not found.</p>
        </div>
      </div>
    );
  }

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
      {data.sections
        .filter((s) => s.content && s.content.trim().length > 0)
        .map((section) => {
          const Component =
            SECTION_COMPONENTS[section.section_type] || CustomSection;
          return (
            <Component key={section.id} content={section.content} />
          );
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
          &copy; {new Date().getFullYear()} {data.name}. Powered by{" "}
          <span style={{ color: "var(--color-primary)" }}>AI CMS</span>
        </p>
      </footer>
    </div>
  );
}
