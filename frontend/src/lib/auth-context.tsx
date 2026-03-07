'use client';

import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface User {
  id: string;
  email: string;
  is_admin: boolean;
  plan: 'free' | 'pro' | 'agency';
  email_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string, redirectTo?: string) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
  planChangedTo: string | null;
  clearPlanChanged: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [planChangedTo, setPlanChangedTo] = useState<string | null>(null);
  const planRef = useRef<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await api.get('/auth/me');
        setUser(response.data);
        planRef.current = response.data.plan;
      } catch {
        // Token invalid/expired — clear it and let each layout decide whether to redirect
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  // Poll /auth/me every 15s to detect externally-triggered plan changes (e.g. admin upgrade)
  useEffect(() => {
    const interval = setInterval(async () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      try {
        const response = await api.get('/auth/me');
        const fresh = response.data as User;
        if (planRef.current && fresh.plan !== planRef.current) {
          setPlanChangedTo(fresh.plan);
        }
        planRef.current = fresh.plan;
        setUser(fresh);
      } catch {
        // ignore — stale user stays
      }
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const login = (token: string, redirectTo?: string) => {
    localStorage.setItem('token', token);
    setLoading(true);
    api
      .get('/auth/me')
      .then((response) => {
        setUser(response.data);
        setLoading(false);
        router.push(redirectTo || '/dashboard');
      })
      .catch(() => {
        localStorage.removeItem('token');
        setLoading(false);
      });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    router.push('/login');
  };

  const refreshUser = async () => {
    try {
      const response = await api.get('/auth/me');
      planRef.current = response.data.plan;
      setUser(response.data);
    } catch {
      // ignore — stale user stays until next full reload
    }
  };

  const clearPlanChanged = () => setPlanChangedTo(null);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser, planChangedTo, clearPlanChanged }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
