"use client";

import { useEffect, useRef } from "react";

interface TestimonialItem {
  quote: string;
  name: string;
  role?: string;
  company?: string;
}

interface TestimonialsContent {
  headline?: string;
  items: TestimonialItem[];
}

function parseContent(raw: string): TestimonialsContent {
  try {
    return JSON.parse(raw) as TestimonialsContent;
  } catch {
    return { items: [] };
  }
}

export function TestimonialsSection({ content }: { content: string }) {
  const sectionRef = useRef<HTMLElement>(null);
  const data = parseContent(content);

  useEffect(() => {
    const section = sectionRef.current;
    if (!section) return;
    const cards = section.querySelectorAll<HTMLElement>(".animate-on-scroll");
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) (e.target as HTMLElement).classList.add("visible");
        });
      },
      { threshold: 0.1 }
    );
    cards.forEach((c) => observer.observe(c));
    return () => observer.disconnect();
  }, []);

  if (data.items.length === 0) return null;

  return (
    <section
      ref={sectionRef}
      className="py-24 px-6"
      style={{ background: "var(--color-dark-section)" }}
    >
      <div className="max-w-6xl mx-auto">
        {data.headline && (
          <h2
            className="text-4xl md:text-5xl font-bold text-center mb-16"
            style={{
              color: "var(--color-dark-section-text)",
              fontFamily: "var(--font-heading)",
            }}
          >
            {data.headline}
          </h2>
        )}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {data.items.map((item, i) => (
            <div
              key={i}
              className="animate-on-scroll rounded-2xl p-8"
              style={{
                background: "var(--color-card)",
                border: "1px solid var(--color-card-border)",
              }}
            >
              <svg
                className="w-8 h-8 mb-4 opacity-30"
                style={{ color: "var(--color-primary)" }}
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
              </svg>
              <p
                className="text-lg leading-relaxed mb-6"
                style={{ color: "var(--color-text)" }}
              >
                {item.quote}
              </p>
              <div>
                <p
                  className="font-semibold"
                  style={{ color: "var(--color-heading)" }}
                >
                  {item.name}
                </p>
                {(item.role || item.company) && (
                  <p
                    className="text-sm"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {[item.role, item.company].filter(Boolean).join(" at ")}
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
