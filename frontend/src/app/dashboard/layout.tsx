'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { DashboardSidebar } from '@/components/admin/sidebar';
import { Toaster } from '@/components/ui/toaster';
import api from '@/lib/api';
import { Mail, X, ShieldAlert, Sparkles } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, planChangedTo, clearPlanChanged } = useAuth();
  const router = useRouter();
  const [bannerDismissed, setBannerDismissed] = useState(false);
  const [resent, setResent] = useState(false);
  const [adminTokenBackup, setAdminTokenBackup] = useState<string | null>(null);

  useEffect(() => {
    setAdminTokenBackup(localStorage.getItem('admin_token_backup'));
  }, []);

  useEffect(() => {
    const meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
    if (adminTokenBackup) {
      if (meta) meta.content = '#7c3aed';
      else {
        const m = document.createElement('meta');
        m.name = 'theme-color';
        m.content = '#7c3aed';
        document.head.appendChild(m);
      }
    } else {
      if (meta) meta.content = '#ffffff';
    }
  }, [adminTokenBackup]);

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
  const showImpersonationBar = !!adminTokenBackup;

  const handleReturnToAdmin = () => {
    localStorage.setItem('token', adminTokenBackup!);
    localStorage.removeItem('admin_token_backup');
    window.location.href = '/dashboard/admin';
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {showImpersonationBar && (
        <>
          <div className="fixed top-0 left-0 right-0 z-50 bg-violet-600 px-4 py-2 flex items-center justify-between gap-4 text-sm text-white">
            <div className="flex items-center gap-2">
              <ShieldAlert size={15} className="flex-shrink-0" />
              <span>
                Viewing as <span className="font-semibold">{user.email}</span>
              </span>
            </div>
            <button
              onClick={handleReturnToAdmin}
              className="flex items-center gap-1.5 bg-white/20 hover:bg-white/30 rounded px-2.5 py-1 font-medium text-xs transition-colors flex-shrink-0"
            >
              <X size={12} />
              Back to Admin
            </button>
          </div>
          {/* spacer to push content below fixed bar */}
          <div className="h-9 shrink-0" />
        </>
      )}
      <div className="flex flex-1 overflow-hidden">
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
      </div>
      <Toaster />

      {/* Plan change notification modal */}
      <Dialog open={!!planChangedTo} onOpenChange={(open) => !open && clearPlanChanged()}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles size={18} className="text-violet-500" />
              Your plan has been updated
            </DialogTitle>
            <DialogDescription>
              Your subscription has been changed to{' '}
              <span className="font-semibold capitalize text-gray-900">{planChangedTo}</span> by an administrator.
              Your new features and site limits are active immediately.
            </DialogDescription>
          </DialogHeader>
          <Button onClick={clearPlanChanged} className="w-full bg-violet-600 hover:bg-violet-700">
            Got it
          </Button>
        </DialogContent>
      </Dialog>
    </div>
  );
}
