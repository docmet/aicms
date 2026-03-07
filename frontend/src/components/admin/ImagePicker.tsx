"use client";

import { useState } from "react";
import { Image as ImageIcon, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MediaLibrary, type MediaFile } from "./MediaLibrary";

interface Props {
  siteId: string;
  value: string | null | undefined;
  onChange: (url: string | null) => void;
  label?: string;
  /** Hint shown below the picker */
  hint?: string;
}

export function ImagePicker({ siteId, value, onChange, label = "Image", hint }: Props) {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<"library" | "url">("library");
  const [urlInput, setUrlInput] = useState("");
  const [urlError, setUrlError] = useState<string | null>(null);

  const handleSelect = (file: MediaFile) => {
    onChange(file.url);
  };

  const validateAndApplyUrl = (raw: string) => {
    const trimmed = raw.trim();
    if (!trimmed) {
      setUrlError(null);
      onChange(null);
      return;
    }
    try {
      new URL(trimmed);
      setUrlError(null);
      onChange(trimmed);
    } catch {
      setUrlError("Enter a valid URL — e.g. https://example.com/image.jpg");
    }
  };

  const handleUrlKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      validateAndApplyUrl(urlInput);
    }
  };

  const handleUrlBlur = () => {
    validateAndApplyUrl(urlInput);
  };

  return (
    <div className="space-y-1.5">
      <p className="text-sm font-medium">{label}</p>

      {/* Mode toggle — shown when no value is set */}
      {!value && (
        <div className="flex gap-1">
          <Button
            type="button"
            size="sm"
            variant={mode === "library" ? "default" : "outline"}
            onClick={() => {
              setMode("library");
              setUrlError(null);
            }}
          >
            Library
          </Button>
          <Button
            type="button"
            size="sm"
            variant={mode === "url" ? "default" : "outline"}
            onClick={() => setMode("url")}
          >
            Paste URL
          </Button>
        </div>
      )}

      {value ? (
        <div className="relative group w-full">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={value}
            alt=""
            className="w-full max-h-40 object-cover rounded-md border bg-muted"
          />
          <div className="absolute inset-0 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/40 rounded-md">
            <Button
              type="button"
              size="sm"
              variant="secondary"
              onClick={() => setOpen(true)}
            >
              Change
            </Button>
            <Button
              type="button"
              size="sm"
              variant="destructive"
              onClick={() => onChange(null)}
            >
              <X size={14} />
            </Button>
          </div>
        </div>
      ) : mode === "library" ? (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="w-full h-24 border-2 border-dashed rounded-md flex flex-col items-center justify-center gap-1 text-muted-foreground hover:border-primary/50 hover:text-primary transition-colors"
        >
          <ImageIcon size={20} />
          <span className="text-xs">Click to select image</span>
        </button>
      ) : (
        <div className="space-y-1">
          <Input
            value={urlInput}
            onChange={(e) => {
              setUrlInput(e.target.value);
              setUrlError(null);
            }}
            onBlur={handleUrlBlur}
            onKeyDown={handleUrlKeyDown}
            placeholder="https://example.com/image.jpg"
            className={urlError ? "border-destructive focus-visible:ring-destructive" : ""}
          />
          {urlError && (
            <p className="text-xs text-destructive">{urlError}</p>
          )}
        </div>
      )}

      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}

      <MediaLibrary
        siteId={siteId}
        open={open}
        onClose={() => setOpen(false)}
        onSelect={handleSelect}
        filter="image"
      />
    </div>
  );
}
