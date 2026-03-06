"use client";

import { useEffect, useRef, useState } from "react";

interface ContactContent {
  headline?: string;
  subheadline?: string;
  email?: string;
  phone?: string;
  address?: string;
  hours?: string;
  show_form?: boolean; // default true
}

function parseContent(raw: string): ContactContent {
  try {
    return JSON.parse(raw) as ContactContent;
  } catch {
    return { headline: "Contact Us" };
  }
}

const SVG_MAIL = (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
);
const SVG_PHONE = (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
  </svg>
);
const SVG_MAP = (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);
const SVG_CLOCK = (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

export function ContactSection({ content, siteSlug }: { content: string; siteSlug?: string }) {
  const sectionRef = useRef<HTMLElement>(null);
  const data = parseContent(content);
  const showForm = data.show_form !== false;

  const [formState, setFormState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [formData, setFormData] = useState({ name: "", email: "", subject: "", message: "" });

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!siteSlug) return;
    setFormState("sending");
    try {
      const res = await fetch(`/api/public/sites/${siteSlug}/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      setFormState(res.ok ? "sent" : "error");
    } catch {
      setFormState("error");
    }
  };

  const contactItems = [
    { icon: SVG_MAIL, label: "Email", value: data.email, href: data.email ? `mailto:${data.email}` : undefined },
    { icon: SVG_PHONE, label: "Phone", value: data.phone, href: data.phone ? `tel:${data.phone}` : undefined },
    { icon: SVG_MAP, label: "Address", value: data.address },
    { icon: SVG_CLOCK, label: "Hours", value: data.hours },
  ].filter((item) => item.value);

  const inputStyle = {
    borderColor: "var(--color-card-border)",
    color: "var(--color-text)",
    background: "var(--color-card)",
  };

  return (
    <section
      ref={sectionRef}
      className="py-24 px-6 animate-on-scroll"
      style={{ background: "var(--color-card)" }}
    >
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <h2
            className="text-4xl md:text-5xl font-bold mb-4"
            style={{ color: "var(--color-heading)", fontFamily: "var(--font-heading)" }}
          >
            {data.headline || "Get in Touch"}
          </h2>
          {data.subheadline && (
            <p className="text-xl max-w-2xl mx-auto" style={{ color: "var(--color-text-muted)" }}>
              {data.subheadline}
            </p>
          )}
        </div>

        <div className={`grid gap-10 ${showForm && siteSlug ? "lg:grid-cols-2" : ""}`}>
          {/* Contact info cards */}
          {contactItems.length > 0 && (
            <div className="grid sm:grid-cols-2 gap-6 content-start">
              {contactItems.map((item, i) => (
                <div
                  key={i}
                  className="rounded-2xl p-6 text-center"
                  style={{ background: "var(--color-bg)", border: "1px solid var(--color-card-border)" }}
                >
                  <div
                    className="w-10 h-10 rounded-full mx-auto mb-3 flex items-center justify-center"
                    style={{ background: "var(--color-primary)", color: "#fff" }}
                  >
                    {item.icon}
                  </div>
                  <p className="text-xs font-medium uppercase tracking-wide mb-1" style={{ color: "var(--color-text-muted)" }}>
                    {item.label}
                  </p>
                  {item.href ? (
                    <a href={item.href} className="font-semibold hover:opacity-80 transition-opacity" style={{ color: "var(--color-primary)" }}>
                      {item.value}
                    </a>
                  ) : (
                    <p className="font-semibold" style={{ color: "var(--color-heading)" }}>{item.value}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Contact form */}
          {showForm && siteSlug && (
            <div className="rounded-2xl p-8" style={{ background: "var(--color-bg)", border: "1px solid var(--color-card-border)" }}>
              {formState === "sent" ? (
                <div className="text-center py-8">
                  <div
                    className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center"
                    style={{ background: "var(--color-primary)" }}
                  >
                    <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold mb-2" style={{ color: "var(--color-heading)" }}>Message sent!</h3>
                  <p style={{ color: "var(--color-text-muted)" }}>We&apos;ll be in touch soon.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Name *</label>
                      <input
                        required
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-4 py-3 rounded-xl border text-sm focus:outline-none focus:ring-2"
                        style={inputStyle}
                        placeholder="Your name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Email *</label>
                      <input
                        required
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="w-full px-4 py-3 rounded-xl border text-sm focus:outline-none focus:ring-2"
                        style={inputStyle}
                        placeholder="your@email.com"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Subject</label>
                    <input
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                      className="w-full px-4 py-3 rounded-xl border text-sm focus:outline-none focus:ring-2"
                      style={inputStyle}
                      placeholder="What is this about?"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Message *</label>
                    <textarea
                      required
                      rows={5}
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      className="w-full px-4 py-3 rounded-xl border text-sm focus:outline-none focus:ring-2"
                      style={{ ...inputStyle, resize: "none" }}
                      placeholder="Your message..."
                    />
                  </div>
                  {formState === "error" && (
                    <p className="text-sm text-red-500">Something went wrong. Please try again.</p>
                  )}
                  <button
                    type="submit"
                    disabled={formState === "sending"}
                    className="w-full py-3 px-6 rounded-xl text-white font-semibold transition-opacity hover:opacity-90 disabled:opacity-60"
                    style={{ background: "linear-gradient(135deg, var(--color-cta-from), var(--color-cta-to))" }}
                  >
                    {formState === "sending" ? "Sending…" : "Send Message"}
                  </button>
                </form>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
