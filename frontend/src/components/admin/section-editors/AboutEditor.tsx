"use client";

import { ImagePicker } from "@/components/admin/ImagePicker";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Trash2 } from "lucide-react";

interface StatItem {
  number: string;
  label: string;
}

interface AboutContent {
  headline: string;
  body: string;
  stats?: StatItem[];
  image_url?: string | null;
}

interface Props {
  siteId: string;
  content: AboutContent;
  onChange: (content: AboutContent) => void;
}

export function AboutEditor({ siteId, content, onChange }: Props) {
  const set = (patch: Partial<AboutContent>) => onChange({ ...content, ...patch });
  const stats = content.stats || [];

  const setStat = (i: number, patch: Partial<StatItem>) => {
    set({ stats: stats.map((s, idx) => (idx === i ? { ...s, ...patch } : s)) });
  };
  const addStat = () => set({ stats: [...stats, { number: "", label: "" }] });
  const removeStat = (i: number) => set({ stats: stats.filter((_, idx) => idx !== i) });

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label>Headline *</Label>
        <Input value={content.headline || ""} onChange={(e) => set({ headline: e.target.value })} placeholder="Your about headline" />
      </div>
      <div className="space-y-1.5">
        <Label>Body Text *</Label>
        <Textarea value={content.body || ""} onChange={(e) => set({ body: e.target.value })} placeholder="Your story..." rows={5} />
      </div>
      <ImagePicker
        siteId={siteId}
        value={content.image_url}
        onChange={(url) => set({ image_url: url })}
        label="Section Image"
        hint="Displayed alongside your about text. Recommended: 1200×800 px."
      />
      <div>
        <div className="flex items-center justify-between mb-2">
          <Label>Stats (optional)</Label>
          <Button type="button" size="sm" variant="outline" onClick={addStat} disabled={stats.length >= 4}>
            <Plus size={14} className="mr-1" /> Add Stat
          </Button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {stats.map((stat, i) => (
            <div key={i} className="flex gap-2 p-2 border rounded-lg bg-muted/30 items-center">
              <div className="flex-1 space-y-1">
                <Input value={stat.number} onChange={(e) => setStat(i, { number: e.target.value })} placeholder='e.g. "500+"' className="text-sm font-bold" />
                <Input value={stat.label} onChange={(e) => setStat(i, { label: e.target.value })} placeholder="Label" className="text-sm" />
              </div>
              <Button type="button" variant="ghost" size="icon" className="shrink-0 text-muted-foreground hover:text-destructive" onClick={() => removeStat(i)}>
                <Trash2 size={14} />
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
