import { CheckCircle2, XCircle, Loader2, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { PostStatus } from "@/types";

const CONFIG: Record<
  PostStatus,
  { label: string; variant: "success" | "destructive" | "warning" | "secondary"; icon: React.ReactNode }
> = {
  published: {
    label: "Published",
    variant: "success",
    icon: <CheckCircle2 className="h-3 w-3" />,
  },
  failed: {
    label: "Failed",
    variant: "destructive",
    icon: <XCircle className="h-3 w-3" />,
  },
  publishing: {
    label: "Publishing…",
    variant: "warning",
    icon: <Loader2 className="h-3 w-3 animate-spin" />,
  },
  queued: {
    label: "Queued",
    variant: "secondary",
    icon: <Clock className="h-3 w-3" />,
  },
};

export function PostStatusBadge({ status }: { status: PostStatus }) {
  const { label, variant, icon } = CONFIG[status];
  return (
    <Badge variant={variant} className="gap-1">
      {icon}
      {label}
    </Badge>
  );
}
