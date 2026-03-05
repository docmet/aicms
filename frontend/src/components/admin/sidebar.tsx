'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { LayoutDashboard, Settings, HelpCircle, Bot, LogOut, Shield, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, adminOnly: false },
  { name: 'Connect AI', href: '/dashboard/mcp', icon: Bot, adminOnly: false },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings, adminOnly: false },
  { name: 'Help', href: '/dashboard/help', icon: HelpCircle, adminOnly: false },
  { name: 'Admin', href: '/dashboard/admin', icon: Shield, adminOnly: true },
];

const PLAN_LABELS = { free: 'Free', pro: 'Pro', agency: 'Agency' };
const PLAN_COLORS = {
  free: 'bg-gray-100 text-gray-500',
  pro: 'bg-violet-100 text-violet-600',
  agency: 'bg-indigo-100 text-indigo-600',
};

function NavLinks({
  items,
  pathname,
  onNavigate,
}: {
  items: typeof navItems;
  pathname: string;
  onNavigate?: () => void;
}) {
  return (
    <>
      {items.map((item) => {
        const active = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
              active
                ? 'bg-violet-50 text-violet-700 font-medium'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <item.icon size={17} className={active ? 'text-violet-600' : ''} />
            {item.name}
          </Link>
        );
      })}
    </>
  );
}

export function DashboardSidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const visibleItems = navItems.filter((item) => !item.adminOnly || user?.is_admin);
  const plan = user?.plan ?? 'free';
  const userInitial = user?.email?.[0].toUpperCase() ?? '?';

  return (
    <>
      {/* ── Mobile top bar ─────────────────────────────────────────────────── */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 bg-white border-b flex items-center justify-between px-4 h-14">
        <Link href="/dashboard" className="text-base font-bold text-gray-900">
          My<span className="text-violet-600">Storey</span>
        </Link>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-violet-100 text-violet-600 flex items-center justify-center font-bold text-sm">
            {userInitial}
          </div>
          <button
            onClick={() => setMobileOpen((o) => !o)}
            className="p-2 rounded-lg text-gray-600 hover:bg-gray-100"
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile nav drawer */}
      {mobileOpen && (
        <>
          <div
            className="md:hidden fixed inset-0 z-30 bg-black/20"
            onClick={() => setMobileOpen(false)}
          />
          <div className="md:hidden fixed top-14 left-0 right-0 z-40 bg-white border-b shadow-lg px-4 py-3 space-y-1">
            <NavLinks
              items={visibleItems}
              pathname={pathname}
              onNavigate={() => setMobileOpen(false)}
            />
            <button
              onClick={() => { setMobileOpen(false); logout(); }}
              className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-red-500 hover:bg-red-50 w-full text-left"
            >
              <LogOut size={17} />
              Logout
            </button>
          </div>
        </>
      )}

      {/* Mobile spacer */}
      <div className="md:hidden h-14 flex-shrink-0" />

      {/* ── Desktop sidebar ────────────────────────────────────────────────── */}
      <aside className="hidden md:flex w-60 bg-white border-r min-h-screen flex-col">
        <div className="px-5 py-5 border-b">
          <Link href="/dashboard" className="text-base font-bold text-gray-900">
            My<span className="text-violet-600">Storey</span>
          </Link>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          <NavLinks items={visibleItems} pathname={pathname} />
        </nav>
        <div className="p-3 border-t mt-auto">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="w-full justify-start gap-3 h-auto py-2.5 px-2">
                <div className="w-8 h-8 rounded-full bg-violet-100 text-violet-600 flex items-center justify-center font-bold text-sm flex-shrink-0">
                  {userInitial}
                </div>
                <div className="flex flex-col items-start min-w-0">
                  <span className="truncate text-sm text-gray-800 font-medium w-full text-left">{user?.email}</span>
                  <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded mt-0.5 ${PLAN_COLORS[plan]}`}>
                    {PLAN_LABELS[plan]}
                  </span>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem onClick={logout} className="text-red-500 gap-2">
                <LogOut size={14} />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </aside>
    </>
  );
}
