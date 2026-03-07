"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Upload, X, Image as ImageIcon, FileText, Check, Link } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";

export interface MediaFile {
  id: string;
  original_filename: string;
  storage_key: string;
  url: string;
  mime_type: string;
  file_type: "image" | "document";
  size_bytes: number;
  alt_text: string | null;
  width: number | null;
  height: number | null;
  created_at: string;
}

interface Props {
  siteId: string;
  open: boolean;
  onClose: () => void;
  onSelect: (file: MediaFile) => void;
  /** Only show images, documents, or all (default: "image") */
  filter?: "image" | "document" | "all";
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function MediaLibrary({ siteId, open, onClose, onSelect, filter = "image" }: Props) {
  const [files, setFiles] = useState<MediaFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"library" | "url">("library");
  const [urlInput, setUrlInput] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchFiles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<MediaFile[]>(`/sites/${siteId}/media`);
      const filtered =
        filter === "all" ? res.data : res.data.filter((f) => f.file_type === filter);
      setFiles(filtered);
    } catch {
      setError("Failed to load media files.");
    } finally {
      setLoading(false);
    }
  }, [siteId, filter]);

  useEffect(() => {
    if (open) {
      fetchFiles();
      setSelected(null);
      setTab("library");
      setUrlInput("");
    }
  }, [open, fetchFiles]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      await api.post(`/sites/${siteId}/media/upload`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await fetchFiles();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Upload failed.";
      setError(msg);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (file: MediaFile, ev: React.MouseEvent) => {
    ev.stopPropagation();
    if (!confirm(`Delete "${file.original_filename}"?`)) return;
    try {
      await api.delete(`/sites/${siteId}/media/${file.id}`);
      setFiles((prev) => prev.filter((f) => f.id !== file.id));
      if (selected === file.id) setSelected(null);
    } catch {
      setError("Failed to delete file.");
    }
  };

  const handleConfirm = () => {
    const file = files.find((f) => f.id === selected);
    if (file) {
      onSelect(file);
      onClose();
    }
  };

  const accept =
    filter === "image"
      ? "image/jpeg,image/png,image/gif,image/webp,image/svg+xml"
      : filter === "document"
        ? "application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        : "image/*,application/pdf,application/msword,.docx";

  const handleUrlConfirm = () => {
    const url = urlInput.trim();
    if (!url) return;
    onSelect({ id: "", original_filename: url, storage_key: "", url, mime_type: "image/*", file_type: "image", size_bytes: 0, alt_text: null, width: null, height: null, created_at: "" });
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Media Library</DialogTitle>
        </DialogHeader>

        {/* Tabs */}
        <div className="flex gap-1 border-b shrink-0 -mx-1 px-1">
          <button
            onClick={() => setTab("library")}
            className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${tab === "library" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"}`}
          >
            <ImageIcon size={13} className="inline mr-1.5 -mt-0.5" />
            Uploaded files
          </button>
          {filter === "image" && (
            <button
              onClick={() => setTab("url")}
              className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${tab === "url" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"}`}
            >
              <Link size={13} className="inline mr-1.5 -mt-0.5" />
              Paste URL
            </button>
          )}
        </div>

        {tab === "url" ? (
          <div className="flex-1 flex flex-col justify-center gap-4 px-2 py-6">
            <p className="text-sm text-muted-foreground">Paste any image URL (Unsplash, CDN, etc.)</p>
            <Input
              placeholder="https://images.unsplash.com/..."
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleUrlConfirm()}
              autoFocus
            />
            {urlInput.trim() && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={urlInput.trim()} alt="preview" className="max-h-40 object-contain rounded border bg-muted" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
            )}
          </div>
        ) : (
          <>
        {/* Toolbar */}
        <div className="flex items-center gap-3 pb-3 border-b shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            <Upload size={14} className="mr-1.5" />
            {uploading ? "Uploading…" : "Upload file"}
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept={accept}
            className="hidden"
            onChange={handleUpload}
          />
          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        {/* Grid */}
        <div className="flex-1 overflow-y-auto min-h-0">
          {loading ? (
            <div className="flex items-center justify-center h-40 text-muted-foreground text-sm">
              Loading…
            </div>
          ) : files.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 text-muted-foreground text-sm gap-2">
              <ImageIcon size={32} className="opacity-30" />
              <p>No files yet. Upload one to get started.</p>
            </div>
          ) : (
            <div className="grid grid-cols-4 gap-3 p-1">
              {files.map((file) => (
                <div
                  key={file.id}
                  onClick={() => setSelected(file.id === selected ? null : file.id)}
                  className={`relative group cursor-pointer rounded-lg border-2 overflow-hidden transition-all ${
                    selected === file.id
                      ? "border-primary ring-2 ring-primary/30"
                      : "border-transparent hover:border-muted-foreground/30"
                  }`}
                >
                  {file.file_type === "image" ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={file.url}
                      alt={file.alt_text ?? file.original_filename}
                      className="w-full aspect-square object-cover bg-muted"
                    />
                  ) : (
                    <div className="w-full aspect-square bg-muted flex flex-col items-center justify-center gap-1">
                      <FileText size={32} className="text-muted-foreground" />
                      <span className="text-xs text-muted-foreground text-center px-1 truncate w-full">
                        {file.original_filename}
                      </span>
                    </div>
                  )}

                  {/* Selected overlay */}
                  {selected === file.id && (
                    <div className="absolute inset-0 bg-primary/10 flex items-start justify-end p-1">
                      <div className="bg-primary text-primary-foreground rounded-full p-0.5">
                        <Check size={12} />
                      </div>
                    </div>
                  )}

                  {/* Delete button */}
                  <button
                    onClick={(ev) => handleDelete(file, ev)}
                    className="absolute top-1 left-1 bg-destructive text-destructive-foreground rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X size={10} />
                  </button>

                  {/* Filename + size */}
                  <div className="p-1.5 text-xs truncate text-muted-foreground">
                    <p className="truncate font-medium text-foreground">{file.original_filename}</p>
                    <p>{formatBytes(file.size_bytes)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

          </>
        )}

        {/* Footer */}
        <div className="flex justify-end gap-2 pt-3 border-t shrink-0">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          {tab === "url" ? (
            <Button onClick={handleUrlConfirm} disabled={!urlInput.trim()}>
              <Check size={14} className="mr-1.5" />
              Use URL
            </Button>
          ) : (
            <Button onClick={handleConfirm} disabled={!selected}>
              <Check size={14} className="mr-1.5" />
              Use selected
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

