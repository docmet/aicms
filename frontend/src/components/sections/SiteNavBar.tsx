"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface NavPage {
  title: string;
  slug: string;
}

interface SiteNavBarProps {
  siteName: string;
  siteSlug: string;
  pages: NavPage[];
  currentPageSlug?: string;
}

export function SiteNavBar({ siteName, siteSlug, pages, currentPageSlug }: SiteNavBarProps) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Only render nav if there are multiple pages
  if (pages.length <= 1) return null;

  const homepageSlug = pages[0]?.slug;

  function href(page: NavPage) {
    return page.slug === homepageSlug
      ? `/${siteSlug}`
      : `/${siteSlug}/${page.slug}`;
  }

  function isActive(page: NavPage) {
    if (currentPageSlug) return page.slug === currentPageSlug;
    return page.slug === homepageSlug;
  }

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 ${
        scrolled ? "shadow-md" : ""
      }`}
      style={{
        background: scrolled
          ? "var(--color-card, rgba(255,255,255,0.97))"
          : "var(--color-hero-from, rgba(255,255,255,0.9))",
        backdropFilter: "blur(8px)",
        borderBottom: scrolled ? "1px solid var(--color-card-border, #e2e8f0)" : "none",
      }}
    >
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between h-16">
        {/* Logo */}
        <Link
          href={`/${siteSlug}`}
          className="text-lg font-bold tracking-tight"
          style={{ color: "var(--color-primary, #3b82f6)" }}
        >
          {siteName}
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {pages.map((page) => (
            <Link
              key={page.slug}
              href={href(page)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(page) ? "opacity-100" : "opacity-70 hover:opacity-100"
              }`}
              style={
                isActive(page)
                  ? {
                      background: "var(--color-primary, #3b82f6)",
                      color: "#fff",
                    }
                  : {
                      color: "var(--color-text, #0f172a)",
                    }
              }
            >
              {page.title}
            </Link>
          ))}
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden p-2 rounded-lg"
          style={{ color: "var(--color-text, #0f172a)" }}
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {menuOpen ? (
              <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
            ) : (
              <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div
          className="md:hidden border-t px-4 py-3 flex flex-col gap-1"
          style={{
            background: "var(--color-card, #fff)",
            borderColor: "var(--color-card-border, #e2e8f0)",
          }}
        >
          {pages.map((page) => (
            <Link
              key={page.slug}
              href={href(page)}
              onClick={() => setMenuOpen(false)}
              className="px-4 py-2 rounded-lg text-sm font-medium"
              style={
                isActive(page)
                  ? {
                      background: "var(--color-primary, #3b82f6)",
                      color: "#fff",
                    }
                  : {
                      color: "var(--color-text, #0f172a)",
                    }
              }
            >
              {page.title}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}
