'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { DashboardSidebar } from '@/components/admin/sidebar';
import { Toaster } from '@/components/ui/toaster';
import api from '@/lib/api';
import { Mail, X } from 'lucide-react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [bannerDismissed, setBannerDismissed] = useState(false);
  const [resent, setResent] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [loading, user, router]);

  const handleResend = async () => {
    if (!user) return;
    await api.post('/auth/resend-verification', { email: user.email }).catch(() => {});
    setResent(true);
  };

  if (loading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-6 h-6 border-2 border-violet-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const showBanner = !bannerDismissed && user && !user.email_verified;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        {showBanner && (
          <div className="bg-amber-50 border-b border-amber-200 px-4 py-2.5 flex items-center justify-between gap-4 text-sm">
            <div className="flex items-center gap-2 text-amber-800">
              <Mail size={15} className="flex-shrink-0" />
              <span>
                Please confirm your email address.{' '}
                {resent ? (
                  <span className="font-medium text-green-700">Link sent!</span>
                ) : (
                  <button
                    onClick={handleResend}
                    className="underline font-medium hover:text-amber-900"
                  >
                    Resend confirmation email
                  </button>
                )}
              </span>
            </div>
            <button onClick={() => setBannerDismissed(true)} className="text-amber-500 hover:text-amber-700 flex-shrink-0">
              <X size={15} />
            </button>
          </div>
        )}
        <main className="flex-1 p-4 md:p-8 overflow-y-auto">
          <div className="max-w-6xl mx-auto pt-14 md:pt-0">{children}</div>
        </main>
      </div>
      <Toaster />
    </div>
  );
}
