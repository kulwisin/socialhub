'use client'

import Link from 'next/link'
import {
  Upload,
  Link2,
  Send,
  Globe,
  ArrowRight,
  Film,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useUploads } from '@/hooks/useUploads'
import { useAccounts } from '@/hooks/useAccounts'
import { usePosts } from '@/hooks/usePosts'
import { formatRelativeTime } from '@/lib/utils'

function StatCard({
  icon: Icon,
  label,
  value,
  loading,
  href,
}: {
  icon: React.ElementType
  label: string
  value: string | number
  loading?: boolean
  href: string
}) {
  return (
    <Link href={href}>
      <Card className="cursor-pointer transition-colors hover:bg-accent/50">
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
  )
}

function PostStatusBadge({ status }: { status: string }) {
  const variants: Record<string, 'default' | 'success' | 'destructive' | 'warning'> = {
    published: 'success',
    failed: 'destructive',
    publishing: 'warning',
    queued: 'default',
  }
  return <Badge variant={variants[status] ?? 'default'}>{status}</Badge>
}

export default function DashboardPage() {
  const { data: uploads, isLoading: loadingUploads } = useUploads(20)
  const { data: accounts, isLoading: loadingAccounts } = useAccounts()
  const { data: posts, isLoading: loadingPosts } = usePosts(20)

  const publishedCount = posts?.filter((p) => p.status === 'published').length ?? 0
  const activePlatforms = new Set(
    accounts?.filter((a) => a.is_active).map((a) => a.platform)
  ).size

  const recentPosts = posts?.slice(0, 5) ?? []
  const recentUploads = uploads?.slice(0, 4) ?? []

  return (
    <div className="flex-1 space-y-8 p-8">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Welcome back. Here&apos;s what&apos;s happening.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={Upload}
          label="Total Uploads"
          value={uploads?.length ?? 0}
          loading={loadingUploads}
          href="/library"
        />
        <StatCard
          icon={Link2}
          label="Connected Accounts"
          value={accounts?.length ?? 0}
          loading={loadingAccounts}
          href="/accounts"
        />
        <StatCard
          icon={Send}
          label="Published Posts"
          value={publishedCount}
          loading={loadingPosts}
          href="/library"
        />
        <StatCard
          icon={Globe}
          label="Active Platforms"
          value={activePlatforms}
          loading={loadingAccounts}
          href="/accounts"
        />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Recent Posts */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="text-base">Recent Posts</CardTitle>
            <Link href="/library">
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
            ) : !recentPosts.length ? (
              <div className="py-6 text-center">
                <p className="text-sm text-muted-foreground">No posts yet</p>
                <Link href="/create">
                  <Button variant="outline" size="sm" className="mt-3 gap-1.5">
                    <Send className="h-3.5 w-3.5" /> Create a post
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {recentPosts.map((p) => (
                  <div key={p.id} className="flex items-center gap-3 py-2.5">
                    <div className="min-w-0 flex-1">
                      <p className="text-xs text-muted-foreground">
                        {p.published_at
                          ? formatRelativeTime(p.published_at)
                          : formatRelativeTime(p.created_at)}
                      </p>
                      {p.error_message && (
                        <p className="truncate text-xs text-destructive">{p.error_message}</p>
                      )}
                    </div>
                    <PostStatusBadge status={p.status} />
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Uploads */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="text-base">Recent Uploads</CardTitle>
            <Link href="/library">
              <Button variant="ghost" size="sm" className="gap-1 text-muted-foreground">
                View all <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {loadingUploads ? (
              <div className="grid grid-cols-2 gap-3">
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton key={i} className="h-28 w-full rounded-lg" />
                ))}
              </div>
            ) : !recentUploads.length ? (
              <div className="py-6 text-center">
                <p className="text-sm text-muted-foreground">No uploads yet</p>
                <Link href="/create">
                  <Button variant="outline" size="sm" className="mt-3 gap-1.5">
                    <Upload className="h-3.5 w-3.5" /> Upload a file
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {recentUploads.map((u) => (
                  <div
                    key={u.id}
                    className="flex flex-col gap-1 rounded-lg border border-border bg-muted/30 p-3"
                  >
                    <div className="flex h-16 items-center justify-center rounded-md bg-muted">
                      <Film className="h-6 w-6 text-muted-foreground" />
                    </div>
                    <p className="truncate text-xs font-medium">
                      {u.title ?? u.original_filename}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatRelativeTime(u.created_at)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
