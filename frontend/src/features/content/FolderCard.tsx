"use client";

import { useState } from "react";
import { Folder, RefreshCw, Trash2, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useDeleteFolder, useScanFolder } from "@/hooks/useContent";
import type { ContentFolder } from "@/types";

interface FolderCardProps {
  folder: ContentFolder;
  onSelect: (id: string) => void;
  isSelected: boolean;
}

function fmtDate(iso: string | null) {
  if (!iso) return "never";
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function FolderCard({ folder, onSelect, isSelected }: FolderCardProps) {
  const deleteFolder = useDeleteFolder();
  const scanFolder = useScanFolder();

  return (
    <Card
      className={`cursor-pointer transition-colors ${
        isSelected ? "border-primary ring-1 ring-primary/30" : "hover:border-muted-foreground/30"
      }`}
      onClick={() => onSelect(folder.id)}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex min-w-0 items-center gap-2">
            <Folder className="h-4 w-4 shrink-0 text-primary" />
            <CardTitle className="truncate text-sm">{folder.label}</CardTitle>
          </div>
          <Badge variant={folder.is_active ? "default" : "secondary"} className="shrink-0 text-xs">
            {folder.is_active ? "active" : "paused"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="truncate font-mono text-xs text-muted-foreground">{folder.path}</p>

        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          <span>Scanned {fmtDate(folder.last_scanned_at)}</span>
        </div>

        <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
          <Button
            size="sm"
            variant="outline"
            className="flex-1 text-xs"
            disabled={scanFolder.isPending}
            onClick={() => scanFolder.mutate(folder.id)}
          >
            <RefreshCw
              className={`mr-1.5 h-3 w-3 ${scanFolder.isPending ? "animate-spin" : ""}`}
            />
            Scan
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="text-destructive hover:text-destructive"
            disabled={deleteFolder.isPending}
            onClick={() => deleteFolder.mutate(folder.id)}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
