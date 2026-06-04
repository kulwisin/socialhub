import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

export function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return formatDate(iso);
}

export function formatFileSize(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export function platformColor(platform: string): string {
  switch (platform) {
    case "instagram":
      return "from-pink-500 via-red-500 to-yellow-400";
    case "facebook":
      return "from-blue-600 to-blue-500";
    case "tiktok":
      return "from-gray-900 to-gray-700";
    default:
      return "from-gray-600 to-gray-500";
  }
}

export function eventTypeLabel(eventType: string): string {
  const labels: Record<string, string> = {
    "device.created": "Device created",
    "device.updated": "Device updated",
    "device.deleted": "Device deleted",
    "account.connected": "Account connected",
    "account.disconnected": "Account disconnected",
    "account.synced": "Account synced",
    "upload.created": "File uploaded",
    "upload.deleted": "Upload deleted",
    "post.published": "Post published",
    "post.failed": "Post failed",
  };
  return labels[eventType] ?? eventType;
}
