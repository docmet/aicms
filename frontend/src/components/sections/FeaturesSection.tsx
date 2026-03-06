/**
 * FeaturesSection — icon grid of features or services.
 * Renders content_published JSON matching the FeaturesContent schema.
 */
"use client";

import React, { useEffect, useRef } from "react";

interface FeatureItem {
  icon?: string;
  title: string;
  description?: string;
}

type SectionBackground = "default" | "white" | "gray" | "brand" | "dark";
type FeaturesLayout = "grid-2" | "grid-3" | "grid-4" | "list";

interface FeaturesContent {
  headline?: string;
  subheadline?: string;
  items: FeatureItem[];
  layout?: FeaturesLayout;
  background?: SectionBackground;
}

function parseContent(raw: string): FeaturesContent {
  try {
    return JSON.parse(raw) as FeaturesContent;
  } catch {
    return { items: [] };
  }
}

function bgStyle(bg: SectionBackground | undefined): React.CSSProperties {
  switch (bg) {
    case "white":   return { background: "var(--color-bg)" };
    case "gray":    return { background: "var(--color-card)" };
    case "brand":   return { background: "var(--color-primary)" };
    case "dark":    return { background: "var(--color-dark-section)" };
    default:        return { background: "var(--color-bg)" };
  }
}

function textColor(bg: SectionBackground | undefined): string {
  return bg === "dark" ? "var(--color-dark-section-text)" : "var(--color-heading)";
}

function mutedColor(bg: SectionBackground | undefined): string {
  return (bg === "dark" || bg === "brand") ? "rgba(255,255,255,0.75)" : "var(--color-text-muted)";
}

export function FeaturesSection({ content }: { content: string }) {
  const sectionRef = useRef<HTMLElement>(null);
  const data = parseContent(content);
  const layout = data.layout ?? "grid-3";
  const bg = data.background;

  useEffect(() => {
    const section = sectionRef.current;
    if (!section) return;
    const cards = section.querySelectorAll<HTMLElement>(".animate-on-scroll");
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => { if (e.isIntersecting) (e.target as HTMLElement).classList.add("visible"); });
      },
      { threshold: 0.1 }
    );
    cards.forEach((c) => observer.observe(c));
    return () => observer.disconnect();
  }, []);

  const gridClass =
    layout === "grid-2" ? "grid md:grid-cols-2 gap-6" :
    layout === "grid-4" ? "grid md:grid-cols-2 lg:grid-cols-4 gap-6" :
    layout === "list"   ? "flex flex-col gap-4" :
    /* grid-3 default */ "grid md:grid-cols-2 lg:grid-cols-3 gap-6";

  return (
    <section
      ref={sectionRef}
      className="py-24 px-6"
      style={bgStyle(bg)}
    >
      <div className="max-w-6xl mx-auto">
        {(data.headline || data.subheadline) && (
          <div className="text-center mb-16">
            {data.headline && (
              <h2
                className="text-4xl md:text-5xl font-bold mb-4"
                style={{ color: textColor(bg), fontFamily: "var(--font-heading, var(--font-sora, Sora, sans-serif))" }}
              >
                {data.headline}
              </h2>
            )}
            {data.subheadline && (
              <p className="text-xl max-w-2xl mx-auto" style={{ color: mutedColor(bg) }}>
                {data.subheadline}
              </p>
            )}
          </div>
        )}

        <div className={gridClass}>
          {data.items.map((item, i) => (
            <div
              key={i}
              className={`animate-on-scroll rounded-2xl transition-all duration-300 hover:-translate-y-1 hover:shadow-lg ${layout === "list" ? "p-6 flex gap-5 items-start" : "p-8"}`}
              style={{ background: "var(--color-card)", border: "1px solid var(--color-card-border)" }}
            >
              {item.icon && (
                <div className={layout === "list" ? "text-3xl flex-shrink-0 mt-0.5" : "text-4xl mb-4"}>
                  {item.icon}
                </div>
              )}
              <div>
                <h3 className="text-xl font-bold mb-2" style={{ color: "var(--color-heading)" }}>
                  {item.title}
                </h3>
                {item.description && (
                  <p className="leading-relaxed" style={{ color: "var(--color-text-muted)" }}>
                    {item.description}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
