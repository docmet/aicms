"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface ContactContent {
  headline?: string;
  email?: string;
  phone?: string;
  address?: string;
  hours?: string;
}

interface Props {
  content: ContactContent;
  onChange: (content: ContactContent) => void;
}

export function ContactEditor({ content, onChange }: Props) {
  const set = (patch: Partial<ContactContent>) => onChange({ ...content, ...patch });
  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label>Section Headline</Label>
        <Input value={content.headline || ""} onChange={(e) => set({ headline: e.target.value })} placeholder='e.g. "Get in Touch"' />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label>Email</Label>
          <Input type="email" value={content.email || ""} onChange={(e) => set({ email: e.target.value })} placeholder="hello@example.com" />
        </div>
        <div className="space-y-1.5">
          <Label>Phone</Label>
          <Input value={content.phone || ""} onChange={(e) => set({ phone: e.target.value })} placeholder="+1 (555) 000-0000" />
        </div>
      </div>
      <div className="space-y-1.5">
        <Label>Address</Label>
        <Input value={content.address || ""} onChange={(e) => set({ address: e.target.value })} placeholder="123 Main St, City, State ZIP" />
      </div>
      <div className="space-y-1.5">
        <Label>Hours</Label>
        <Input value={content.hours || ""} onChange={(e) => set({ hours: e.target.value })} placeholder="Mon–Fri 9am–5pm" />
      </div>
    </div>
  );
}
