'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import api from '@/lib/api';
import { ArrowRight, Sparkles, Check, Loader2, Settings } from 'lucide-react';

const PLAN_CONFIG = {
  free: {
    label: 'Free',
    color: 'text-gray-600 bg-gray-100',
    sites: 1,
    badge: true,
    customDomain: false,
    upgradeMsg: 'Upgrade to Pro for 3 sites, custom domains, and no MyStorey badge.',
    upgradeCta: 'Upgrade to Pro — $9.99/mo',
    upgradeHref: '/dashboard/billing?plan=pro',
  },
  pro: {
    label: 'Pro',
    color: 'text-violet-700 bg-violet-100',
    sites: 3,
    badge: false,
    customDomain: true,
    upgradeMsg: 'Upgrade to Agency for 15 sites and upcoming AI automation features.',
    upgradeCta: 'Upgrade to Agency — $99/mo',
    upgradeHref: '/dashboard/billing?plan=agency',
  },
  agency: {
    label: 'Agency',
    color: 'text-indigo-700 bg-indigo-100',
    sites: 15,
    badge: false,
    customDomain: true,
    upgradeMsg: null,
    upgradeCta: null,
    upgradeHref: null,
  },
};

export default function SettingsPage() {
  const { user } = useAuth();
  const plan = user?.plan ?? 'free';
  const config = PLAN_CONFIG[plan];
  const [portalLoading, setPortalLoading] = useState(false);
  const [portalError, setPortalError] = useState('');

  const handlePortal = async () => {
    setPortalLoading(true);
    setPortalError('');
    try {
      const res = await api.get('/billing/portal');
      window.location.href = res.data.portal_url;
    } catch {
      setPortalError('Could not open subscription portal. Contact support.');
      setPortalLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-500 mt-0.5">Manage your account and subscription</p>
      </div>

      {/* Account */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-gray-900">Account</h2>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1.5">Email address</label>
          <input
            value={user?.email ?? ''}
            disabled
            className="w-full px-3.5 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-600 bg-gray-50"
          />
          <p className="text-xs text-gray-400 mt-1">Email cannot be changed.</p>
        </div>
      </div>

      {/* Plan */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-900">Subscription</h2>
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${config.color}`}>
            {config.label}
          </span>
        </div>

        <ul className="space-y-2.5">
          {[
            `${config.sites} website${config.sites !== 1 ? 's' : ''}`,
            config.customDomain ? 'Custom domains' : 'Free mystorey.io subdomain only',
            config.badge ? '"Made with MyStorey" badge on sites' : 'No badge',
          ].map((feat) => (
            <li key={feat} className="flex items-center gap-2.5 text-sm text-gray-600">
              <Check size={14} className="text-violet-500 flex-shrink-0" />
              {feat}
            </li>
          ))}
        </ul>

        {config.upgradeMsg && config.upgradeCta && config.upgradeHref && (
          <div className="border-t border-gray-100 pt-4">
            <p className="text-xs text-gray-500 mb-3">{config.upgradeMsg}</p>
            <Link
              href={config.upgradeHref}
              className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              <Sparkles size={12} />
              {config.upgradeCta}
              <ArrowRight size={12} />
            </Link>
          </div>
        )}

        {(plan === 'pro' || plan === 'agency') && (
          <div className="border-t border-gray-100 pt-4 space-y-2">
            {plan === 'agency' && (
              <p className="text-xs text-gray-500">AI automation features are coming soon.</p>
            )}
            {portalError && (
              <p className="text-xs text-red-600">{portalError}</p>
            )}
            <button
              onClick={handlePortal}
              disabled={portalLoading}
              className="inline-flex items-center gap-2 border border-gray-200 hover:border-gray-300 text-gray-600 hover:text-gray-900 text-xs font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              {portalLoading ? (
                <><Loader2 size={12} className="animate-spin" /> Opening…</>
              ) : (
                <><Settings size={12} /> Manage subscription</>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
