"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface CtaButton {
  label: string;
  href: string;
}

interface HeroContent {
  headline: string;
  subheadline?: string;
  badge?: string;
  cta_primary?: CtaButton;
  cta_secondary?: CtaButton;
}

interface Props {
  content: HeroContent;
  onChange: (content: HeroContent) => void;
}

export function HeroEditor({ content, onChange }: Props) {
  const set = (patch: Partial<HeroContent>) => onChange({ ...content, ...patch });
  const setCta = (key: "cta_primary" | "cta_secondary", patch: Partial<CtaButton>) =>
    set({ [key]: { ...content[key], ...patch } as CtaButton });

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label>Headline *</Label>
        <Input value={content.headline || ""} onChange={(e) => set({ headline: e.target.value })} placeholder="Your main headline" />
      </div>
      <div className="space-y-1.5">
        <Label>Subheadline</Label>
        <Textarea value={content.subheadline || ""} onChange={(e) => set({ subheadline: e.target.value })} placeholder="Supporting text below headline" rows={2} />
      </div>
      <div className="space-y-1.5">
        <Label>Badge</Label>
        <Input value={content.badge || ""} onChange={(e) => set({ badge: e.target.value })} placeholder='e.g. "Now in beta"' />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <p className="text-sm font-medium">Primary Button</p>
          <Input value={content.cta_primary?.label || ""} onChange={(e) => setCta("cta_primary", { label: e.target.value })} placeholder="Label" />
          <Input value={content.cta_primary?.href || ""} onChange={(e) => setCta("cta_primary", { href: e.target.value })} placeholder="URL or #anchor" />
        </div>
        <div className="space-y-2">
          <p className="text-sm font-medium">Secondary Button</p>
          <Input value={content.cta_secondary?.label || ""} onChange={(e) => setCta("cta_secondary", { label: e.target.value })} placeholder="Label" />
          <Input value={content.cta_secondary?.href || ""} onChange={(e) => setCta("cta_secondary", { href: e.target.value })} placeholder="URL or #anchor" />
        </div>
      </div>
    </div>
  );
}
