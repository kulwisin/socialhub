"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { PostStatusBadge } from "@/features/posts/PostStatusBadge";
import { usePosts } from "@/hooks/usePosts";
import { formatDate } from "@/lib/utils";
import type { PostStatus } from "@/types";

const STATUS_TABS: Array<{ label: string; value?: PostStatus }> = [
  { label: "All" },
  { label: "Published", value: "published" },
  { label: "Failed", value: "failed" },
  { label: "Queued", value: "queued" },
];

export default function PostsPage() {
  const [statusFilter, setStatusFilter] = useState<PostStatus | undefined>();
  const { data: posts, isLoading } = usePosts(50, statusFilter);

  return (
    <>
      <Header
        title="Publish History"
        description="All publishing jobs and their outcomes."
      />

      <div className="flex-1 space-y-6 p-8">
        {/* Filter tabs */}
        <div className="flex gap-1 rounded-xl border border-border bg-card p-1 w-fit">
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.label}
              onClick={() => setStatusFilter(tab.value)}
              className={`rounded-lg px-4 py-1.5 text-sm font-medium transition-colors ${
                statusFilter === tab.value
                  ? "bg-primary/15 text-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Table */}
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-16 w-full rounded-xl" />
            ))}
          </div>
        ) : !posts?.length ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-20 text-center">
            <Send className="mb-3 h-10 w-10 text-muted-foreground/40" />
            <p className="font-medium">No posts yet</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Posts will appear here after you publish from the Upload Studio.
            </p>
          </div>
        ) : (
          <Card>
            <CardContent className="p-0">
              <div className="divide-y divide-border">
                {posts.map((post) => (
                  <div
                    key={post.id}
                    className="flex flex-col gap-1 px-5 py-4 sm:flex-row sm:items-center sm:gap-4"
                  >
                    <div className="min-w-0 flex-1 space-y-0.5">
                      <p className="text-xs font-mono text-muted-foreground">
                        Upload {post.upload_id.slice(0, 8)}…
                      </p>
                      {post.platform_post_id && (
                        <p className="text-xs text-muted-foreground">
                          Platform ID: {post.platform_post_id}
                        </p>
                      )}
                      {post.error_message && (
                        <p className="text-xs text-destructive line-clamp-1">
                          {post.error_message}
                        </p>
                      )}
                      {post.caption && (
                        <p className="text-xs text-muted-foreground line-clamp-1">
                          {post.caption}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center gap-4 shrink-0">
                      <PostStatusBadge status={post.status} />
                      <p className="text-xs text-muted-foreground whitespace-nowrap">
                        {post.published_at
                          ? formatDate(post.published_at)
                          : formatDate(post.created_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
