"use client";

import {
  Smartphone,
  Link2,
  Link2Off,
  Upload,
  Send,
  XCircle,
  RefreshCw,
  Trash2,
  Activity,
} from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useActivity } from "@/hooks/useActivity";
import { formatRelativeTime, eventTypeLabel } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { ActivityLog } from "@/types";

const EVENT_ICON: Record<string, React.ReactNode> = {
  "device.created": <Smartphone className="h-3.5 w-3.5" />,
  "device.updated": <Smartphone className="h-3.5 w-3.5" />,
  "device.deleted": <Trash2 className="h-3.5 w-3.5" />,
  "account.connected": <Link2 className="h-3.5 w-3.5" />,
  "account.disconnected": <Link2Off className="h-3.5 w-3.5" />,
  "account.synced": <RefreshCw className="h-3.5 w-3.5" />,
  "upload.created": <Upload className="h-3.5 w-3.5" />,
  "upload.deleted": <Trash2 className="h-3.5 w-3.5" />,
  "post.published": <Send className="h-3.5 w-3.5" />,
  "post.failed": <XCircle className="h-3.5 w-3.5" />,
};

const EVENT_COLOR: Record<string, string> = {
  "post.published": "bg-emerald-500/15 text-emerald-400",
  "post.failed": "bg-red-500/15 text-red-400",
  "account.connected": "bg-primary/15 text-primary",
  "account.disconnected": "bg-amber-500/15 text-amber-400",
  "device.deleted": "bg-red-500/15 text-red-400",
  "upload.deleted": "bg-red-500/15 text-red-400",
};

function ActivityItem({ log }: { log: ActivityLog }) {
  const icon = EVENT_ICON[log.event_type] ?? <Activity className="h-3.5 w-3.5" />;
  const colorClass =
    EVENT_COLOR[log.event_type] ?? "bg-muted text-muted-foreground";

  return (
    <div className="flex items-start gap-3 py-3">
      {/* Icon dot */}
      <div
        className={cn(
          "mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full",
          colorClass
        )}
      >
        {icon}
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium">{eventTypeLabel(log.event_type)}</p>
        {log.description && (
          <p className="mt-0.5 text-xs text-muted-foreground leading-relaxed">
            {log.description}
          </p>
        )}
      </div>

      {/* Time */}
      <span className="shrink-0 text-xs text-muted-foreground">
        {formatRelativeTime(log.created_at)}
      </span>
    </div>
  );
}

interface ActivityFeedProps {
  limit?: number;
}

export function ActivityFeed({ limit = 50 }: ActivityFeedProps) {
  const { data: logs, isLoading, isError } = useActivity(limit);

  if (isLoading) {
    return (
      <div className="divide-y divide-border">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-start gap-3 py-3">
            <Skeleton className="h-6 w-6 shrink-0 rounded-full" />
            <div className="flex-1 space-y-1.5">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-3 w-64" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <p className="py-8 text-center text-sm text-destructive">
        Failed to load activity log.
      </p>
    );
  }

  if (!logs?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Activity className="mb-3 h-10 w-10 text-muted-foreground/40" />
        <p className="font-medium">No activity yet</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Events will appear here as you create devices, connect accounts, and publish content.
        </p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-border">
      {logs.map((log) => (
        <ActivityItem key={log.id} log={log} />
      ))}
    </div>
  );
}
