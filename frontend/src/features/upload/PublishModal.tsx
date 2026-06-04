"use client";

import { useState } from "react";
import { Instagram, Facebook, Music2, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { Dialog, DialogHeader } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useDevices } from "@/hooks/useDevices";
import { usePublish } from "@/hooks/usePosts";
import type { Upload, SocialAccountSummary, Platform, PublishResponse } from "@/types";
import { cn, formatNumber } from "@/lib/utils";

const PLATFORM_ICON: Record<Platform, React.ReactNode> = {
  instagram: <Instagram className="h-4 w-4" />,
  facebook: <Facebook className="h-4 w-4" />,
  tiktok: <Music2 className="h-4 w-4" />,
};

const PLATFORM_BADGE: Record<Platform, "instagram" | "facebook" | "tiktok"> = {
  instagram: "instagram",
  facebook: "facebook",
  tiktok: "tiktok",
};

interface PublishModalProps {
  upload: Upload;
  open: boolean;
  onClose: () => void;
}

export function PublishModal({ upload, open, onClose }: PublishModalProps) {
  const { data: devices, isLoading } = useDevices();
  const publish = usePublish();
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<PublishResponse | null>(null);

  // Flatten all active accounts across all devices
  const allAccounts: Array<SocialAccountSummary & { deviceName: string }> =
    (devices ?? []).flatMap((device) =>
      device.social_accounts
        .filter((a) => a.is_active)
        .map((a) => ({ ...a, deviceName: device.name }))
    );

  function toggle(accountId: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(accountId)) next.delete(accountId);
      else next.add(accountId);
      return next;
    });
  }

  async function handlePublish() {
    const res = await publish.mutateAsync({
      upload_id: upload.id,
      account_ids: Array.from(selected),
      caption: upload.caption ?? undefined,
    });
    setResult(res);
  }

  function handleClose() {
    setSelected(new Set());
    setResult(null);
    onClose();
  }

  const isPending = publish.isPending;

  return (
    <Dialog open={open} onClose={handleClose} className="max-w-xl">
      <DialogHeader
        title="Publish to accounts"
        description={`"${upload.original_filename}" will be posted to each selected account.`}
        onClose={handleClose}
      />

      {/* Result view */}
      {result ? (
        <div className="space-y-3">
          <div className="flex gap-4 text-center">
            <div className="flex-1 rounded-xl bg-emerald-500/10 p-4">
              <p className="text-2xl font-bold text-emerald-400">{result.succeeded}</p>
              <p className="text-sm text-muted-foreground">Published</p>
            </div>
            <div className="flex-1 rounded-xl bg-red-500/10 p-4">
              <p className="text-2xl font-bold text-red-400">{result.failed}</p>
              <p className="text-sm text-muted-foreground">Failed</p>
            </div>
          </div>

          <div className="space-y-2">
            {result.posts.map((post) => {
              const account = allAccounts.find((a) => a.id === post.social_account_id);
              return (
                <div
                  key={post.id}
                  className="flex items-center gap-3 rounded-lg border border-border p-3"
                >
                  {post.status === "published" ? (
                    <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
                  ) : (
                    <XCircle className="h-4 w-4 shrink-0 text-red-400" />
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">
                      @{account?.username ?? post.social_account_id}
                    </p>
                    {post.error_message && (
                      <p className="text-xs text-destructive truncate">
                        {post.error_message}
                      </p>
                    )}
                    {post.platform_post_id && (
                      <p className="text-xs text-muted-foreground">
                        ID: {post.platform_post_id}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <Button className="w-full mt-2" onClick={handleClose}>
            Done
          </Button>
        </div>
      ) : (
        /* Account picker */
        <>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : allAccounts.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border p-8 text-center">
              <p className="text-sm text-muted-foreground">
                No connected accounts found. Go to a device and connect Instagram or Facebook first.
              </p>
            </div>
          ) : (
            <div className="max-h-80 space-y-2 overflow-y-auto pr-1">
              {allAccounts.map((account) => {
                const isSelected = selected.has(account.id);
                const platform = account.platform as Platform;

                return (
                  <button
                    key={account.id}
                    onClick={() => toggle(account.id)}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-xl border p-3.5 text-left transition-all",
                      isSelected
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-primary/40 hover:bg-accent/50"
                    )}
                  >
                    {/* Checkbox */}
                    <div
                      className={cn(
                        "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors",
                        isSelected
                          ? "border-primary bg-primary"
                          : "border-muted-foreground/40"
                      )}
                    >
                      {isSelected && (
                        <svg
                          className="h-3 w-3 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          strokeWidth={3}
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>

                    {/* Account info */}
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant={PLATFORM_BADGE[platform]} className="gap-1 shrink-0">
                          {PLATFORM_ICON[platform]}
                          {account.platform}
                        </Badge>
                        <span className="truncate font-medium text-sm">
                          @{account.username}
                        </span>
                      </div>
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        {account.deviceName}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          <div className="flex items-center justify-between gap-3 pt-4 border-t border-border mt-4">
            <p className="text-sm text-muted-foreground">
              {selected.size} account{selected.size !== 1 ? "s" : ""} selected
            </p>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleClose} disabled={isPending}>
                Cancel
              </Button>
              <Button
                onClick={handlePublish}
                disabled={selected.size === 0 || isPending}
                loading={isPending}
              >
                {isPending ? "Publishing…" : `Post to ${selected.size || "…"}`}
              </Button>
            </div>
          </div>
        </>
      )}
    </Dialog>
  );
}
