"use client";

import { useEffect, useRef } from "react";

interface StatItem {
  number: string;
  label: string;
}

interface AboutContent {
  headline: string;
  body: string;
  stats?: StatItem[];
}

function parseContent(raw: string): AboutContent {
  try {
    return JSON.parse(raw) as AboutContent;
  } catch {
    return { headline: "About Us", body: raw };
  }
}

export function AboutSection({ content }: { content: string }) {
  const sectionRef = useRef<HTMLElement>(null);
  const data = parseContent(content);

  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) el.classList.add("visible");
      },
      { threshold: 0.1 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="py-24 px-6 animate-on-scroll"
      style={{ background: "var(--color-bg)" }}
    >
      <div className="max-w-6xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2
              className="text-4xl md:text-5xl font-bold mb-6"
              style={{
                color: "var(--color-heading)",
                fontFamily: "var(--font-heading)",
              }}
            >
              {data.headline}
            </h2>
            <div
              className="text-lg leading-relaxed space-y-4"
              style={{ color: "var(--color-text-muted)" }}
            >
              {data.body.split("\n").map((paragraph, i) => (
                <p key={i}>{paragraph}</p>
              ))}
            </div>
          </div>

          {data.stats && data.stats.length > 0 && (
            <div className="grid grid-cols-2 gap-8">
              {data.stats.map((stat, i) => (
                <div
                  key={i}
                  className="text-center rounded-2xl p-8"
                  style={{
                    background: "var(--color-card)",
                    border: "1px solid var(--color-card-border)",
                  }}
                >
                  <div
                    className="text-4xl font-extrabold mb-2"
                    style={{ color: "var(--color-primary)" }}
                  >
                    {stat.number}
                  </div>
                  <div
                    className="text-sm font-medium uppercase tracking-wide"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
