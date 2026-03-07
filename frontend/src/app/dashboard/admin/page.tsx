"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Users, Globe, FileText, Layers, Trash2, UserCheck, Shield, Search, Pencil, Check, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface UserWithStats {
  id: string;
  email: string;
  name: string | null;
  phone: string | null;
  is_admin: boolean;
  plan: 'free' | 'pro' | 'agency';
  site_count: number;
  created_at: string;
}

interface PlatformStats {
  total_users: number;
  total_sites: number;
  total_pages: number;
  total_sections: number;
}

// Inline editable cell
function EditableCell({
  value,
  onSave,
  placeholder,
}: {
  value: string | null;
  onSave: (v: string) => Promise<void>;
  placeholder?: string;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value ?? '');
  const [saving, setSaving] = useState(false);

  const commit = async () => {
    setSaving(true);
    await onSave(draft.trim());
    setSaving(false);
    setEditing(false);
  };

  const cancel = () => {
    setDraft(value ?? '');
    setEditing(false);
  };

  if (editing) {
    return (
      <div className="flex items-center gap-1 min-w-[140px]">
        <input
          autoFocus
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') commit(); if (e.key === 'Escape') cancel(); }}
          className="flex-1 text-xs border border-violet-400 rounded px-2 py-1 outline-none w-full"
          disabled={saving}
        />
        <button onClick={commit} disabled={saving} className="text-green-600 hover:text-green-800">
          <Check size={13} />
        </button>
        <button onClick={cancel} className="text-gray-400 hover:text-gray-600">
          <X size={13} />
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => { setDraft(value ?? ''); setEditing(true); }}
      className="group flex items-center gap-1 text-left hover:text-violet-700 transition-colors max-w-[200px]"
      title="Click to edit"
    >
      <span className="truncate">{value || <span className="text-gray-300 italic">{placeholder ?? 'None'}</span>}</span>
      <Pencil size={11} className="opacity-0 group-hover:opacity-100 flex-shrink-0 text-gray-400" />
    </button>
  );
}

export default function AdminPage() {
  const { user, refreshUser } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [users, setUsers] = useState<UserWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  // Guard: redirect non-admins
  useEffect(() => {
    if (user && !user.is_admin) {
      router.replace("/dashboard");
    }
  }, [user, router]);

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, usersRes] = await Promise.all([
        api.get("/admin/stats"),
        api.get("/admin/users"),
      ]);
      setStats(statsRes.data as PlatformStats);
      setUsers(usersRes.data as UserWithStats[]);
    } catch {
      toast({ title: "Failed to load admin data", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    if (user?.is_admin) fetchData();
  }, [user, fetchData]);

  const patchUser = async (userId: string, payload: Record<string, unknown>) => {
    await api.patch(`/admin/users/${userId}`, payload);
    await fetchData();
  };

  const handleImpersonate = async (userId: string, userEmail: string) => {
    try {
      const res = await api.post(`/admin/impersonate/${userId}`);
      const { access_token } = res.data as { access_token: string };
      const adminToken = localStorage.getItem("token");
      localStorage.setItem("admin_token_backup", adminToken ?? "");
      localStorage.setItem("token", access_token);
      toast({ title: `Impersonating ${userEmail}. Refresh to switch.` });
      window.location.href = "/dashboard";
    } catch {
      toast({ title: "Impersonation failed", variant: "destructive" });
    }
  };

  const handleDeleteUser = async (userId: string, userEmail: string) => {
    if (!confirm(`Delete user ${userEmail} and all their sites? This cannot be undone.`)) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      toast({ title: `User ${userEmail} deleted` });
      fetchData();
    } catch {
      toast({ title: "Delete failed", variant: "destructive" });
    }
  };

  const handleToggleAdmin = async (userId: string, currentlyAdmin: boolean) => {
    try {
      await patchUser(userId, { is_admin: !currentlyAdmin });
      toast({ title: "Admin status updated" });
    } catch {
      toast({ title: "Update failed", variant: "destructive" });
    }
  };

  const handleChangePlan = async (userId: string, plan: string) => {
    try {
      await patchUser(userId, { plan });
      toast({ title: `Plan updated to ${plan}` });
      if (userId === user?.id) await refreshUser();
    } catch {
      toast({ title: "Plan update failed", variant: "destructive" });
    }
  };

  if (!user?.is_admin) return null;

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      </div>
    );
  }

  const q = search.toLowerCase().trim();
  const filtered = q
    ? users.filter(
        (u) =>
          u.email.toLowerCase().includes(q) ||
          (u.name ?? '').toLowerCase().includes(q) ||
          (u.phone ?? '').toLowerCase().includes(q)
      )
    : users;

  const statCards = stats
    ? [
        { label: "Total Users", value: stats.total_users, icon: Users, color: "text-blue-600" },
        { label: "Active Sites", value: stats.total_sites, icon: Globe, color: "text-green-600" },
        { label: "Pages", value: stats.total_pages, icon: FileText, color: "text-purple-600" },
        { label: "Content Sections", value: stats.total_sections, icon: Layers, color: "text-orange-600" },
      ]
    : [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Shield size={28} className="text-blue-600" />
          Admin Panel
        </h1>
        <p className="text-gray-500 mt-1">Platform management and user oversight</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <Card key={label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">{label}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Icon size={20} className={color} />
                <span className="text-2xl font-bold">{value}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Users table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <CardTitle>All Users</CardTitle>
          <div className="relative">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search name, email, phone…"
              className="text-xs pl-8 pr-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-500 w-56"
            />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Email</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Name</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Phone</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Role</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Plan</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Sites</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Joined</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filtered.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">
                      <EditableCell
                        value={u.email}
                        placeholder="email"
                        onSave={async (v) => {
                          await patchUser(u.id, { email: v });
                          toast({ title: 'Email updated' });
                        }}
                      />
                      {u.id === user.id && (
                        <span className="ml-1 text-xs text-gray-400">(you)</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      <EditableCell
                        value={u.name}
                        placeholder="no name"
                        onSave={async (v) => {
                          await patchUser(u.id, { name: v || null });
                          toast({ title: 'Name updated' });
                        }}
                      />
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      <EditableCell
                        value={u.phone}
                        placeholder="no phone"
                        onSave={async (v) => {
                          await patchUser(u.id, { phone: v || null });
                          toast({ title: 'Phone updated' });
                        }}
                      />
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={u.is_admin ? "default" : "secondary"}>
                        {u.is_admin ? "Admin" : "User"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={u.plan}
                        onChange={(e) => handleChangePlan(u.id, e.target.value)}
                        className="text-xs border border-gray-200 rounded px-2 py-1 bg-white text-gray-700 cursor-pointer"
                      >
                        <option value="free">Free</option>
                        <option value="pro">Pro</option>
                        <option value="agency">Agency</option>
                      </select>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{u.site_count}</td>
                    <td className="px-4 py-3 text-gray-500">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-1">
                        {u.id !== user.id && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Impersonate user"
                              onClick={() => handleImpersonate(u.id, u.email)}
                            >
                              <UserCheck size={15} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              title={u.is_admin ? "Remove admin" : "Make admin"}
                              onClick={() => handleToggleAdmin(u.id, u.is_admin)}
                            >
                              <Shield size={15} className={u.is_admin ? "text-blue-600" : "text-gray-400"} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-500 hover:text-red-700"
                              title="Delete user"
                              onClick={() => handleDeleteUser(u.id, u.email)}
                            >
                              <Trash2 size={15} />
                            </Button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-sm text-gray-400">
                      No users match your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
