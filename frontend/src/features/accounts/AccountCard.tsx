"use client";

import Image from "next/image";
import { RefreshCw, Unlink, Instagram, Facebook, Music2, Users, Image as ImageIcon, KeyRound } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useDisconnectAccount, useRefreshToken, useSyncAccount } from "@/hooks/useSocialAccounts";
import type { SocialAccount, Platform } from "@/types";
import { formatNumber, formatRelativeTime } from "@/lib/utils";
import { MediaFeed } from "./MediaFeed";

const PLATFORM_ICON: Record<Platform, React.ReactNode> = {
  instagram: <Instagram className="h-4 w-4" />,
  facebook: <Facebook className="h-4 w-4" />,
  tiktok: <Music2 className="h-4 w-4" />,
};

const PLATFORM_GRADIENT: Record<Platform, string> = {
  instagram: "from-pink-500 via-red-500 to-yellow-400",
  facebook: "from-blue-600 to-blue-500",
  tiktok: "from-gray-700 to-gray-600",
};

const PLATFORM_BADGE: Record<Platform, "instagram" | "facebook" | "tiktok"> = {
  instagram: "instagram",
  facebook: "facebook",
  tiktok: "tiktok",
};

interface AccountCardProps {
  account: SocialAccount;
  deviceId: string;
}

export function AccountCard({ account, deviceId }: AccountCardProps) {
  const disconnect = useDisconnectAccount(deviceId);
  const sync = useSyncAccount(deviceId);
  const refreshToken = useRefreshToken();

  function handleDisconnect() {
    if (confirm(`Disconnect @${account.username} from ${account.platform}?`)) {
      disconnect.mutate(account.id);
    }
  }

  const platform = account.platform as Platform;

  return (
    <Card className="overflow-hidden">
      {/* Gradient header bar */}
      <div className={`h-1.5 w-full bg-gradient-to-r ${PLATFORM_GRADIENT[platform]}`} />

      <CardContent className="p-5">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="relative shrink-0">
            {account.profile_image_url ? (
              <Image
                src={account.profile_image_url}
                alt={account.username}
                width={52}
                height={52}
                className="rounded-full object-cover ring-2 ring-border"
                unoptimized
              />
            ) : (
              <div
                className={`flex h-13 w-13 items-center justify-center rounded-full bg-gradient-to-br ${PLATFORM_GRADIENT[platform]} text-white`}
              >
                {PLATFORM_ICON[platform]}
              </div>
            )}
            {/* Platform badge overlay */}
            <div
              className={`absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-br ${PLATFORM_GRADIENT[platform]} text-white ring-2 ring-card`}
            >
              <span className="text-[9px]">{PLATFORM_ICON[platform]}</span>
            </div>
          </div>

          {/* Info */}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <p className="truncate font-semibold">@{account.username}</p>
              <Badge variant={PLATFORM_BADGE[platform]} className="shrink-0 capitalize">
                {account.platform}
              </Badge>
            </div>

            {account.display_name && (
              <p className="mt-0.5 text-sm text-muted-foreground truncate">
                {account.display_name}
              </p>
            )}

            {/* Stats row */}
            <div className="mt-3 flex flex-wrap items-center gap-4 text-sm">
              <span className="flex items-center gap-1 text-muted-foreground">
                <Users className="h-3.5 w-3.5" />
                <span className="font-medium text-foreground">
                  {formatNumber(account.followers_count)}
                </span>{" "}
                followers
              </span>
              <span className="flex items-center gap-1 text-muted-foreground">
                <ImageIcon className="h-3.5 w-3.5" />
                <span className="font-medium text-foreground">
                  {formatNumber(account.media_count)}
                </span>{" "}
                posts
              </span>
            </div>

            {account.biography && (
              <p className="mt-2 text-xs text-muted-foreground line-clamp-2">
                {account.biography}
              </p>
            )}

            {account.last_synced_at && (
              <p className="mt-2 text-xs text-muted-foreground">
                Synced {formatRelativeTime(account.last_synced_at)}
              </p>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="mt-4 flex items-center justify-end gap-2 border-t border-border pt-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => sync.mutate(account.id)}
            loading={sync.isPending}
            className="gap-1.5 text-muted-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Sync
          </Button>
          {platform === "instagram" && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => refreshToken.mutate(account.id)}
              loading={refreshToken.isPending}
              className="gap-1.5 text-muted-foreground"
              title="Extend the Instagram token for another 60 days"
            >
              <KeyRound className="h-3.5 w-3.5" />
              Refresh token
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDisconnect}
            loading={disconnect.isPending}
            className="gap-1.5 text-muted-foreground hover:text-destructive"
          >
            <Unlink className="h-3.5 w-3.5" />
            Disconnect
          </Button>
        </div>

        {/* Instagram media feed */}
        {platform === "instagram" && (
          <div className="mt-5 border-t border-border pt-5">
            <MediaFeed accountId={account.id} username={account.username} />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
