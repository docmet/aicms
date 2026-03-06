"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import api from "@/lib/api";
import { ArrowLeft, BarChart2, ExternalLink, Globe, TrendingUp } from "lucide-react";

interface DailyRow {
  date: string;
  views: number;
}

interface PageStatsRow {
  page_path: string;
  views: number;
}

interface ReferrerRow {
  referrer: string;
  views: number;
}

interface Analytics {
  total_views: number;
  unique_pages: number;
  top_pages: PageStatsRow[];
  top_referrers: ReferrerRow[];
  daily: DailyRow[];
  days: number;
}

function SparkBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="flex items-center gap-3 w-full">
      <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
        <div
          className="h-2 rounded-full"
          style={{ width: `${pct}%`, background: "var(--color-primary, #7c3aed)" }}
        />
      </div>
      <span className="text-xs text-muted-foreground w-8 text-right">{value}</span>
    </div>
  );
}

function DailyChart({ daily }: { daily: DailyRow[] }) {
  if (daily.length === 0) return <p className="text-sm text-muted-foreground">No data yet.</p>;
  const max = Math.max(...daily.map((d) => d.views), 1);
  return (
    <div className="flex items-end gap-1 h-24">
      {daily.map((d) => {
        const h = Math.max(4, Math.round((d.views / max) * 96));
        return (
          <div key={d.date} className="flex-1 flex flex-col items-center gap-1 group relative">
            <div
              className="w-full rounded-t-sm"
              style={{ height: `${h}px`, background: "var(--color-primary, #7c3aed)", opacity: 0.8 }}
            />
            <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 bg-popover text-popover-foreground text-[10px] px-1.5 py-0.5 rounded shadow hidden group-hover:block whitespace-nowrap z-10">
              {d.date}: {d.views}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function AnalyticsPage({ params }: { params: Promise<{ site_id: string }> }) {
  const { site_id } = use(params);
  const router = useRouter();
  const [data, setData] = useState<Analytics | null>(null);
  const [days, setDays] = useState("30");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .get(`/sites/${site_id}/analytics?days=${days}`)
      .then((r) => setData(r.data as Analytics))
      .catch(() => router.push("/dashboard"))
      .finally(() => setLoading(false));
  }, [site_id, days, router]);

  return (
    <div className="container max-w-4xl mx-auto py-8 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href={`/dashboard/sites/${site_id}`}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft size={18} />
          </Link>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BarChart2 size={22} /> Analytics
          </h1>
        </div>
        <Select value={days} onValueChange={setDays}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">Last 7 days</SelectItem>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {loading || !data ? (
        <div className="flex items-center justify-center py-24 text-muted-foreground text-sm">
          Loading analytics…
        </div>
      ) : (
        <>
          {/* KPI cards */}
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1.5">
                  <TrendingUp size={14} /> Total pageviews
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{data.total_views.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground mt-1">last {data.days} days</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1.5">
                  <Globe size={14} /> Unique pages viewed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{data.unique_pages}</p>
                <p className="text-xs text-muted-foreground mt-1">distinct paths</p>
              </CardContent>
            </Card>
          </div>

          {/* Daily chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Pageviews over time</CardTitle>
            </CardHeader>
            <CardContent>
              <DailyChart daily={data.daily} />
            </CardContent>
          </Card>

          {/* Top pages + referrers */}
          <div className="grid md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Top pages</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.top_pages.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No data yet.</p>
                ) : (
                  data.top_pages.map((p, i) => (
                    <div key={i} className="space-y-1">
                      <p className="text-sm font-mono truncate">{p.page_path || "/"}</p>
                      <SparkBar value={p.views} max={data.top_pages[0].views} />
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-1.5">
                  <ExternalLink size={13} /> Top referrers
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.top_referrers.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No referrer data yet.</p>
                ) : (
                  data.top_referrers.map((r, i) => (
                    <div key={i} className="space-y-1">
                      <p className="text-sm truncate">{r.referrer}</p>
                      <SparkBar value={r.views} max={data.top_referrers[0].views} />
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          <p className="text-xs text-center text-muted-foreground">
            Privacy-first analytics — no cookies, no personal data stored.
          </p>
        </>
      )}
    </div>
  );
}
