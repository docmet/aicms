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
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          onClick={onNavigate}
          className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
            pathname === item.href
              ? 'bg-blue-50 text-blue-600 font-medium'
              : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          <item.icon size={20} />
          {item.name}
        </Link>
      ))}
    </>
  );
}

export function DashboardSidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const visibleItems = navItems.filter((item) => !item.adminOnly || user?.is_admin);

  const userInitial = user?.email?.[0].toUpperCase() ?? '?';

  return (
    <>
      {/* ── Mobile top bar ─────────────────────────────────────────────────── */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 bg-white border-b flex items-center justify-between px-4 h-14">
        <Link href="/dashboard" className="text-lg font-bold text-blue-600">
          My<span className="text-violet-600">Storey</span>
        </Link>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">
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
              className="flex items-center gap-3 px-4 py-2 rounded-lg text-red-600 hover:bg-red-50 w-full text-left"
            >
              <LogOut size={20} />
              Logout
            </button>
          </div>
        </>
      )}

      {/* Mobile spacer */}
      <div className="md:hidden h-14 flex-shrink-0" />

      {/* ── Desktop sidebar ────────────────────────────────────────────────── */}
      <aside className="hidden md:flex w-64 bg-white border-r min-h-screen flex-col">
        <div className="p-6 border-b">
          <Link href="/dashboard" className="text-xl font-bold text-blue-600">
            My<span className="text-violet-600">Storey</span>
          </Link>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <NavLinks items={visibleItems} pathname={pathname} />
        </nav>
        <div className="p-4 border-t mt-auto">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="w-full justify-start gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                  {userInitial}
                </div>
                <span className="truncate flex-1 text-left">{user?.email}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuItem onClick={logout} className="text-red-600 gap-2">
                <LogOut size={16} />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </aside>
    </>
  );
}
