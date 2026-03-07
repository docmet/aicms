"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Users, Globe, FileText, Layers, Trash2, UserCheck, Shield } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface UserWithStats {
  id: string;
  email: string;
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

export default function AdminPage() {
  const { user, refreshUser } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [users, setUsers] = useState<UserWithStats[]>([]);
  const [loading, setLoading] = useState(true);

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

  const handleImpersonate = async (userId: string, userEmail: string) => {
    try {
      const res = await api.post(`/admin/impersonate/${userId}`);
      const { access_token } = res.data as { access_token: string };
      // Store the current admin token so we can restore it
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
      await api.patch(`/admin/users/${userId}`, { is_admin: !currentlyAdmin });
      toast({ title: `Admin status updated` });
      fetchData();
    } catch {
      toast({ title: "Update failed", variant: "destructive" });
    }
  };

  const handleChangePlan = async (userId: string, plan: string) => {
    try {
      await api.patch(`/admin/users/${userId}`, { plan });
      toast({ title: `Plan updated to ${plan}` });
      fetchData();
      // If admin changed their own plan, refresh auth context so sidebar + limits update immediately
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
        <CardHeader>
          <CardTitle>All Users</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Email</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Role</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Plan</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Sites</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Joined</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">
                      {u.email}
                      {u.id === user.id && (
                        <span className="ml-2 text-xs text-gray-400">(you)</span>
                      )}
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
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

    </div>
  );
}
