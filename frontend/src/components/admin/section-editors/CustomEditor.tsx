"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type RenderMode = "text" | "markdown" | "html";

interface CustomContent {
  title?: string;
  content?: string;
  render_mode?: RenderMode;
}

interface Props {
  content: CustomContent;
  onChange: (content: CustomContent) => void;
}

const MODE_LABELS: Record<RenderMode, string> = {
  text: "Plain text",
  markdown: "Markdown (rich text)",
  html: "Raw HTML / embed",
};

const MODE_HINTS: Record<RenderMode, string> = {
  text: "Paragraphs separated by newlines.",
  markdown: "Supports # headings, **bold**, - lists, [links](url), `code`.",
  html: "Raw HTML — use for embeds (maps, videos, widgets). Script tags are not executed.",
};

export function CustomEditor({ content, onChange }: Props) {
  const set = (patch: Partial<CustomContent>) => onChange({ ...content, ...patch });
  const mode = content.render_mode ?? "text";

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label>Render mode</Label>
        <Select value={mode} onValueChange={(v) => set({ render_mode: v as RenderMode })}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {(["text", "markdown", "html"] as RenderMode[]).map((m) => (
              <SelectItem key={m} value={m}>{MODE_LABELS[m]}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-xs text-muted-foreground">{MODE_HINTS[mode]}</p>
      </div>
      <div className="space-y-1.5">
        <Label>Title</Label>
        <Input value={content.title || ""} onChange={(e) => set({ title: e.target.value })} placeholder="Section title" />
      </div>
      <div className="space-y-1.5">
        <Label>Content</Label>
        <Textarea
          value={content.content || ""}
          onChange={(e) => set({ content: e.target.value })}
          placeholder={mode === "html" ? "<iframe ...></iframe>" : mode === "markdown" ? "# Heading\n\nParagraph with **bold** and [links](https://...)" : "Your content..."}
          rows={10}
          className={mode === "html" ? "font-mono text-xs" : ""}
        />
      </div>
    </div>
  );
}
