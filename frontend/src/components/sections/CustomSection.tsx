"use client";

import { useEffect, useRef } from "react";

interface CustomContent {
  title?: string;
  content?: string;
}

function parseContent(raw: string): CustomContent {
  try {
    const parsed = JSON.parse(raw);
    return parsed as CustomContent;
  } catch {
    return { content: raw };
  }
}

export function CustomSection({ content }: { content: string }) {
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
      <div className="max-w-4xl mx-auto">
        {data.title && (
          <h2
            className="text-4xl md:text-5xl font-bold text-center mb-8"
            style={{
              color: "var(--color-heading)",
              fontFamily: "var(--font-heading)",
            }}
          >
            {data.title}
          </h2>
        )}
        {data.content && (
          <div
            className="text-lg leading-relaxed space-y-4"
            style={{ color: "var(--color-text)" }}
          >
            {data.content.split("\n").map((paragraph, i) => (
              <p key={i}>{paragraph}</p>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
