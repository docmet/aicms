/**
 * HeroSection — full-bleed gradient hero with headline, badge, and CTA buttons.
 * Renders content_published JSON matching the HeroContent schema.
 */
"use client";

import { useEffect, useRef } from "react";

interface CtaButton {
  label: string;
  href?: string;
}

interface HeroContent {
  headline: string;
  subheadline?: string;
  badge?: string;
  cta_primary?: CtaButton;
  cta_secondary?: CtaButton;
  background_image?: string | null;
  logo_url?: string | null;
}

function parseContent(raw: string): HeroContent {
  try {
    return JSON.parse(raw) as HeroContent;
  } catch {
    return { headline: raw };
  }
}

export function HeroSection({ content }: { content: string }) {
  const sectionRef = useRef<HTMLElement>(null);
  const data = parseContent(content);

  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) el.classList.add("visible"); },
      { threshold: 0.1 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative min-h-[85vh] flex items-center overflow-hidden animate-on-scroll"
      style={
        data.background_image
          ? { backgroundImage: `url(${data.background_image})`, backgroundSize: "cover", backgroundPosition: "center" }
          : { background: "linear-gradient(135deg, var(--color-hero-from), var(--color-hero-to))" }
      }
    >
      {/* Dark overlay when background image is set */}
      {data.background_image && (
        <div className="absolute inset-0 bg-black/50" aria-hidden />
      )}

      {/* Decorative blobs (only when no bg image) */}
      {!data.background_image && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden>
          <div
            className="absolute -top-40 -right-40 w-96 h-96 rounded-full blur-3xl opacity-25"
            style={{ background: "var(--color-primary)" }}
          />
          <div
            className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full blur-3xl opacity-15"
            style={{ background: "var(--color-accent)" }}
          />
        </div>
      )}

      <div className="relative max-w-6xl mx-auto px-6 py-28 text-center">
        {data.logo_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={data.logo_url}
            alt="Logo"
            className="h-16 mx-auto mb-8 object-contain"
          />
        )}
        {data.badge && (
          <span
            className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-semibold text-white mb-8"
            style={{ background: "var(--color-primary)" }}
          >
            {data.badge}
          </span>
        )}

        <h1
          className="text-5xl md:text-7xl font-extrabold leading-tight tracking-tight mb-6"
          style={{ fontFamily: "var(--font-heading, var(--font-sora, Sora, sans-serif))" }}
        >
          <span
            style={{
              background:
                "linear-gradient(135deg, var(--color-gradient-text-from), var(--color-gradient-text-to))",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            {data.headline}
          </span>
        </h1>

        {data.subheadline && (
          <p
            className="text-xl md:text-2xl max-w-3xl mx-auto mb-12 leading-relaxed"
            style={{ color: "var(--color-text-muted)" }}
          >
            {data.subheadline}
          </p>
        )}

        <div className="flex flex-wrap gap-4 justify-center">
          {data.cta_primary && (
            <a
              href={data.cta_primary.href ?? "#"}
              className="inline-flex items-center px-8 py-4 rounded-xl text-lg font-semibold text-white transition-all duration-200 hover:opacity-90 hover:-translate-y-0.5 shadow-lg hover:shadow-xl"
              style={{
                background:
                  "linear-gradient(135deg, var(--color-cta-from), var(--color-cta-to))",
              }}
            >
              {data.cta_primary.label}
            </a>
          )}
          {data.cta_secondary && (
            <a
              href={data.cta_secondary.href ?? "#"}
              className="inline-flex items-center px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-200 hover:-translate-y-0.5"
              style={{
                color: "var(--color-text)",
                border: "2px solid var(--color-card-border)",
                background: "transparent",
              }}
            >
              {data.cta_secondary.label}
            </a>
          )}
        </div>
      </div>
    </section>
  );
}
