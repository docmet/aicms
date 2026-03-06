'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';

export function NavAuthButtons() {
  const { user, loading } = useAuth();

  // Reserve space while loading to avoid layout shift
  if (loading) return <div className="w-32 h-8" />;

  if (user) {
    return (
      <Link
        href="/dashboard"
        className="text-sm font-medium bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Go to Dashboard
      </Link>
    );
  }

  return (
    <>
      <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900 transition-colors px-3 py-1.5">
        Sign in
      </Link>
      <Link
        href="/register"
        className="text-sm font-medium bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Get started free
      </Link>
    </>
  );
}
