"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface CtaContent {
  headline: string;
  subheadline?: string;
  button_label: string;
  button_href?: string;
}

interface Props {
  content: CtaContent;
  onChange: (content: CtaContent) => void;
}

export function CtaEditor({ content, onChange }: Props) {
  const set = (patch: Partial<CtaContent>) => onChange({ ...content, ...patch });
  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label>Headline *</Label>
        <Input value={content.headline || ""} onChange={(e) => set({ headline: e.target.value })} placeholder="Your call to action headline" />
      </div>
      <div className="space-y-1.5">
        <Label>Subheadline</Label>
        <Textarea value={content.subheadline || ""} onChange={(e) => set({ subheadline: e.target.value })} placeholder="Supporting text" rows={2} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label>Button Label *</Label>
          <Input value={content.button_label || ""} onChange={(e) => set({ button_label: e.target.value })} placeholder="Get Started" />
        </div>
        <div className="space-y-1.5">
          <Label>Button URL</Label>
          <Input value={content.button_href || ""} onChange={(e) => set({ button_href: e.target.value })} placeholder="https://... or #anchor" />
        </div>
      </div>
    </div>
  );
}
