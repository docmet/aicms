"use client";

import { useEffect, useRef } from "react";

interface ContactContent {
  headline?: string;
  email?: string;
  phone?: string;
  address?: string;
  hours?: string;
}

function parseContent(raw: string): ContactContent {
  try {
    return JSON.parse(raw) as ContactContent;
  } catch {
    return { headline: "Contact Us" };
  }
}

export function ContactSection({ content }: { content: string }) {
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

  const items = [
    { icon: "mail", label: "Email", value: data.email, href: data.email ? `mailto:${data.email}` : undefined },
    { icon: "phone", label: "Phone", value: data.phone, href: data.phone ? `tel:${data.phone}` : undefined },
    { icon: "map", label: "Address", value: data.address },
    { icon: "clock", label: "Hours", value: data.hours },
  ].filter((item) => item.value);

  return (
    <section
      ref={sectionRef}
      className="py-24 px-6 animate-on-scroll"
      style={{ background: "var(--color-card)" }}
    >
      <div className="max-w-4xl mx-auto text-center">
        <h2
          className="text-4xl md:text-5xl font-bold mb-16"
          style={{
            color: "var(--color-heading)",
            fontFamily: "var(--font-heading)",
          }}
        >
          {data.headline || "Get in Touch"}
        </h2>

        <div className="grid sm:grid-cols-2 gap-8">
          {items.map((item, i) => (
            <div
              key={i}
              className="rounded-2xl p-8 text-center"
              style={{
                background: "var(--color-bg)",
                border: "1px solid var(--color-card-border)",
              }}
            >
              <div
                className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center"
                style={{ background: "var(--color-primary)", color: "#fff" }}
              >
                {item.icon === "mail" && (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                )}
                {item.icon === "phone" && (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                )}
                {item.icon === "map" && (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                )}
                {item.icon === "clock" && (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
              </div>
              <p
                className="text-sm font-medium uppercase tracking-wide mb-2"
                style={{ color: "var(--color-text-muted)" }}
              >
                {item.label}
              </p>
              {item.href ? (
                <a
                  href={item.href}
                  className="text-lg font-semibold hover:opacity-80 transition-opacity"
                  style={{ color: "var(--color-primary)" }}
                >
                  {item.value}
                </a>
              ) : (
                <p
                  className="text-lg font-semibold"
                  style={{ color: "var(--color-heading)" }}
                >
                  {item.value}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
