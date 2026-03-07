"use client";

import { ImagePicker } from "@/components/admin/ImagePicker";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Trash2 } from "lucide-react";

interface TestimonialItem {
  quote: string;
  name: string;
  role?: string;
  company?: string;
  avatar_url?: string | null;
}

interface TestimonialsContent {
  headline?: string;
  items: TestimonialItem[];
}

interface Props {
  siteId: string;
  content: TestimonialsContent;
  onChange: (content: TestimonialsContent) => void;
}

export function TestimonialsEditor({ siteId, content, onChange }: Props) {
  const set = (patch: Partial<TestimonialsContent>) => onChange({ ...content, ...patch });
  const items = content.items || [];

  const setItem = (i: number, patch: Partial<TestimonialItem>) => {
    set({ items: items.map((item, idx) => (idx === i ? { ...item, ...patch } : item)) });
  };
  const addItem = () => set({ items: [...items, { quote: "", name: "" }] });
  const removeItem = (i: number) => set({ items: items.filter((_, idx) => idx !== i) });

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label>Section Headline</Label>
        <Input value={content.headline || ""} onChange={(e) => set({ headline: e.target.value })} placeholder='e.g. "What Our Customers Say"' />
      </div>
      <div>
        <div className="flex items-center justify-between mb-2">
          <Label>Testimonials ({items.length})</Label>
          <Button type="button" size="sm" variant="outline" onClick={addItem}>
            <Plus size={14} className="mr-1" /> Add
          </Button>
        </div>
        <div className="space-y-3">
          {items.map((item, i) => (
            <div key={i} className="p-3 border rounded-lg bg-muted/30 space-y-2">
              <div className="flex gap-2">
                <Textarea value={item.quote} onChange={(e) => setItem(i, { quote: e.target.value })} placeholder="Quote *" rows={2} className="flex-1 text-sm" />
                <Button type="button" variant="ghost" size="icon" className="shrink-0 text-muted-foreground hover:text-destructive" onClick={() => removeItem(i)}>
                  <Trash2 size={14} />
                </Button>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <Input value={item.name} onChange={(e) => setItem(i, { name: e.target.value })} placeholder="Name *" className="text-sm" />
                <Input value={item.role || ""} onChange={(e) => setItem(i, { role: e.target.value })} placeholder="Role" className="text-sm" />
                <Input value={item.company || ""} onChange={(e) => setItem(i, { company: e.target.value })} placeholder="Company" className="text-sm" />
              </div>
              <ImagePicker
                siteId={siteId}
                value={item.avatar_url}
                onChange={(url) => setItem(i, { avatar_url: url })}
                label="Avatar photo"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
