"use client";

import { useState } from "react";
import { Image as ImageIcon, X } from "lucide-react";
import { Button } from "@/components/ui/button";
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

  const handleSelect = (file: MediaFile) => {
    onChange(file.url);
  };

  return (
    <div className="space-y-1.5">
      <p className="text-sm font-medium">{label}</p>
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
      ) : (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="w-full h-24 border-2 border-dashed rounded-md flex flex-col items-center justify-center gap-1 text-muted-foreground hover:border-primary/50 hover:text-primary transition-colors"
        >
          <ImageIcon size={20} />
          <span className="text-xs">Click to select image</span>
        </button>
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
