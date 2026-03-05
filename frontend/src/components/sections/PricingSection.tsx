"use client";

import { useEffect, useRef } from "react";

interface PricingPlan {
  name: string;
  price: string;
  period?: string;
  features: string[];
  cta_label?: string;
  cta_href?: string;
  highlighted?: boolean;
}

interface PricingContent {
  headline?: string;
  subheadline?: string;
  plans: PricingPlan[];
}

function parseContent(raw: string): PricingContent {
  try {
    return JSON.parse(raw) as PricingContent;
  } catch {
    return { plans: [] };
  }
}

export function PricingSection({ content }: { content: string }) {
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

  if (data.plans.length === 0) return null;

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
                  fontFamily: "var(--font-heading)",
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

        <div
          className="grid gap-8"
          style={{
            gridTemplateColumns: `repeat(${Math.min(data.plans.length, 3)}, minmax(0, 1fr))`,
          }}
        >
          {data.plans.map((plan, i) => (
            <div
              key={i}
              className="animate-on-scroll rounded-2xl p-8 flex flex-col relative"
              style={{
                background: plan.highlighted
                  ? "var(--color-primary)"
                  : "var(--color-card)",
                border: plan.highlighted
                  ? "2px solid var(--color-primary)"
                  : "1px solid var(--color-card-border)",
                transform: plan.highlighted ? "scale(1.05)" : undefined,
              }}
            >
              {plan.highlighted && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-xs font-bold text-white bg-gradient-to-r from-[var(--color-cta-from)] to-[var(--color-cta-to)]">
                  Most Popular
                </span>
              )}

              <h3
                className="text-xl font-bold mb-2"
                style={{
                  color: plan.highlighted ? "#ffffff" : "var(--color-heading)",
                }}
              >
                {plan.name}
              </h3>

              <div className="mb-6">
                <span
                  className="text-4xl font-extrabold"
                  style={{
                    color: plan.highlighted ? "#ffffff" : "var(--color-heading)",
                  }}
                >
                  {plan.price}
                </span>
                {plan.period && (
                  <span
                    className="text-sm ml-1"
                    style={{
                      color: plan.highlighted
                        ? "rgba(255,255,255,0.7)"
                        : "var(--color-text-muted)",
                    }}
                  >
                    {plan.period}
                  </span>
                )}
              </div>

              <ul className="space-y-3 mb-8 flex-1">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-start gap-2">
                    <svg
                      className="w-5 h-5 mt-0.5 flex-shrink-0"
                      style={{
                        color: plan.highlighted
                          ? "rgba(255,255,255,0.9)"
                          : "var(--color-primary)",
                      }}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span
                      className="text-sm"
                      style={{
                        color: plan.highlighted
                          ? "rgba(255,255,255,0.9)"
                          : "var(--color-text)",
                      }}
                    >
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              <a
                href={plan.cta_href ?? "#"}
                className="block w-full text-center py-3 rounded-xl font-semibold transition-all duration-200 hover:-translate-y-0.5"
                style={
                  plan.highlighted
                    ? { background: "#ffffff", color: "var(--color-primary)" }
                    : {
                        background: "var(--color-primary)",
                        color: "#ffffff",
                      }
                }
              >
                {plan.cta_label || "Get Started"}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
