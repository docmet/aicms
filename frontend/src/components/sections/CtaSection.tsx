"use client";

import { useEffect, useRef } from "react";

interface CtaContent {
  headline: string;
  subheadline?: string;
  button_label: string;
  button_href?: string;
}

function parseContent(raw: string): CtaContent {
  try {
    return JSON.parse(raw) as CtaContent;
  } catch {
    return { headline: raw, button_label: "Get Started" };
  }
}

export function CtaSection({ content }: { content: string }) {
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
      style={{
        background:
          "linear-gradient(135deg, var(--color-cta-from), var(--color-cta-to))",
      }}
    >
      <div className="max-w-4xl mx-auto text-center">
        <h2
          className="text-4xl md:text-5xl font-bold mb-6 text-white"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          {data.headline}
        </h2>

        {data.subheadline && (
          <p className="text-xl mb-10 text-white/80 max-w-2xl mx-auto leading-relaxed">
            {data.subheadline}
          </p>
        )}

        <a
          href={data.button_href ?? "#"}
          className="inline-flex items-center px-10 py-4 rounded-xl text-lg font-semibold transition-all duration-200 hover:-translate-y-0.5 shadow-lg hover:shadow-xl"
          style={{
            background: "#ffffff",
            color: "var(--color-cta-from)",
          }}
        >
          {data.button_label}
        </a>
      </div>
    </section>
  );
}
