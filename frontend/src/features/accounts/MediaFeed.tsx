"use client";

import { ExternalLink, Film, Heart, MessageCircle, Grid3x3 } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useAccountMedia } from "@/hooks/useSocialAccounts";
import type { InstagramMediaItem, InstagramMediaType } from "@/types";
import { formatNumber } from "@/lib/utils";
import { cn } from "@/lib/utils";

const MEDIA_TYPE_LABEL: Record<InstagramMediaType, string> = {
  IMAGE: "Photo",
  VIDEO: "Video",
  CAROUSEL_ALBUM: "Album",
  REELS: "Reel",
};

function MediaThumbnail({ item }: { item: InstagramMediaItem }) {
  const thumbSrc = item.thumbnail_url ?? item.media_url;
  const isVideo = item.media_type === "VIDEO" || item.media_type === "REELS";

  return (
    <a
      href={item.permalink ?? "#"}
      target="_blank"
      rel="noopener noreferrer"
      className="group relative block aspect-square overflow-hidden rounded-xl bg-muted"
    >
      {thumbSrc ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={thumbSrc}
          alt={item.caption ?? item.media_type}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center">
          <Film className="h-8 w-8 text-muted-foreground/40" />
        </div>
      )}

      {/* Video indicator */}
      {isVideo && (
        <div className="absolute left-2 top-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-xs font-medium text-white backdrop-blur-sm">
          <Film className="h-3 w-3" />
          {MEDIA_TYPE_LABEL[item.media_type]}
        </div>
      )}

      {/* Hover overlay with stats */}
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black/50 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
        {(item.like_count != null || item.comments_count != null) && (
          <div className="flex items-center gap-4 text-white">
            {item.like_count != null && (
              <span className="flex items-center gap-1.5 text-sm font-semibold">
                <Heart className="h-4 w-4 fill-white" />
                {formatNumber(item.like_count)}
              </span>
            )}
            {item.comments_count != null && (
              <span className="flex items-center gap-1.5 text-sm font-semibold">
                <MessageCircle className="h-4 w-4 fill-white" />
                {formatNumber(item.comments_count)}
              </span>
            )}
          </div>
        )}
        <ExternalLink className="h-4 w-4 text-white/80" />
      </div>
    </a>
  );
}

interface MediaFeedProps {
  accountId: string;
  username: string;
}

export function MediaFeed({ accountId, username }: MediaFeedProps) {
  const { data, isLoading, isError } = useAccountMedia(accountId, 12);

  if (isLoading) {
    return (
      <div>
        <div className="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <Grid3x3 className="h-4 w-4" />
          Recent posts
        </div>
        <div className="grid grid-cols-3 gap-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="aspect-square w-full rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <p className="text-xs text-muted-foreground">
        Could not load media feed. The account may not be a Business or Creator account.
      </p>
    );
  }

  if (!data?.items.length) {
    return (
      <p className="text-xs text-muted-foreground">
        No posts found on @{username}&apos;s account.
      </p>
    );
  }

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <span className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <Grid3x3 className="h-4 w-4" />
          Recent posts
        </span>
        <span className="text-xs text-muted-foreground">
          {data.items.length} shown
        </span>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {data.items.map((item) => (
          <MediaThumbnail key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
}
