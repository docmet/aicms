'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Check, ArrowRight } from 'lucide-react';
import api from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

// ── Config ────────────────────────────────────────────────────────────────────

const WP_STARTER_PRICE_ID = process.env.NEXT_PUBLIC_STRIPE_WP_STARTER_PRICE_ID ?? '';
const WP_PRO_PRICE_ID = process.env.NEXT_PUBLIC_STRIPE_WP_PRO_PRICE_ID ?? '';

// ── Types ─────────────────────────────────────────────────────────────────────

interface PricingTier {
  name: string;
  price: string;
  period: string;
  features: string[];
  priceId: string;
  plan: string;
  highlight: boolean;
}

const tiers: PricingTier[] = [
  {
    name: 'Starter',
    price: '7',
    period: 'per month',
    features: [
      '1 WordPress site',
      'All WP tools (posts, pages, settings)',
      'Works with Claude.ai + ChatGPT',
      'MCP token authentication',
    ],
    priceId: WP_STARTER_PRICE_ID,
    plan: 'wp_starter',
    highlight: false,
  },
  {
    name: 'Pro',
    price: '24',
    period: 'per month',
    features: [
      '3 WordPress sites',
      'All Starter features',
      'Priority support',
      'Early access to WooCommerce tools',
    ],
    priceId: WP_PRO_PRICE_ID,
    plan: 'wp_pro',
    highlight: true,
  },
];

// ── Checkout button ───────────────────────────────────────────────────────────

function CheckoutButton({ tier }: { tier: PricingTier }) {
  const { user } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  if (!tier.priceId) {
    return (
      <button
        disabled
        className="w-full text-sm font-semibold px-5 py-2.5 rounded-lg text-center bg-gray-700 text-gray-400 cursor-not-allowed"
      >
        Coming soon
      </button>
    );
  }

  const handleClick = async () => {
    if (!user) {
      router.push('/login?next=/wordpress');
      return;
    }
    setLoading(true);
    try {
      const origin = window.location.origin;
      const res = await api.post<{ checkout_url: string }>(`/billing/checkout?plan=${tier.plan}`, {
        success_url: `${origin}/dashboard/wordpress?checkout=success`,
        cancel_url: `${origin}/wordpress`,
      });
      window.location.href = res.data.checkout_url;
    } catch {
      toast({ title: 'Checkout failed', description: 'Please try again.', variant: 'destructive' });
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className={`w-full text-sm font-semibold px-5 py-2.5 rounded-lg text-center transition-all disabled:opacity-60 disabled:cursor-wait ${
        tier.highlight
          ? 'bg-white text-violet-600 hover:bg-violet-50'
          : 'bg-violet-600 text-white hover:bg-violet-700'
      }`}
    >
      {loading ? 'Redirecting...' : 'Get Started'}
    </button>
  );
}

// ── How it works ──────────────────────────────────────────────────────────────

const steps = [
  {
    n: 1,
    title: 'Install the MyStorey plugin',
    desc: 'Download and activate the MyStorey plugin on your WordPress site. Plugin download coming soon.',
  },
  {
    n: 2,
    title: 'Connect in MyStorey settings',
    desc: "Enter your WordPress URL and Application Password in your MyStorey dashboard. We'll verify the connection and issue your MCP token.",
  },
  {
    n: 3,
    title: 'Chat with AI to control your site',
    desc: 'Paste the MCP URL into Claude.ai or ChatGPT — then just tell it what to do. Write posts, update pages, change your tagline.',
  },
];

// ── Features ──────────────────────────────────────────────────────────────────

const features = [
  {
    title: 'Write and publish blog posts',
    desc: 'Create posts with categories, tags, and status. Publish immediately or save as draft.',
  },
  {
    title: 'Update pages',
    desc: 'Change homepage copy, your about page, contact details — any WordPress page.',
  },
  {
    title: 'Control site settings',
    desc: 'Update your site title and tagline without logging into the WP admin.',
  },
  {
    title: 'Works with any MCP-compatible AI',
    desc: 'Claude.ai, ChatGPT, Cursor, and any tool that supports the MCP protocol.',
  },
];

// ── Main component ────────────────────────────────────────────────────────────

export function WordPressLanding() {
  return (
    <div className="min-h-screen bg-gray-950 text-white font-sans">
      {/* Nav */}
      <header className="sticky top-0 z-50 bg-gray-950/90 backdrop-blur border-b border-gray-800">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link href="/" className="text-base font-bold text-white">
            My<span className="text-violet-400">Storey</span>
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <a href="#pricing" className="text-gray-400 hover:text-white transition-colors">
              Pricing
            </a>
            <Link
              href="/login"
              className="bg-violet-600 hover:bg-violet-700 text-white font-semibold px-4 py-1.5 rounded-lg text-sm transition-colors"
            >
              Sign in
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 bg-violet-950/60 text-violet-300 text-xs font-medium px-3 py-1.5 rounded-full mb-8 border border-violet-800">
          WordPress + AI
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6">
          Your WordPress.
          <br />
          <span className="text-violet-400">Controlled by AI.</span>
        </h1>

        <p className="text-lg text-gray-400 max-w-2xl mx-auto leading-relaxed mb-12">
          Stop clicking through the WP admin. Tell Claude or ChatGPT what to write — and it writes it
          directly to your site.
        </p>

        {/* Matrix pill choice */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <div className="flex flex-col items-center gap-1">
            <button
              className="cursor-default bg-red-600 text-white font-semibold px-7 py-3 rounded-xl relative group"
              title="Are you sure?"
            >
              Keep clicking menus
              <span className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-800 text-gray-300 text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                Are you sure?
              </span>
            </button>
            <span className="text-xs text-gray-500">Same old WP admin</span>
          </div>

          <span className="text-gray-600 text-sm hidden sm:block">or</span>

          <div className="flex flex-col items-center gap-1">
            <a
              href="#pricing"
              className="bg-violet-600 hover:bg-violet-700 text-white font-semibold px-7 py-3 rounded-xl transition-colors flex items-center gap-2"
            >
              Control with AI
              <ArrowRight size={16} />
            </a>
            <span className="text-xs text-gray-500">MyStorey WP Plugin</span>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="bg-gray-900 border-y border-gray-800 py-20">
        <div className="max-w-5xl mx-auto px-6">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-12">How it works</h2>
          <div className="grid sm:grid-cols-3 gap-8">
            {steps.map((step) => (
              <div key={step.n} className="flex flex-col gap-4">
                <div className="w-10 h-10 rounded-full bg-violet-600 flex items-center justify-center font-bold text-lg flex-shrink-0">
                  {step.n}
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2">{step.title}</h3>
                  <p className="text-sm text-gray-400 leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What AI can do */}
      <section className="py-20 max-w-5xl mx-auto px-6">
        <h2 className="text-2xl sm:text-3xl font-bold text-center mb-12">What AI can do</h2>
        <div className="grid sm:grid-cols-2 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-violet-800 transition-colors"
            >
              <h3 className="font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="bg-gray-900 border-y border-gray-800 py-20">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold">Simple pricing</h2>
            <p className="text-gray-400 mt-2">Cancel any time. No hidden fees.</p>
          </div>

          <div className="grid sm:grid-cols-2 gap-6 max-w-2xl mx-auto">
            {tiers.map((tier) => (
              <div
                key={tier.name}
                className={`rounded-2xl p-8 flex flex-col gap-6 ${
                  tier.highlight
                    ? 'bg-violet-600 border-0 shadow-2xl shadow-violet-900'
                    : 'bg-gray-950 border border-gray-800'
                }`}
              >
                <div>
                  <p
                    className={`text-sm font-medium mb-1 ${
                      tier.highlight ? 'text-violet-200' : 'text-gray-400'
                    }`}
                  >
                    {tier.name}
                  </p>
                  <div className="flex items-end gap-1">
                    <span className="text-4xl font-bold">${tier.price}</span>
                    <span
                      className={`text-sm mb-1.5 ${
                        tier.highlight ? 'text-violet-200' : 'text-gray-400'
                      }`}
                    >
                      /{tier.period}
                    </span>
                  </div>
                </div>

                <ul className="space-y-3 flex-1">
                  {tier.features.map((feat) => (
                    <li key={feat} className="flex items-start gap-2.5 text-sm">
                      <Check
                        size={15}
                        className={`mt-0.5 flex-shrink-0 ${
                          tier.highlight ? 'text-violet-200' : 'text-violet-400'
                        }`}
                      />
                      <span className={tier.highlight ? 'text-white/90' : 'text-gray-300'}>
                        {feat}
                      </span>
                    </li>
                  ))}
                </ul>

                <CheckoutButton tier={tier} />
              </div>
            ))}
          </div>

          <p className="text-center text-xs text-gray-500 mt-6">
            Requires a MyStorey account — free to create.{' '}
            <Link href="/register" className="text-violet-400 hover:underline">
              Sign up free
            </Link>
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8">
        <div className="max-w-5xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-500">
          <span className="font-semibold text-white">
            My<span className="text-violet-400">Storey</span>
          </span>
          <p>&copy; 2026 MyStorey. All rights reserved.</p>
          <div className="flex gap-4">
            <a href="#" className="hover:text-gray-300">
              Privacy
            </a>
            <a href="#" className="hover:text-gray-300">
              Terms
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
