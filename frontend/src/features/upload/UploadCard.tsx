"use client";

import { useState } from "react";
import { Film, ImageIcon, Trash2, Send, CheckCircle2, XCircle, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useDeleteUpload } from "@/hooks/useUploads";
import { uploadService } from "@/services/upload.service";
import type { Upload } from "@/types";
import { formatFileSize, formatRelativeTime } from "@/lib/utils";
import { PublishModal } from "./PublishModal";

const STATUS_CONFIG = {
  pending: { label: "Processing", icon: Clock, variant: "warning" as const },
  ready: { label: "Ready", icon: CheckCircle2, variant: "success" as const },
  failed: { label: "Failed", icon: XCircle, variant: "destructive" as const },
};

interface UploadCardProps {
  upload: Upload;
}

export function UploadCard({ upload }: UploadCardProps) {
  const deleteUpload = useDeleteUpload();
  const [publishOpen, setPublishOpen] = useState(false);

  const status = STATUS_CONFIG[upload.status];
  const StatusIcon = status.icon;
  const thumbnailUrl = uploadService.thumbnailUrl(upload.thumbnail_path);
  const isVideo = upload.media_type === "video";

  function handleDelete() {
    if (confirm(`Delete "${upload.original_filename}"?`)) {
      deleteUpload.mutate(upload.id);
    }
  }

  return (
    <>
      <Card className="overflow-hidden">
        {/* Thumbnail */}
        <div className="relative h-40 w-full bg-muted/50 flex items-center justify-center overflow-hidden">
          {thumbnailUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={thumbnailUrl}
              alt={upload.original_filename}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex flex-col items-center gap-2 text-muted-foreground">
              {isVideo ? (
                <Film className="h-10 w-10" />
              ) : (
                <ImageIcon className="h-10 w-10" />
              )}
              <span className="text-xs">{isVideo ? "Video" : "Image"}</span>
            </div>
          )}

          {/* Status overlay */}
          <div className="absolute bottom-2 left-2">
            <Badge variant={status.variant} className="gap-1 shadow-sm">
              <StatusIcon className="h-3 w-3" />
              {status.label}
            </Badge>
          </div>
        </div>

        <CardContent className="p-4">
          {/* Filename */}
          <p className="truncate font-medium text-sm" title={upload.original_filename}>
            {upload.original_filename}
          </p>

          {/* Meta */}
          <p className="mt-0.5 text-xs text-muted-foreground">
            {formatFileSize(upload.file_size_bytes)} · {formatRelativeTime(upload.created_at)}
          </p>

          {/* Caption preview */}
          {upload.caption && (
            <p className="mt-2 text-xs text-muted-foreground line-clamp-2">
              {upload.caption}
            </p>
          )}

          {upload.error_message && (
            <p className="mt-2 text-xs text-destructive line-clamp-2">
              {upload.error_message}
            </p>
          )}

          {/* Actions */}
          <div className="mt-4 flex items-center justify-between gap-2">
            <Button
              variant="ghost"
              size="sm"
              className="gap-1.5 text-muted-foreground hover:text-destructive"
              onClick={handleDelete}
              loading={deleteUpload.isPending}
            >
              <Trash2 className="h-3.5 w-3.5" />
              Delete
            </Button>

            <Button
              size="sm"
              className="gap-1.5"
              disabled={upload.status !== "ready"}
              onClick={() => setPublishOpen(true)}
            >
              <Send className="h-3.5 w-3.5" />
              Publish
            </Button>
          </div>
        </CardContent>
      </Card>

      <PublishModal
        upload={upload}
        open={publishOpen}
        onClose={() => setPublishOpen(false)}
      />
    </>
  );
}
