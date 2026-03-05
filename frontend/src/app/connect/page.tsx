'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import api from '@/lib/api';

function ConnectContent() {
  const searchParams = useSearchParams();
  const redirectUri = searchParams.get('redirect_uri') ?? '';
  const state = searchParams.get('state') ?? '';

  const [step, setStep] = useState<'loading' | 'login' | 'allow' | 'done' | 'error'>('loading');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Check if already logged in
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { setStep('login'); return; }
    api.get('/auth/me')
      .then(() => setStep('allow'))
      .catch(() => { localStorage.removeItem('token'); setStep('login'); });
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const form = new URLSearchParams();
      form.append('username', email);
      form.append('password', password);
      const res = await api.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      localStorage.setItem('token', res.data.access_token);
      setStep('allow');
    } catch {
      setError('Incorrect email or password.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAllow = async () => {
    setSubmitting(true);
    try {
      const res = await api.post<{ code: string }>('/mcp/oauth-authorize');
      const code = res.data.code;
      const sep = redirectUri.includes('?') ? '&' : '?';
      const url = `${redirectUri}${sep}code=${encodeURIComponent(code)}${state ? `&state=${encodeURIComponent(state)}` : ''}`;
      setStep('done');
      window.location.href = url;
    } catch {
      setError('Something went wrong. Please try again.');
      setSubmitting(false);
    }
  };

  const handleDeny = () => {
    if (redirectUri) {
      const sep = redirectUri.includes('?') ? '&' : '?';
      window.location.href = `${redirectUri}${sep}error=access_denied${state ? `&state=${encodeURIComponent(state)}` : ''}`;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-600 rounded-2xl mb-4">
            <span className="text-white text-2xl font-bold">A</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">AI CMS</h1>
          <p className="text-gray-500 text-sm mt-1">
            {step === 'allow'
              ? 'An AI tool wants to connect to your account'
              : 'Sign in to connect your AI tool'}
          </p>
        </div>

        {/* Login form */}
        {step === 'login' && (
          <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  required
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="you@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="••••••••"
                />
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
              >
                {submitting ? 'Signing in…' : 'Continue'}
              </button>
            </form>
          </div>
        )}

        {/* Allow / deny */}
        {step === 'allow' && (
          <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-5">
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-900">This will allow your AI tool to:</p>
              <ul className="text-sm text-gray-600 space-y-1.5">
                {[
                  'View and manage your sites',
                  'Create and edit page content',
                  'Publish changes on your behalf',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <svg className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {error && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <div className="flex gap-3">
              <button
                onClick={handleDeny}
                className="flex-1 border border-gray-300 text-gray-700 font-medium py-2.5 rounded-lg text-sm hover:bg-gray-50 transition-colors"
              >
                Deny
              </button>
              <button
                onClick={handleAllow}
                disabled={submitting}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
              >
                {submitting ? 'Connecting…' : 'Allow'}
              </button>
            </div>

            <p className="text-xs text-gray-400 text-center">
              You can revoke this access anytime from the Connect AI page in your dashboard.
            </p>
          </div>
        )}

        {/* Done */}
        {step === 'done' && (
          <div className="bg-white rounded-2xl shadow-sm border p-6 text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="font-medium text-gray-900">Connected!</p>
            <p className="text-sm text-gray-500 mt-1">Redirecting you back…</p>
          </div>
        )}

        {/* Loading */}
        {step === 'loading' && (
          <div className="bg-white rounded-2xl shadow-sm border p-6 flex justify-center">
            <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

      </div>
    </div>
  );
}

export default function ConnectPage() {
  return (
    <Suspense>
      <ConnectContent />
    </Suspense>
  );
}
