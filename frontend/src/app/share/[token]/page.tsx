"use client";

import { use, useEffect, useRef, useState } from "react";
import { HeroSection } from "@/components/sections/HeroSection";
import { FeaturesSection } from "@/components/sections/FeaturesSection";
import { TestimonialsSection } from "@/components/sections/TestimonialsSection";
import { AboutSection } from "@/components/sections/AboutSection";
import { ContactSection } from "@/components/sections/ContactSection";
import { CtaSection } from "@/components/sections/CtaSection";
import { PricingSection } from "@/components/sections/PricingSection";
import { CustomSection } from "@/components/sections/CustomSection";

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

interface Section {
  id: string;
  section_type: string;
  content: string;
}

interface SiteData {
  name: string;
  theme_slug: string;
  sections: Section[];
  _expires_at?: string;
}

export default function SharePreviewPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);
  const [data, setData] = useState<SiteData | null>(null);
  const [sections, setSections] = useState<Section[]>([]);
  const [themeSlug, setThemeSlug] = useState<string>("default");
  const [loadStatus, setLoadStatus] = useState<"loading" | "expired" | "error" | "ok">("loading");
  const sseRef = useRef<EventSource | null>(null);

  // Initial data load
  useEffect(() => {
    fetch(`/api/share/${token}`)
      .then(async (res) => {
        if (res.status === 410) { setLoadStatus("expired"); return; }
        if (!res.ok) { setLoadStatus("error"); return; }
        const json = await res.json() as SiteData;
        setData(json);
        setSections(json.sections);
        setThemeSlug(json.theme_slug || "default");
        setLoadStatus("ok");
      })
      .catch(() => setLoadStatus("error"));
  }, [token]);

  // SSE live updates — no auth required, token is in the URL
  useEffect(() => {
    if (loadStatus !== "ok") return;

    const es = new EventSource(`/api/preview/share/${token}`);
    sseRef.current = es;

    es.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data) as {
          type: string;
          sections?: { id: string; section_type: string; content_draft: string | null; order: number }[];
        };
        if (msg.type === "sections_updated" && msg.sections) {
          setSections(
            msg.sections
              .filter((s) => s.content_draft)
              .sort((a, b) => a.order - b.order)
              .map((s) => ({
                id: s.id,
                section_type: s.section_type,
                content: s.content_draft!,
              }))
          );
        } else if (msg.type === "theme_updated") {
          const theme = msg as unknown as { theme_slug_draft?: string | null; theme_slug?: string | null };
          setThemeSlug(theme.theme_slug_draft ?? theme.theme_slug ?? "default");
        }
      } catch {
        // ignore malformed events
      }
    };

    return () => {
      es.close();
      sseRef.current = null;
    };
  }, [token, loadStatus]);

  if (loadStatus === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 rounded-full animate-spin border-violet-200 border-t-violet-600" />
      </div>
    );
  }

  if (loadStatus === "expired") {
    return (
      <div className="min-h-screen flex items-center justify-center text-center">
        <div>
          <p className="text-5xl mb-4">⏰</p>
          <h1 className="text-2xl font-bold mb-2">Preview link expired</h1>
          <p className="text-muted-foreground">Ask the site owner to generate a new preview link.</p>
        </div>
      </div>
    );
  }

  if (loadStatus === "error" || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center text-center">
        <div>
          <h1 className="text-5xl font-bold text-gray-300 mb-4">404</h1>
          <p className="text-muted-foreground">Preview link not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div
      data-theme={themeSlug}
      style={{ background: "var(--color-bg, #fff)", color: "var(--color-text, #0f172a)", fontFamily: "var(--font-sans)" }}
    >
      {/* Draft preview banner — amber like the owner's preview, CTA instead of Close */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-amber-400 text-amber-900 text-sm font-semibold text-center py-2 flex items-center justify-center gap-3">
        <span>DRAFT PREVIEW — changes not yet published</span>
        <a
          href="https://mystorey.io"
          target="_blank"
          rel="noopener noreferrer"
          className="px-3 py-0.5 rounded bg-amber-900/20 hover:bg-amber-900/30 text-xs whitespace-nowrap"
        >
          Build your site →
        </a>
      </div>
      {/* Spacer for fixed bar */}
      <div className="h-9" />

      {sections
        .filter((s) => s.content && s.content.trim().length > 0)
        .map((section) => {
          const Component = SECTION_COMPONENTS[section.section_type] || CustomSection;
          return <Component key={section.id} content={section.content} />;
        })}

      <footer className="py-6 text-center text-sm text-muted-foreground border-t">
        &copy; {new Date().getFullYear()} {data.name}
      </footer>
    </div>
  );
}
