"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, Film, ImageIcon, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useUploadFile } from "@/hooks/useUploads";
import { formatFileSize } from "@/lib/utils";
import { cn } from "@/lib/utils";

const ACCEPTED = {
  "video/*": [".mp4", ".mov", ".avi", ".m4v", ".webm"],
  "image/*": [".jpg", ".jpeg", ".png", ".webp"],
};
const MAX_SIZE = 500 * 1024 * 1024; // 500 MB

export function UploadDropzone() {
  const [file, setFile] = useState<File | null>(null);
  const [caption, setCaption] = useState("");
  const [progress, setProgress] = useState(0);
  const uploadFile = useUploadFile();

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) {
      setFile(accepted[0]);
      setProgress(0);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxSize: MAX_SIZE,
    multiple: false,
  });

  async function handleUpload() {
    if (!file) return;
    setProgress(0);
    await uploadFile.mutateAsync({
      file,
      caption: caption.trim() || undefined,
      onProgress: setProgress,
    });
    setFile(null);
    setCaption("");
    setProgress(0);
  }

  const isVideo = file?.type.startsWith("video/");
  const isUploading = uploadFile.isPending;

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      {!file ? (
        <div
          {...getRootProps()}
          className={cn(
            "flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12 text-center transition-colors cursor-pointer",
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-border hover:border-primary/50 hover:bg-accent/50"
          )}
        >
          <input {...getInputProps()} />
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
            <Upload className="h-7 w-7 text-primary" />
          </div>
          <p className="text-base font-medium">
            {isDragActive ? "Drop it here…" : "Drag & drop your video or image"}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            MP4, MOV, JPG, PNG · up to 500 MB
          </p>
          <Button variant="outline" className="mt-5" size="sm">
            Browse files
          </Button>
          {fileRejections.length > 0 && (
            <p className="mt-3 text-xs text-destructive">
              {fileRejections[0]?.errors[0]?.message}
            </p>
          )}
        </div>
      ) : (
        /* File selected — show preview + caption */
        <div className="rounded-2xl border border-border bg-card p-5">
          {/* File info */}
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
              {isVideo ? (
                <Film className="h-6 w-6" />
              ) : (
                <ImageIcon className="h-6 w-6" />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium">{file.name}</p>
              <p className="text-sm text-muted-foreground">
                {formatFileSize(file.size)} · {file.type}
              </p>
            </div>
            <button
              onClick={() => { setFile(null); setProgress(0); }}
              className="shrink-0 rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Caption */}
          <div className="mt-5 space-y-1.5">
            <Label htmlFor="caption">Caption</Label>
            <Textarea
              id="caption"
              placeholder="Write a caption for this post…"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              rows={4}
              maxLength={2200}
            />
            <p className="text-right text-xs text-muted-foreground">
              {caption.length}/2200
            </p>
          </div>

          {/* Progress bar */}
          {isUploading && (
            <div className="mt-4">
              <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                <span>Uploading…</span>
                <span>{progress}%</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="mt-5 flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => { setFile(null); setCaption(""); setProgress(0); }}
              disabled={isUploading}
            >
              Cancel
            </Button>
            <Button onClick={handleUpload} loading={isUploading} disabled={isUploading}>
              Upload
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
