"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Trash2 } from "lucide-react";

interface FeatureItem {
  icon?: string;
  title: string;
  description?: string;
}

interface FeaturesContent {
  headline?: string;
  subheadline?: string;
  items: FeatureItem[];
}

interface Props {
  content: FeaturesContent;
  onChange: (content: FeaturesContent) => void;
}

export function FeaturesEditor({ content, onChange }: Props) {
  const set = (patch: Partial<FeaturesContent>) => onChange({ ...content, ...patch });
  const items = content.items || [];

  const setItem = (i: number, patch: Partial<FeatureItem>) => {
    const next = items.map((item, idx) => (idx === i ? { ...item, ...patch } : item));
    set({ items: next });
  };
  const addItem = () => set({ items: [...items, { title: "" }] });
  const removeItem = (i: number) => set({ items: items.filter((_, idx) => idx !== i) });

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label>Headline</Label>
          <Input value={content.headline || ""} onChange={(e) => set({ headline: e.target.value })} placeholder="Section headline" />
        </div>
        <div className="space-y-1.5">
          <Label>Subheadline</Label>
          <Input value={content.subheadline || ""} onChange={(e) => set({ subheadline: e.target.value })} placeholder="Supporting text" />
        </div>
      </div>
      <div>
        <div className="flex items-center justify-between mb-2">
          <Label>Features ({items.length})</Label>
          <Button type="button" size="sm" variant="outline" onClick={addItem}>
            <Plus size={14} className="mr-1" /> Add Feature
          </Button>
        </div>
        <div className="space-y-3">
          {items.map((item, i) => (
            <div key={i} className="flex gap-2 p-3 border rounded-lg bg-muted/30">
              <div className="w-14 shrink-0 space-y-1">
                <Label className="text-xs">Icon</Label>
                <Input value={item.icon || ""} onChange={(e) => setItem(i, { icon: e.target.value })} placeholder="☕" className="text-center text-lg px-1" />
              </div>
              <div className="flex-1 space-y-1.5">
                <Input value={item.title} onChange={(e) => setItem(i, { title: e.target.value })} placeholder="Feature title *" />
                <Textarea value={item.description || ""} onChange={(e) => setItem(i, { description: e.target.value })} placeholder="Description" rows={2} className="text-sm" />
              </div>
              <Button type="button" variant="ghost" size="icon" className="shrink-0 text-muted-foreground hover:text-destructive" onClick={() => removeItem(i)}>
                <Trash2 size={14} />
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
