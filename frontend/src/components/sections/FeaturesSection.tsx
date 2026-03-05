/**
 * FeaturesSection — icon grid of features or services.
 * Renders content_published JSON matching the FeaturesContent schema.
 */
"use client";

import { useEffect, useRef } from "react";

interface FeatureItem {
  icon?: string;
  title: string;
  description?: string;
}

interface FeaturesContent {
  headline?: string;
  subheadline?: string;
  items: FeatureItem[];
}

function parseContent(raw: string): FeaturesContent {
  try {
    return JSON.parse(raw) as FeaturesContent;
  } catch {
    return { items: [] };
  }
}

export function FeaturesSection({ content }: { content: string }) {
  const sectionRef = useRef<HTMLElement>(null);
  const data = parseContent(content);

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

  return (
    <section
      ref={sectionRef}
      className="py-24 px-6"
      style={{ background: "var(--color-bg)" }}
    >
      <div className="max-w-6xl mx-auto">
        {(data.headline || data.subheadline) && (
          <div className="text-center mb-16">
            {data.headline && (
              <h2
                className="text-4xl md:text-5xl font-bold mb-4"
                style={{
                  color: "var(--color-heading)",
                  fontFamily: "var(--font-heading, var(--font-sora, Sora, sans-serif))",
                }}
              >
                {data.headline}
              </h2>
            )}
            {data.subheadline && (
              <p
                className="text-xl max-w-2xl mx-auto"
                style={{ color: "var(--color-text-muted)" }}
              >
                {data.subheadline}
              </p>
            )}
          </div>
        )}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.items.map((item, i) => (
            <div
              key={i}
              className="animate-on-scroll rounded-2xl p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
              style={{
                background: "var(--color-card)",
                border: "1px solid var(--color-card-border)",
              }}
            >
              {item.icon && (
                <div className="text-4xl mb-4">{item.icon}</div>
              )}
              <h3
                className="text-xl font-bold mb-2"
                style={{ color: "var(--color-heading)" }}
              >
                {item.title}
              </h3>
              {item.description && (
                <p className="leading-relaxed" style={{ color: "var(--color-text-muted)" }}>
                  {item.description}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
