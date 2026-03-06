'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import api from '@/lib/api';
import Link from 'next/link';
import { ArrowRight, Check } from 'lucide-react';
import { Suspense } from 'react';

const planLabels: Record<string, { name: string; price: string; highlight: string }> = {
  pro: { name: 'Pro', price: '$9.99/mo', highlight: '7-day free trial' },
  agency: { name: 'Agency', price: '$99/mo', highlight: '7-day free trial' },
};

function RegisterForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const plan = searchParams.get('plan') ?? 'free';
  const planInfo = planLabels[plan];
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && user) {
      // Already logged in — go to billing if a paid plan was selected, else dashboard
      if (plan !== 'free') {
        router.push(`/dashboard/billing?plan=${plan}`);
      } else {
        router.push('/dashboard');
      }
    }
  }, [loading, user, plan, router]);

  if (loading || user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="w-6 h-6 border-2 border-violet-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      await api.post('/auth/register', { email, password });
      router.push('/login?registered=true');
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      setError(e.response?.data?.detail || 'Could not create account. Try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left: brand panel */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-violet-600 to-indigo-700 flex-col justify-between p-12 text-white">
        <Link href="/" className="text-xl font-bold tracking-tight">
          My<span className="text-violet-200">Storey</span>
        </Link>
        <div className="space-y-6">
          <h2 className="text-3xl font-bold leading-snug max-w-xs">
            Your story starts here.
          </h2>
          <ul className="space-y-3">
            {[
              'Free forever plan — no card needed',
              'Connect any AI assistant in seconds',
              'Beautiful themes out of the box',
            ].map((item) => (
              <li key={item} className="flex items-center gap-3 text-sm text-violet-100">
                <Check size={15} className="text-violet-300 flex-shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>
        <p className="text-violet-400 text-xs">© 2026 MyStorey</p>
      </div>

      {/* Right: form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <Link href="/" className="lg:hidden block text-xl font-bold text-gray-900 mb-8">
            My<span className="text-violet-600">Storey</span>
          </Link>

          {/* Plan badge */}
          {planInfo && (
            <div className="mb-6 bg-violet-50 border border-violet-200 rounded-xl p-4 flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-violet-800">{planInfo.name} plan selected</p>
                <p className="text-xs text-violet-500 mt-0.5">{planInfo.price} · {planInfo.highlight}</p>
              </div>
              <Link href="/register" className="text-xs text-violet-400 hover:text-violet-600 whitespace-nowrap mt-0.5">
                Switch to Free
              </Link>
            </div>
          )}

          <h1 className="text-2xl font-bold text-gray-900 mb-1">Create your account</h1>
          <p className="text-sm text-gray-500 mb-8">
            Already have one?{' '}
            <Link href="/login" className="text-violet-600 hover:text-violet-700 font-medium">
              Sign in
            </Link>
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input
                type="email"
                required
                autoFocus
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
              <input
                type="password"
                required
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
                placeholder="At least 8 characters"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-700 text-white font-semibold py-2.5 rounded-lg text-sm transition-all disabled:opacity-50 mt-2"
            >
              {isSubmitting ? 'Creating account…' : 'Create free account'}
              {!isSubmitting && <ArrowRight size={15} />}
            </button>

            <p className="text-xs text-gray-400 text-center">
              By signing up you agree to our{' '}
              <a href="#" className="underline hover:text-gray-600">Terms</a> and{' '}
              <a href="#" className="underline hover:text-gray-600">Privacy Policy</a>.
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense>
      <RegisterForm />
    </Suspense>
  );
}
