'use client';

import { useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { ArrowRight, Mail } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Always show success to avoid email enumeration
    await api.post('/auth/forgot-password', { email }).catch(() => {});
    setSubmitted(true);
    setIsSubmitting(false);
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <Link href="/login" className="text-xl font-bold text-gray-900 mb-10 block">
          My<span className="text-violet-600">Storey</span>
        </Link>

        {submitted ? (
          <div className="space-y-4">
            <div className="w-12 h-12 rounded-full bg-violet-100 flex items-center justify-center">
              <Mail className="w-6 h-6 text-violet-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Check your inbox</h1>
            <p className="text-gray-500 text-sm leading-relaxed">
              If <strong>{email}</strong> has an account, we sent a password reset link. It expires in 1 hour.
            </p>
            <Link href="/login" className="inline-flex items-center gap-2 text-sm text-violet-600 hover:text-violet-700 mt-2">
              Back to sign in <ArrowRight size={14} />
            </Link>
          </div>
        ) : (
          <>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">Forgot your password?</h1>
            <p className="text-sm text-gray-500 mb-8">
              Enter your email and we&apos;ll send you a reset link.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
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

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-700 text-white font-semibold py-2.5 rounded-lg text-sm transition-all disabled:opacity-50"
              >
                {isSubmitting ? 'Sending…' : 'Send reset link'}
                {!isSubmitting && <ArrowRight size={15} />}
              </button>

              <div className="text-center">
                <Link href="/login" className="text-sm text-gray-500 hover:text-gray-700">
                  Back to sign in
                </Link>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
