import Link from 'next/link';
import { Check, Sparkles, Globe, Zap, ArrowRight, Star } from 'lucide-react';

const features = [
  {
    icon: Sparkles,
    title: 'Build with AI',
    desc: 'Connect Claude, Cursor, or any AI assistant. Describe your site in plain English and watch it come to life.',
  },
  {
    icon: Globe,
    title: 'Live in seconds',
    desc: 'Every site gets a free mystorey.io subdomain, instant SSL, and global CDN — zero config.',
  },
  {
    icon: Zap,
    title: 'Always up to date',
    desc: 'Your AI keeps content fresh. Edit copy, swap themes, and publish changes without touching code.',
  },
];

const tiers = [
  {
    name: 'Free',
    price: '0',
    period: 'forever',
    highlight: false,
    description: 'Perfect to try it out',
    features: [
      '1 website',
      'Free mystorey.io subdomain',
      'All themes & sections',
      'AI assistant connection',
      '"Made with MyStorey" badge',
    ],
    cta: 'Start for free',
    href: '/register',
    note: null,
  },
  {
    name: 'Pro',
    price: '9.99',
    period: 'per month',
    highlight: true,
    description: 'For creators & freelancers',
    features: [
      '3 websites',
      'Custom domains',
      'Remove MyStorey badge',
      'Priority support',
      'Early access to new features',
    ],
    cta: 'Start 7-day free trial',
    href: '/register?plan=pro',
    note: 'No credit card required',
  },
  {
    name: 'Agency',
    price: '99',
    period: 'per month',
    highlight: false,
    description: 'For teams & agencies',
    features: [
      '15 websites',
      'Custom domains',
      'AI automations (coming soon)',
      'Social content scheduling',
      'Bulk site generation',
      'Dedicated support',
    ],
    cta: 'Start 7-day free trial',
    href: '/register?plan=agency',
    note: 'No credit card required',
  },
];

const testimonials = [
  {
    quote: 'I built my portfolio site in under 10 minutes by just chatting with Claude. Wild.',
    name: 'Alex M.',
    role: 'Photographer',
  },
  {
    quote: 'Our agency uses MyStorey to spin up client landing pages before the kickoff call even ends.',
    name: 'Sara K.',
    role: 'Creative Director',
  },
  {
    quote: 'The AI integration is seamless. I describe a change and it just happens.',
    name: 'James T.',
    role: 'Indie maker',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Nav */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <span className="text-xl font-bold tracking-tight text-gray-900">
            My<span className="text-violet-600">Storey</span>
          </span>
          <nav className="hidden md:flex items-center gap-8 text-sm text-gray-600">
            <a href="#features" className="hover:text-gray-900 transition-colors">Features</a>
            <a href="#pricing" className="hover:text-gray-900 transition-colors">Pricing</a>
          </nav>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900 transition-colors px-3 py-1.5">
              Sign in
            </Link>
            <Link
              href="/register"
              className="text-sm font-medium bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Get started free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 bg-violet-50 text-violet-700 text-xs font-medium px-3 py-1.5 rounded-full mb-8 border border-violet-100">
          <Sparkles size={12} />
          Build your website by talking to AI
        </div>

        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 leading-[1.08] tracking-tight max-w-4xl mx-auto">
          Your story,{' '}
          <span className="bg-gradient-to-r from-violet-600 to-indigo-500 bg-clip-text text-transparent">
            built by AI.
          </span>
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed">
          Connect Claude or any AI assistant to MyStorey and build beautiful websites through
          conversation — no design skills, no code.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/register"
            className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-700 text-white font-semibold px-8 py-3.5 rounded-xl text-base transition-all shadow-lg shadow-violet-200 hover:shadow-violet-300 hover:-translate-y-0.5"
          >
            Build your site — it&apos;s free
            <ArrowRight size={18} />
          </Link>
          <Link
            href="/login"
            className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            Already have an account? Sign in →
          </Link>
        </div>

        <p className="mt-4 text-xs text-gray-400">No credit card required · Free forever plan</p>

        {/* Hero visual */}
        <div className="mt-16 mx-auto max-w-4xl rounded-2xl border border-gray-200 bg-gradient-to-br from-gray-50 to-violet-50/30 shadow-xl overflow-hidden">
          <div className="flex items-center gap-1.5 px-4 py-3 border-b border-gray-200 bg-white/60">
            <span className="w-3 h-3 rounded-full bg-red-400" />
            <span className="w-3 h-3 rounded-full bg-yellow-400" />
            <span className="w-3 h-3 rounded-full bg-green-400" />
            <span className="ml-2 text-xs text-gray-400 font-mono">mystorey.io/your-site</span>
          </div>
          <div className="p-8 text-left space-y-4">
            {/* Chat bubbles mockup */}
            <div className="flex gap-3 items-start">
              <div className="w-7 h-7 rounded-full bg-violet-600 flex items-center justify-center flex-shrink-0">
                <Sparkles size={12} className="text-white" />
              </div>
              <div className="bg-white rounded-xl rounded-tl-sm px-4 py-3 text-sm text-gray-700 shadow-sm border border-gray-100 max-w-sm">
                Create a hero section for my photography portfolio with a dark, moody feel.
              </div>
            </div>
            <div className="flex gap-3 items-start flex-row-reverse">
              <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                <span className="text-xs font-bold text-gray-500">AI</span>
              </div>
              <div className="bg-violet-600 rounded-xl rounded-tr-sm px-4 py-3 text-sm text-white max-w-sm">
                Done! I&apos;ve created a dark hero section with &quot;Capturing Moments&quot; as the headline, a moody overlay, and a full-width background. Published and live ✓
              </div>
            </div>
            <div className="mx-10 rounded-xl bg-gray-900 aspect-[16/5] overflow-hidden flex items-center justify-center">
              <p className="text-white/60 text-sm font-medium tracking-wide">✦ Capturing Moments ✦</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="bg-gray-50 border-y border-gray-100 py-24">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">Everything you need</h2>
            <p className="mt-3 text-gray-500 text-lg">A complete website platform, powered by AI.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((f) => (
              <div key={f.title} className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center mb-5">
                  <f.icon size={20} className="text-violet-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social proof */}
      <section className="py-20 max-w-6xl mx-auto px-6">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-1 mb-3">
            {[...Array(5)].map((_, i) => (
              <Star key={i} size={16} className="text-amber-400 fill-amber-400" />
            ))}
          </div>
          <p className="text-gray-500 text-sm">Loved by creators worldwide</p>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((t) => (
            <div key={t.name} className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
              <p className="text-gray-700 text-sm leading-relaxed mb-4">&ldquo;{t.quote}&rdquo;</p>
              <div>
                <p className="text-sm font-semibold text-gray-900">{t.name}</p>
                <p className="text-xs text-gray-400">{t.role}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="bg-gray-50 border-y border-gray-100 py-24">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">Simple, honest pricing</h2>
            <p className="mt-3 text-gray-500 text-lg">Start free. Upgrade when you&apos;re ready.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {tiers.map((tier) => (
              <div
                key={tier.name}
                className={`rounded-2xl p-8 flex flex-col ${
                  tier.highlight
                    ? 'bg-violet-600 text-white shadow-2xl shadow-violet-200 scale-105 border-0'
                    : 'bg-white border border-gray-200 shadow-sm'
                }`}
              >
                {tier.highlight && (
                  <div className="inline-flex items-center gap-1.5 bg-white/20 text-white text-xs font-medium px-2.5 py-1 rounded-full mb-4 self-start">
                    <Sparkles size={10} />
                    Most popular
                  </div>
                )}
                <p className={`text-sm font-medium ${tier.highlight ? 'text-violet-200' : 'text-gray-400'}`}>
                  {tier.name}
                </p>
                <div className="mt-2 flex items-end gap-1">
                  <span className={`text-4xl font-bold ${tier.highlight ? 'text-white' : 'text-gray-900'}`}>
                    ${tier.price}
                  </span>
                  <span className={`text-sm mb-1.5 ${tier.highlight ? 'text-violet-200' : 'text-gray-400'}`}>
                    /{tier.period}
                  </span>
                </div>
                <p className={`text-sm mt-1 mb-6 ${tier.highlight ? 'text-violet-200' : 'text-gray-500'}`}>
                  {tier.description}
                </p>

                <ul className="space-y-3 flex-1 mb-8">
                  {tier.features.map((feat) => (
                    <li key={feat} className="flex items-start gap-2.5 text-sm">
                      <Check
                        size={15}
                        className={`mt-0.5 flex-shrink-0 ${tier.highlight ? 'text-violet-200' : 'text-violet-500'}`}
                      />
                      <span className={tier.highlight ? 'text-white/90' : 'text-gray-600'}>{feat}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href={tier.href}
                  className={`text-sm font-semibold px-5 py-2.5 rounded-lg text-center transition-all ${
                    tier.highlight
                      ? 'bg-white text-violet-600 hover:bg-violet-50'
                      : 'bg-violet-600 text-white hover:bg-violet-700'
                  }`}
                >
                  {tier.cta}
                </Link>
                {tier.note && (
                  <p className={`text-xs text-center mt-2 ${tier.highlight ? 'text-violet-300' : 'text-gray-400'}`}>
                    {tier.note}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 max-w-3xl mx-auto px-6 text-center">
        <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
          Ready to tell your storey?
        </h2>
        <p className="mt-4 text-gray-500 text-lg">
          Free forever. No credit card. Live in minutes.
        </p>
        <Link
          href="/register"
          className="mt-8 inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-700 text-white font-semibold px-8 py-3.5 rounded-xl text-base transition-all shadow-lg shadow-violet-200 hover:shadow-violet-300 hover:-translate-y-0.5"
        >
          Start building free
          <ArrowRight size={18} />
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-10">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="text-sm font-semibold text-gray-900">
            My<span className="text-violet-600">Storey</span>
          </span>
          <p className="text-xs text-gray-400">© 2026 MyStorey. Build beautiful. Tell your story.</p>
          <div className="flex gap-6 text-xs text-gray-400">
            <a href="#" className="hover:text-gray-600">Privacy</a>
            <a href="#" className="hover:text-gray-600">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
