"use client";

import Link from "next/link";
import {
  Smartphone,
  Upload,
  Send,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Plus,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Header } from "@/components/layout/Header";
import { ActivityFeed } from "@/features/activity/ActivityFeed";
import { useDevices } from "@/hooks/useDevices";
import { useUploads } from "@/hooks/useUploads";
import { usePosts } from "@/hooks/usePosts";
import { PostStatusBadge } from "@/features/posts/PostStatusBadge";
import { formatRelativeTime } from "@/lib/utils";

function StatCard({
  icon: Icon,
  label,
  value,
  loading,
  href,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  loading?: boolean;
  href: string;
}) {
  return (
    <Link href={href}>
      <Card className="card-hover cursor-pointer">
        <CardContent className="flex items-center gap-4 p-5">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/10">
            <Icon className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">{label}</p>
            {loading ? (
              <Skeleton className="mt-1 h-7 w-12" />
            ) : (
              <p className="text-2xl font-bold">{value}</p>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

export default function OverviewPage() {
  const { data: devices, isLoading: loadingDevices } = useDevices();
  const { data: uploads, isLoading: loadingUploads } = useUploads(5);
  const { data: posts, isLoading: loadingPosts } = usePosts(5);

  const totalAccounts =
    devices?.reduce((sum, d) => sum + d.social_accounts.length, 0) ?? 0;
  const publishedToday =
    posts?.filter(
      (p) =>
        p.status === "published" &&
        p.published_at &&
        new Date(p.published_at).toDateString() === new Date().toDateString()
    ).length ?? 0;

  return (
    <>
      <Header
        title="Overview"
        description="Welcome back. Here's what's happening."
      />

      <div className="flex-1 space-y-8 p-8">
        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={Smartphone}
            label="Devices"
            value={devices?.length ?? 0}
            loading={loadingDevices}
            href="/devices"
          />
          <StatCard
            icon={CheckCircle2}
            label="Accounts connected"
            value={totalAccounts}
            loading={loadingDevices}
            href="/devices"
          />
          <StatCard
            icon={Upload}
            label="Ready to publish"
            value={uploads?.filter((u) => u.status === "ready").length ?? 0}
            loading={loadingUploads}
            href="/upload"
          />
          <StatCard
            icon={Send}
            label="Published today"
            value={publishedToday}
            loading={loadingPosts}
            href="/posts"
          />
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Recent uploads */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle className="text-base">Recent Uploads</CardTitle>
              <Link href="/upload">
                <Button variant="ghost" size="sm" className="gap-1 text-muted-foreground">
                  View all <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {loadingUploads ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : !uploads?.length ? (
                <div className="py-6 text-center">
                  <p className="text-sm text-muted-foreground">No uploads yet</p>
                  <Link href="/upload">
                    <Button variant="outline" size="sm" className="mt-3 gap-1.5">
                      <Plus className="h-3.5 w-3.5" /> Upload a file
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {uploads.map((u) => (
                    <div key={u.id} className="flex items-center gap-3 py-2.5">
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium">
                          {u.original_filename}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatRelativeTime(u.created_at)}
                        </p>
                      </div>
                      <Badge
                        variant={
                          u.status === "ready"
                            ? "success"
                            : u.status === "failed"
                            ? "destructive"
                            : "warning"
                        }
                      >
                        {u.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent posts */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle className="text-base">Recent Posts</CardTitle>
              <Link href="/posts">
                <Button variant="ghost" size="sm" className="gap-1 text-muted-foreground">
                  View all <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {loadingPosts ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : !posts?.length ? (
                <div className="py-6 text-center">
                  <p className="text-sm text-muted-foreground">No posts yet</p>
                  <Link href="/upload">
                    <Button variant="outline" size="sm" className="mt-3 gap-1.5">
                      <Send className="h-3.5 w-3.5" /> Start publishing
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {posts.map((p) => (
                    <div key={p.id} className="flex items-center gap-3 py-2.5">
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-muted-foreground">
                          {p.published_at
                            ? formatRelativeTime(p.published_at)
                            : formatRelativeTime(p.created_at)}
                        </p>
                        {p.error_message && (
                          <p className="truncate text-xs text-destructive">
                            {p.error_message}
                          </p>
                        )}
                      </div>
                      <PostStatusBadge status={p.status} />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Activity */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="text-base">Activity Log</CardTitle>
            <Link href="/activity">
              <Button variant="ghost" size="sm" className="gap-1 text-muted-foreground">
                View all <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <ActivityFeed limit={8} />
          </CardContent>
        </Card>
      </div>
    </>
  );
}
