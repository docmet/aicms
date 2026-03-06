"use client";

import { use, useEffect, useState } from "react";
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

interface SiteData {
  name: string;
  theme_slug: string;
  sections: { id: string; section_type: string; content: string }[];
  _expires_at?: string;
}

export default function SharePreviewPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);
  const [data, setData] = useState<SiteData | null>(null);
  const [status, setStatus] = useState<"loading" | "expired" | "error" | "ok">("loading");

  useEffect(() => {
    fetch(`/api/share/${token}`)
      .then(async (res) => {
        if (res.status === 410) { setStatus("expired"); return; }
        if (!res.ok) { setStatus("error"); return; }
        setData(await res.json() as SiteData);
        setStatus("ok");
      })
      .catch(() => setStatus("error"));
  }, [token]);

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 rounded-full animate-spin border-violet-200 border-t-violet-600" />
      </div>
    );
  }

  if (status === "expired") {
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

  if (status === "error" || !data) {
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
      data-theme={data.theme_slug || "default"}
      style={{ background: "var(--color-bg, #fff)", color: "var(--color-text, #0f172a)", fontFamily: "var(--font-sans)" }}
    >
      {/* Preview banner */}
      <div className="sticky top-0 z-50 flex items-center justify-center gap-2 py-2 text-xs font-medium bg-violet-600 text-white">
        <span>✦</span> Draft Preview
        {data._expires_at && (
          <span className="opacity-75">— expires {new Date(data._expires_at).toLocaleString()}</span>
        )}
      </div>

      {data.sections
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
