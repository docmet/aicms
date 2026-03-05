"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import api from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

// ── Industry templates ─────────────────────────────────────────────────────

const INDUSTRIES = [
  { id: "restaurant", label: "Restaurant / Café", emoji: "🍽️" },
  { id: "portfolio", label: "Portfolio / Freelance", emoji: "🎨" },
  { id: "saas", label: "SaaS / Startup", emoji: "🚀" },
  { id: "services", label: "Service Business", emoji: "🔧" },
  { id: "boutique", label: "Boutique / Store", emoji: "🛍️" },
  { id: "other", label: "Other / Blank", emoji: "✨" },
];

const THEMES = [
  { slug: "default", label: "Default", color: "#3b82f6" },
  { slug: "warm", label: "Warm", color: "#f97316" },
  { slug: "startup", label: "Startup", color: "#10b981" },
  { slug: "minimal", label: "Minimal", color: "#71717a" },
  { slug: "dark", label: "Dark", color: "#a78bfa" },
];

type IndustryId = (typeof INDUSTRIES)[number]["id"];

function buildSections(siteName: string, industry: IndustryId) {
  const name = siteName || "My Business";

  const templates: Record<IndustryId, { section_type: string; content: object; order: number }[]> = {
    restaurant: [
      {
        section_type: "hero",
        order: 0,
        content: {
          headline: `Welcome to ${name}`,
          subheadline: "Fresh ingredients, unforgettable flavours. Dine in or take away.",
          badge: "Now open 7 days",
          cta_primary: { label: "Reserve a Table", href: "#contact" },
          cta_secondary: { label: "View Menu", href: "#menu" },
        },
      },
      {
        section_type: "features",
        order: 1,
        content: {
          headline: "Why Guests Love Us",
          subheadline: "Every detail crafted with care.",
          items: [
            { icon: "🌿", title: "Farm-to-Table", description: "Seasonal produce sourced from local farms." },
            { icon: "🍷", title: "Curated Wine List", description: "Over 80 labels from small producers." },
            { icon: "👨‍🍳", title: "Award-Winning Chef", description: "15 years of Michelin-starred experience." },
            { icon: "🌟", title: "Private Dining", description: "Host your event in our exclusive room." },
          ],
        },
      },
      {
        section_type: "about",
        order: 2,
        content: {
          headline: `Our Story`,
          body: `${name} was founded on a simple belief: great food brings people together. We source the finest seasonal ingredients and prepare every dish with heart.`,
          stats: [
            { number: "12+", label: "Years in business" },
            { number: "500+", label: "5-star reviews" },
            { number: "3", label: "Award nominations" },
          ],
        },
      },
      {
        section_type: "cta",
        order: 3,
        content: {
          headline: "Ready for an Unforgettable Evening?",
          subheadline: "Book your table online — we fill up fast on weekends.",
          button_label: "Reserve Now",
          button_href: "#contact",
        },
      },
      {
        section_type: "contact",
        order: 4,
        content: {
          headline: "Find Us",
          email: `hello@${name.toLowerCase().replace(/\s+/g, "")}.com`,
          phone: "+1 (555) 000-1234",
          address: "123 Main Street, Downtown",
          hours: "Tue–Sun: 12pm–10pm",
        },
      },
    ],

    portfolio: [
      {
        section_type: "hero",
        order: 0,
        content: {
          headline: `Hi, I'm ${name}`,
          subheadline: "I design and build digital experiences that people love.",
          cta_primary: { label: "View My Work", href: "#work" },
          cta_secondary: { label: "Get in Touch", href: "#contact" },
        },
      },
      {
        section_type: "features",
        order: 1,
        content: {
          headline: "What I Do",
          items: [
            { icon: "🎨", title: "UI / UX Design", description: "Pixel-perfect interfaces with great UX." },
            { icon: "💻", title: "Frontend Development", description: "React, Next.js, TypeScript." },
            { icon: "📱", title: "Mobile Apps", description: "React Native for iOS and Android." },
            { icon: "⚡", title: "Performance", description: "Fast, accessible, SEO-optimised." },
          ],
        },
      },
      {
        section_type: "testimonials",
        order: 2,
        content: {
          headline: "Client Feedback",
          items: [
            { quote: "Delivered on time and exceeded every expectation. Will hire again!", name: "Alex R.", role: "Product Lead", company: "TechCo" },
            { quote: "Our new website doubled our conversion rate.", name: "Maria S.", role: "Founder", company: "StartupXYZ" },
          ],
        },
      },
      {
        section_type: "cta",
        order: 3,
        content: {
          headline: "Let's Build Something Together",
          subheadline: "Available for freelance projects starting next month.",
          button_label: "Hire Me",
          button_href: "#contact",
        },
      },
      {
        section_type: "contact",
        order: 4,
        content: {
          headline: "Get in Touch",
          email: `hello@${name.toLowerCase().replace(/\s+/g, "")}.dev`,
        },
      },
    ],

    saas: [
      {
        section_type: "hero",
        order: 0,
        content: {
          headline: `${name} — Build Faster`,
          subheadline: "The all-in-one platform that cuts your workflow from days to minutes.",
          badge: "Now in beta — free forever plan",
          cta_primary: { label: "Start Free", href: "#pricing" },
          cta_secondary: { label: "See Demo", href: "#features" },
        },
      },
      {
        section_type: "features",
        order: 1,
        content: {
          headline: "Everything You Need",
          subheadline: "One platform, no integrations required.",
          items: [
            { icon: "⚡", title: "Blazing Fast", description: "Sub-100ms response times, globally distributed." },
            { icon: "🔒", title: "Enterprise Security", description: "SOC2 Type II, end-to-end encryption." },
            { icon: "🤖", title: "AI-Powered", description: "Smart suggestions that learn from your workflow." },
            { icon: "📊", title: "Analytics", description: "Real-time dashboards with custom reports." },
            { icon: "🔗", title: "Integrations", description: "Connects to 200+ tools you already use." },
            { icon: "📱", title: "Mobile-First", description: "Native apps for iOS and Android." },
          ],
        },
      },
      {
        section_type: "testimonials",
        order: 2,
        content: {
          headline: "Loved by Teams Worldwide",
          items: [
            { quote: "We cut our deployment time by 80%. Worth every penny.", name: "James K.", role: "CTO", company: "ScaleUp Inc" },
            { quote: "Finally a tool that doesn't require a PhD to configure.", name: "Priya N.", role: "Engineering Lead", company: "FinTech Co" },
          ],
        },
      },
      {
        section_type: "pricing",
        order: 3,
        content: {
          headline: "Simple, Transparent Pricing",
          subheadline: "Start free. Scale when you're ready.",
          plans: [
            { name: "Free", price: "$0", period: "/month", features: ["Up to 3 projects", "Basic analytics", "Community support"], cta_label: "Get started", highlighted: false },
            { name: "Pro", price: "$29", period: "/month", features: ["Unlimited projects", "Advanced analytics", "Priority support", "Team collaboration"], cta_label: "Start free trial", highlighted: true },
            { name: "Enterprise", price: "Custom", features: ["Dedicated infrastructure", "SLA guarantee", "Custom integrations", "Onboarding support"], cta_label: "Contact sales", highlighted: false },
          ],
        },
      },
      {
        section_type: "cta",
        order: 4,
        content: {
          headline: "Start Building Today",
          subheadline: "No credit card required. Cancel anytime.",
          button_label: "Get Started Free",
          button_href: "#",
        },
      },
    ],

    services: [
      {
        section_type: "hero",
        order: 0,
        content: {
          headline: `${name} — Professional Services`,
          subheadline: "Trusted by hundreds of clients. Results guaranteed.",
          cta_primary: { label: "Get a Free Quote", href: "#contact" },
          cta_secondary: { label: "Our Services", href: "#services" },
        },
      },
      {
        section_type: "features",
        order: 1,
        content: {
          headline: "Our Services",
          items: [
            { icon: "🔧", title: "Consultation", description: "Expert advice tailored to your needs." },
            { icon: "📋", title: "Planning & Strategy", description: "Detailed project plans with clear timelines." },
            { icon: "⚙️", title: "Execution", description: "Done right, on time, every time." },
            { icon: "✅", title: "Ongoing Support", description: "We stay with you after the job is done." },
          ],
        },
      },
      {
        section_type: "about",
        order: 2,
        content: {
          headline: `About ${name}`,
          body: "We are a team of experienced professionals dedicated to delivering exceptional results. With over a decade of expertise, we've helped hundreds of clients achieve their goals.",
          stats: [
            { number: "10+", label: "Years experience" },
            { number: "300+", label: "Projects completed" },
            { number: "98%", label: "Client satisfaction" },
          ],
        },
      },
      {
        section_type: "testimonials",
        order: 3,
        content: {
          headline: "What Our Clients Say",
          items: [
            { quote: "Professional, reliable, and delivered exactly what we needed.", name: "Tom B.", role: "Business Owner" },
            { quote: "Best decision we made this year was hiring them.", name: "Linda M.", role: "Operations Manager" },
          ],
        },
      },
      {
        section_type: "cta",
        order: 4,
        content: {
          headline: "Ready to Get Started?",
          subheadline: "Free consultation, no obligation.",
          button_label: "Book a Free Call",
          button_href: "#contact",
        },
      },
      {
        section_type: "contact",
        order: 5,
        content: {
          headline: "Contact Us",
          email: `hello@${name.toLowerCase().replace(/\s+/g, "")}.com`,
          phone: "+1 (555) 000-1234",
        },
      },
    ],

    boutique: [
      {
        section_type: "hero",
        order: 0,
        content: {
          headline: `Discover ${name}`,
          subheadline: "Handpicked pieces for the discerning customer. New arrivals weekly.",
          cta_primary: { label: "Shop Now", href: "#products" },
          cta_secondary: { label: "Our Story", href: "#about" },
        },
      },
      {
        section_type: "features",
        order: 1,
        content: {
          headline: "Why Shop With Us",
          items: [
            { icon: "✨", title: "Curated Selection", description: "Every item personally selected for quality." },
            { icon: "🚚", title: "Free Shipping", description: "On all orders over $75." },
            { icon: "↩️", title: "Easy Returns", description: "30-day hassle-free returns." },
            { icon: "💬", title: "Personal Styling", description: "Free 1:1 styling advice via chat." },
          ],
        },
      },
      {
        section_type: "about",
        order: 2,
        content: {
          headline: `The ${name} Story`,
          body: "We started as a passion project, scouring trade shows and artisan markets for pieces you won't find anywhere else. Every item in our store has a story.",
          stats: [
            { number: "500+", label: "Unique products" },
            { number: "20+", label: "Artisan partners" },
            { number: "4.9★", label: "Average review" },
          ],
        },
      },
      {
        section_type: "testimonials",
        order: 3,
        content: {
          headline: "Our Happy Customers",
          items: [
            { quote: "The quality is unmatched. I always get compliments when I wear pieces from here.", name: "Sophie L.", role: "Regular Customer" },
            { quote: "Fast shipping, beautiful packaging, and exactly as described.", name: "Mark T." },
          ],
        },
      },
      {
        section_type: "cta",
        order: 4,
        content: {
          headline: "New Arrivals Every Week",
          subheadline: "Sign up to be the first to know.",
          button_label: "Browse New Arrivals",
          button_href: "#products",
        },
      },
    ],

    other: [
      {
        section_type: "hero",
        order: 0,
        content: {
          headline: `Welcome to ${name}`,
          subheadline: "Tell your story here.",
          cta_primary: { label: "Get Started", href: "#" },
        },
      },
      {
        section_type: "about",
        order: 1,
        content: {
          headline: `About ${name}`,
          body: "Replace this with your own story.",
        },
      },
      {
        section_type: "contact",
        order: 2,
        content: {
          headline: "Get in Touch",
          email: "hello@example.com",
        },
      },
    ],
  };

  return templates[industry] ?? templates.other;
}

// ── Step indicators ────────────────────────────────────────────────────────

function StepDot({ step, current }: { step: number; current: number }) {
  return (
    <div className={`flex items-center gap-2 ${step <= current ? "text-blue-600" : "text-gray-300"}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 ${
          step < current
            ? "bg-blue-600 border-blue-600 text-white"
            : step === current
            ? "border-blue-600 text-blue-600"
            : "border-gray-200 text-gray-300"
        }`}
      >
        {step < current ? "✓" : step}
      </div>
    </div>
  );
}

// ── Main wizard ────────────────────────────────────────────────────────────

export default function NewSitePage() {
  const [step, setStep] = useState(1);
  const [industry, setIndustry] = useState<IndustryId>("other");
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [theme, setTheme] = useState("default");
  const [creating, setCreating] = useState(false);
  const router = useRouter();
  const { toast } = useToast();

  function toSlug(s: string) {
    return s
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^\w-]+/g, "");
  }

  function handleNameChange(e: React.ChangeEvent<HTMLInputElement>) {
    const v = e.target.value;
    setName(v);
    if (!slug || slug === toSlug(name)) setSlug(toSlug(v));
  }

  async function handleCreate() {
    setCreating(true);
    try {
      // 1. Create site
      const siteRes = await api.post("/sites/", { name, slug, theme_slug: theme });
      const siteId: string = siteRes.data.id;

      // 2. Create homepage
      const pageRes = await api.post(`/sites/${siteId}/pages`, {
        title: "Home",
        slug: "home",
        is_published: false,
      });
      const pageId: string = pageRes.data.id;

      // 3. Upsert all starter sections
      const sections = buildSections(name, industry);
      await Promise.all(
        sections.map((s) =>
          api.put(`/sites/${siteId}/pages/${pageId}/content/by-type/${s.section_type}`, {
            content_draft: JSON.stringify(s.content),
            order: s.order,
          })
        )
      );

      // 4. Publish
      await api.post(`/sites/${siteId}/pages/${pageId}/publish`);

      toast({ title: "Site created!", description: `${name} is live at /${slug}` });
      router.push(`/dashboard/sites/${siteId}`);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      toast({
        title: "Failed to create site",
        description: e.response?.data?.detail ?? "Unknown error",
        variant: "destructive",
      });
      setCreating(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" asChild>
          <Link href="/dashboard">Back</Link>
        </Button>
        <h1 className="text-3xl font-bold text-gray-900">Create New Site</h1>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-3">
        <StepDot step={1} current={step} />
        <div className={`flex-1 h-px ${step > 1 ? "bg-blue-300" : "bg-gray-200"}`} />
        <StepDot step={2} current={step} />
        <div className={`flex-1 h-px ${step > 2 ? "bg-blue-300" : "bg-gray-200"}`} />
        <StepDot step={3} current={step} />
      </div>

      {/* Step 1: Industry */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>What kind of site is this?</CardTitle>
            <CardDescription>
              We&apos;ll pre-fill starter content based on your industry.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {INDUSTRIES.map((ind) => (
                <button
                  key={ind.id}
                  onClick={() => setIndustry(ind.id)}
                  className={`p-4 rounded-xl border-2 text-left transition-all hover:border-blue-400 ${
                    industry === ind.id
                      ? "border-blue-600 bg-blue-50"
                      : "border-gray-200"
                  }`}
                >
                  <div className="text-3xl mb-2">{ind.emoji}</div>
                  <div className="text-sm font-medium text-gray-800">{ind.label}</div>
                </button>
              ))}
            </div>
            <div className="flex justify-end mt-6">
              <Button onClick={() => setStep(2)}>Continue →</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Name + Slug */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Name your site</CardTitle>
            <CardDescription>
              You can always change this later.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Site Name</Label>
              <Input
                id="name"
                placeholder="Brew & Bean Coffee"
                value={name}
                onChange={handleNameChange}
                autoFocus
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="slug">URL Slug</Label>
              <div className="flex items-center gap-2">
                <Input
                  id="slug"
                  placeholder="brew-and-bean"
                  value={slug}
                  onChange={(e) => setSlug(toSlug(e.target.value))}
                />
                <span className="text-sm text-gray-400 whitespace-nowrap">.docmet.systems</span>
              </div>
              <p className="text-xs text-gray-400">Only lowercase letters, numbers, and hyphens.</p>
            </div>
            <div className="flex justify-between mt-6">
              <Button variant="outline" onClick={() => setStep(1)}>← Back</Button>
              <Button onClick={() => setStep(3)} disabled={!name || !slug}>
                Continue →
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Theme + Confirm */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Choose a theme</CardTitle>
            <CardDescription>
              Pick the colour palette that fits your brand.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-wrap gap-3">
              {THEMES.map((t) => (
                <button
                  key={t.slug}
                  onClick={() => setTheme(t.slug)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 text-sm font-medium transition-all ${
                    theme === t.slug
                      ? "border-blue-600 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ background: t.color }}
                  />
                  {t.label}
                </button>
              ))}
            </div>

            {/* Summary */}
            <div className="bg-gray-50 rounded-xl p-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Site name</span>
                <span className="font-medium">{name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">URL slug</span>
                <span className="font-medium">/{slug}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Industry</span>
                <span className="font-medium">
                  {INDUSTRIES.find((i) => i.id === industry)?.label}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Starter sections</span>
                <span className="font-medium">
                  {buildSections(name, industry).length} sections
                </span>
              </div>
            </div>

            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(2)}>← Back</Button>
              <Button onClick={handleCreate} disabled={creating}>
                {creating ? "Creating your site…" : "🚀 Create Site"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
