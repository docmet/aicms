"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface CustomContent {
  title?: string;
  content?: string;
}

interface Props {
  content: CustomContent;
  onChange: (content: CustomContent) => void;
}

export function CustomEditor({ content, onChange }: Props) {
  const set = (patch: Partial<CustomContent>) => onChange({ ...content, ...patch });
  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label>Title</Label>
        <Input value={content.title || ""} onChange={(e) => set({ title: e.target.value })} placeholder="Section title" />
      </div>
      <div className="space-y-1.5">
        <Label>Content</Label>
        <Textarea value={content.content || ""} onChange={(e) => set({ content: e.target.value })} placeholder="Your content..." rows={6} />
      </div>
    </div>
  );
}
