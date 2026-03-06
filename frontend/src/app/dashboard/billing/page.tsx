'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import api from '@/lib/api';
import { Check, Sparkles, ArrowRight, Loader2 } from 'lucide-react';

const PLANS = {
  pro: {
    name: 'Pro',
    price: '$9.99',
    period: 'per month',
    description: 'For creators & freelancers',
    features: ['3 websites', 'Custom domains', 'Remove MyStorey badge', 'Priority support'],
    color: 'border-violet-400 bg-violet-50',
    badge: 'Most popular',
  },
  agency: {
    name: 'Agency',
    price: '$99',
    period: 'per month',
    description: 'For teams & agencies',
    features: ['15 websites', 'Custom domains', 'AI automations (coming soon)', 'Dedicated support'],
    color: 'border-indigo-400 bg-indigo-50',
    badge: null,
  },
};

function BillingContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const plan = (searchParams.get('plan') ?? 'pro') as 'pro' | 'agency';
  const paymentComplete = searchParams.get('payment_complete') === 'true';

  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const planInfo = PLANS[plan] ?? PLANS.pro;
  const alreadyOnPlan = user?.plan === plan || user?.plan === 'agency';

  // After Revolut redirects back, verify the payment
  useEffect(() => {
    if (!paymentComplete) return;
    setVerifying(true);
    api
      .post(`/billing/verify?order_id=redirect&plan=${plan}`)
      .then(async (res) => {
        if (res.data.success) {
          await refreshUser();
          setSuccess(true);
        } else {
          setError('Payment could not be confirmed yet. Please refresh in a moment.');
        }
      })
      .catch(() => setError('Could not verify payment. Contact support if charged.'))
      .finally(() => setVerifying(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handlePay = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.post(`/billing/checkout?plan=${plan}`);
      window.location.href = res.data.checkout_url;
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      setError(e.response?.data?.detail || 'Could not start checkout. Try again.');
      setLoading(false);
    }
  };

  if (verifying) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
        <p className="text-gray-500 text-sm">Confirming your payment…</p>
      </div>
    );
  }

  if (success) {
    return (
      <div className="max-w-md mx-auto py-24 text-center space-y-4">
        <div className="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto">
          <Check className="w-7 h-7 text-green-600" />
        </div>
        <h1 className="text-2xl font-bold">You&apos;re on {planInfo.name}!</h1>
        <p className="text-gray-500 text-sm">Your plan has been upgraded. Enjoy the new features.</p>
        <button
          onClick={() => router.push('/dashboard')}
          className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-700 text-white font-semibold px-6 py-2.5 rounded-lg text-sm transition-colors"
        >
          Go to Dashboard <ArrowRight size={14} />
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upgrade your plan</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          {alreadyOnPlan
            ? `You're already on the ${user?.plan} plan.`
            : `You're currently on the ${user?.plan ?? 'free'} plan.`}
        </p>
      </div>

      {/* Plan card */}
      <div className={`rounded-2xl border-2 p-8 space-y-5 ${planInfo.color}`}>
        <div className="flex items-start justify-between">
          <div>
            {planInfo.badge && (
              <span className="inline-flex items-center gap-1 bg-violet-600 text-white text-xs font-medium px-2.5 py-1 rounded-full mb-2">
                <Sparkles size={10} /> {planInfo.badge}
              </span>
            )}
            <h2 className="text-xl font-bold text-gray-900">{planInfo.name}</h2>
            <p className="text-sm text-gray-500">{planInfo.description}</p>
          </div>
          <div className="text-right">
            <span className="text-3xl font-bold text-gray-900">{planInfo.price}</span>
            <span className="text-sm text-gray-400 ml-1">/{planInfo.period}</span>
          </div>
        </div>

        <ul className="space-y-2.5">
          {planInfo.features.map((feat) => (
            <li key={feat} className="flex items-center gap-2.5 text-sm text-gray-700">
              <Check size={14} className="text-violet-500 flex-shrink-0" />
              {feat}
            </li>
          ))}
        </ul>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {alreadyOnPlan ? (
        <button
          onClick={() => router.push('/dashboard/settings')}
          className="w-full flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 rounded-xl text-sm transition-colors"
        >
          Back to Settings
        </button>
      ) : (
        <button
          onClick={handlePay}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white font-semibold py-3 rounded-xl text-sm transition-colors"
        >
          {loading ? (
            <><Loader2 size={15} className="animate-spin" /> Redirecting to payment…</>
          ) : (
            <>Pay with Revolut — {planInfo.price}/mo <ArrowRight size={14} /></>
          )}
        </button>
      )}

      <p className="text-xs text-gray-400 text-center">
        Secure payment via Revolut. Cancel anytime by contacting support.
      </p>
    </div>
  );
}

export default function BillingPage() {
  return (
    <Suspense>
      <BillingContent />
    </Suspense>
  );
}
