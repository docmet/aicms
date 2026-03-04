'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { LayoutDashboard, Globe, Settings, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'My Sites', href: '/dashboard/sites', icon: Globe },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export function DashboardSidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="w-64 bg-white border-r min-h-screen flex flex-col">
      <div className="p-6 border-b">
        <Link href="/dashboard" className="text-xl font-bold text-blue-600">
          AI CMS
        </Link>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
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
      </nav>
      <div className="p-4 border-t mt-auto">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="w-full justify-start gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                {user?.email?.[0].toUpperCase()}
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
  );
}
