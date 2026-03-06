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
  layout?: "centered" | "split" | "fullscreen";
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

  const layout = data.layout ?? "centered";

  /** Shared CTA buttons block */
  const ctaButtons = (
    <div className="flex flex-wrap gap-4 justify-center">
      {data.cta_primary && (
        <a
          href={data.cta_primary.href ?? "#"}
          className="inline-flex items-center px-8 py-4 rounded-xl text-lg font-semibold text-white transition-all duration-200 hover:opacity-90 hover:-translate-y-0.5 shadow-lg hover:shadow-xl"
          style={{ background: "linear-gradient(135deg, var(--color-cta-from), var(--color-cta-to))" }}
        >
          {data.cta_primary.label}
        </a>
      )}
      {data.cta_secondary && (
        <a
          href={data.cta_secondary.href ?? "#"}
          className="inline-flex items-center px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-200 hover:-translate-y-0.5"
          style={{ color: "var(--color-text)", border: "2px solid var(--color-card-border)", background: "transparent" }}
        >
          {data.cta_secondary.label}
        </a>
      )}
    </div>
  );

  /** Shared headline block */
  const headlineBlock = (centered: boolean) => (
    <>
      {data.logo_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={data.logo_url} alt="Logo" className={`h-16 mb-8 object-contain ${centered ? "mx-auto" : ""}`} />
      )}
      {data.badge && (
        <span
          className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-semibold text-white mb-8 ${centered ? "" : "self-start"}`}
          style={{ background: "var(--color-primary)" }}
        >
          {data.badge}
        </span>
      )}
      <h1
        className={`text-5xl md:text-7xl font-extrabold leading-tight tracking-tight mb-6 ${centered ? "" : "text-left"}`}
        style={{ fontFamily: "var(--font-heading, var(--font-sora, Sora, sans-serif))" }}
      >
        <span
          style={{
            background: "linear-gradient(135deg, var(--color-gradient-text-from), var(--color-gradient-text-to))",
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
          className={`text-xl md:text-2xl mb-12 leading-relaxed ${centered ? "max-w-3xl mx-auto" : "max-w-xl"}`}
          style={{ color: "var(--color-text-muted)" }}
        >
          {data.subheadline}
        </p>
      )}
    </>
  );

  // ── Split layout: text left, image right ───────────────────────────────
  if (layout === "split") {
    return (
      <section
        ref={sectionRef}
        className="py-24 px-6 animate-on-scroll"
        style={{ background: "var(--color-bg)" }}
      >
        <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
          <div className="flex flex-col">
            {headlineBlock(false)}
            <div className="flex flex-wrap gap-4">{ctaButtons}</div>
          </div>
          {data.background_image ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={data.background_image}
              alt=""
              className="w-full rounded-2xl object-cover shadow-xl"
              style={{ maxHeight: "520px" }}
            />
          ) : (
            <div
              className="w-full rounded-2xl flex items-center justify-center"
              style={{ minHeight: "360px", background: "linear-gradient(135deg, var(--color-hero-from), var(--color-hero-to))" }}
            />
          )}
        </div>
      </section>
    );
  }

  // ── Fullscreen layout: 100vh, centered, bold ───────────────────────────
  if (layout === "fullscreen") {
    return (
      <section
        ref={sectionRef}
        className="relative min-h-screen flex items-center justify-center overflow-hidden animate-on-scroll"
        style={
          data.background_image
            ? { backgroundImage: `url(${data.background_image})`, backgroundSize: "cover", backgroundPosition: "center" }
            : { background: "linear-gradient(135deg, var(--color-hero-from), var(--color-hero-to))" }
        }
      >
        {data.background_image && <div className="absolute inset-0 bg-black/60" aria-hidden />}
        <div className="relative max-w-5xl mx-auto px-6 py-32 text-center">
          {headlineBlock(true)}
          {ctaButtons}
        </div>
      </section>
    );
  }

  // ── Centered layout (default) ──────────────────────────────────────────
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
      {data.background_image && <div className="absolute inset-0 bg-black/50" aria-hidden />}

      {!data.background_image && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden>
          <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full blur-3xl opacity-25" style={{ background: "var(--color-primary)" }} />
          <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full blur-3xl opacity-15" style={{ background: "var(--color-accent)" }} />
        </div>
      )}

      <div className="relative max-w-6xl mx-auto px-6 py-28 text-center w-full">
        {headlineBlock(true)}
        {ctaButtons}
      </div>
    </section>
  );
}
