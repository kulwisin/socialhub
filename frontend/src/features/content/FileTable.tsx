"use client";

import { Music2, Video, AlertCircle, CheckCircle2, Clock, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import type { ContentFile, ContentFileStatus } from "@/types";

interface FileTableProps {
  files: ContentFile[] | undefined;
  isLoading: boolean;
}

const STATUS_CONFIG: Record<
  ContentFileStatus,
  { label: string; variant: "default" | "secondary" | "destructive" | "outline"; icon: React.ElementType }
> = {
  pending:   { label: "Pending",   variant: "secondary",    icon: Clock },
  analyzing: { label: "Analyzing", variant: "outline",      icon: Loader2 },
  analyzed:  { label: "Analyzed",  variant: "default",      icon: CheckCircle2 },
  matched:   { label: "Matched",   variant: "default",      icon: CheckCircle2 },
  queued:    { label: "Queued",    variant: "outline",      icon: Clock },
  posted:    { label: "Posted",    variant: "default",      icon: CheckCircle2 },
  failed:    { label: "Failed",    variant: "destructive",  icon: AlertCircle },
};

function fmtSize(bytes: number | null) {
  if (bytes === null) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fmtDuration(sec: number | null) {
  if (sec === null) return "—";
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function FileTable({ files, isLoading }: FileTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} className="h-12 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (!files?.length) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-16 text-center">
        <Video className="mb-3 h-10 w-10 text-muted-foreground/40" />
        <p className="font-medium">No files found</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Select a folder and click Scan to discover content.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-muted/40">
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">File</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Type</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Size</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Duration</th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file, i) => {
            const cfg = STATUS_CONFIG[file.status] ?? STATUS_CONFIG.pending;
            const StatusIcon = cfg.icon;
            return (
              <tr
                key={file.id}
                className={`border-b border-border last:border-0 ${i % 2 === 0 ? "" : "bg-muted/20"}`}
              >
                <td className="max-w-xs truncate px-4 py-3 font-medium">
                  <div className="flex items-center gap-2">
                    {file.file_type === "video" ? (
                      <Video className="h-4 w-4 shrink-0 text-blue-500" />
                    ) : (
                      <Music2 className="h-4 w-4 shrink-0 text-purple-500" />
                    )}
                    <span className="truncate">{file.filename}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-muted-foreground capitalize">{file.file_type}</td>
                <td className="px-4 py-3 text-muted-foreground">{fmtSize(file.file_size_bytes)}</td>
                <td className="px-4 py-3 text-muted-foreground">{fmtDuration(file.duration_seconds)}</td>
                <td className="px-4 py-3">
                  <Badge variant={cfg.variant} className="gap-1 text-xs">
                    <StatusIcon className="h-3 w-3" />
                    {cfg.label}
                  </Badge>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
