"use client";

import { useEffect, useRef } from "react";

interface TestimonialItem {
  quote: string;
  name: string;
  role?: string;
  company?: string;
  avatar_url?: string | null;
}

type TestimonialsLayout = "cards" | "masonry" | "featured";

interface TestimonialsContent {
  headline?: string;
  items: TestimonialItem[];
  layout?: TestimonialsLayout;
  background?: "default" | "white" | "gray" | "dark";
}

function parseContent(raw: string): TestimonialsContent {
  try {
    return JSON.parse(raw) as TestimonialsContent;
  } catch {
    return { items: [] };
  }
}

const QuoteIcon = () => (
  <svg className="w-8 h-8 mb-4 opacity-30" style={{ color: "var(--color-primary)" }} fill="currentColor" viewBox="0 0 24 24">
    <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
  </svg>
);

function TestimonialCard({ item }: { item: TestimonialItem }) {
  return (
    <div className="animate-on-scroll rounded-2xl p-8" style={{ background: "var(--color-card)", border: "1px solid var(--color-card-border)" }}>
      <QuoteIcon />
      <p className="text-lg leading-relaxed mb-6" style={{ color: "var(--color-text)" }}>{item.quote}</p>
      <div className="flex items-center gap-3">
        {item.avatar_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={item.avatar_url} alt={item.name} className="w-10 h-10 rounded-full object-cover flex-shrink-0" />
        )}
        <div>
          <p className="font-semibold" style={{ color: "var(--color-heading)" }}>{item.name}</p>
          {(item.role || item.company) && (
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              {[item.role, item.company].filter(Boolean).join(" at ")}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export function TestimonialsSection({ content }: { content: string }) {
  const sectionRef = useRef<HTMLElement>(null);
  const data = parseContent(content);
  const layout = data.layout ?? "cards";

  const sectionBg =
    data.background === "white" ? "var(--color-bg)" :
    data.background === "gray"  ? "var(--color-card)" :
    /* default dark */ "var(--color-dark-section)";
  const headingColor =
    data.background === "white" || data.background === "gray"
      ? "var(--color-heading)" : "var(--color-dark-section-text)";

  useEffect(() => {
    const section = sectionRef.current;
    if (!section) return;
    const cards = section.querySelectorAll<HTMLElement>(".animate-on-scroll");
    const observer = new IntersectionObserver(
      (entries) => { entries.forEach((e) => { if (e.isIntersecting) (e.target as HTMLElement).classList.add("visible"); }); },
      { threshold: 0.1 }
    );
    cards.forEach((c) => observer.observe(c));
    return () => observer.disconnect();
  }, []);

  if (data.items.length === 0) return null;

  return (
    <section ref={sectionRef} className="py-24 px-6" style={{ background: sectionBg }}>
      <div className="max-w-6xl mx-auto">
        {data.headline && (
          <h2
            className="text-4xl md:text-5xl font-bold text-center mb-16"
            style={{ color: headingColor, fontFamily: "var(--font-heading)" }}
          >
            {data.headline}
          </h2>
        )}

        {layout === "featured" ? (
          // Featured: first item large, rest below in a row
          <div className="space-y-8">
            {data.items[0] && (
              <div
                className="animate-on-scroll rounded-2xl p-10"
                style={{ background: "var(--color-card)", border: "1px solid var(--color-card-border)" }}
              >
                <QuoteIcon />
                <p className="text-2xl leading-relaxed mb-8 font-medium" style={{ color: "var(--color-text)" }}>
                  {data.items[0].quote}
                </p>
                <div className="flex items-center gap-3">
                  {data.items[0].avatar_url && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={data.items[0].avatar_url} alt={data.items[0].name} className="w-12 h-12 rounded-full object-cover" />
                  )}
                  <div>
                    <p className="font-semibold text-lg" style={{ color: "var(--color-heading)" }}>{data.items[0].name}</p>
                    {(data.items[0].role || data.items[0].company) && (
                      <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        {[data.items[0].role, data.items[0].company].filter(Boolean).join(" at ")}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
            {data.items.length > 1 && (
              <div className="grid md:grid-cols-2 gap-6">
                {data.items.slice(1).map((item, i) => <TestimonialCard key={i + 1} item={item} />)}
              </div>
            )}
          </div>
        ) : layout === "masonry" ? (
          // Masonry: CSS columns
          <div className="columns-1 md:columns-2 lg:columns-3 gap-6">
            {data.items.map((item, i) => (
              <div key={i} className="break-inside-avoid mb-6">
                <TestimonialCard item={item} />
              </div>
            ))}
          </div>
        ) : (
          // Cards (default): uniform grid
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {data.items.map((item, i) => <TestimonialCard key={i} item={item} />)}
          </div>
        )}
      </div>
    </section>
  );
}
