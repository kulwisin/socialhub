'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Film, Search, Trash2, RefreshCw } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useUploads, useSearchUploads, useDeleteUpload } from '@/hooks/useUploads'
import { formatRelativeTime } from '@/lib/utils'
import type { Upload } from '@/types'

function UploadCard({ upload, onDelete }: { upload: Upload; onDelete: (id: string) => void }) {
  const displayHashtags = upload.hashtags?.slice(0, 3) ?? []
  const extraCount = (upload.hashtags?.length ?? 0) - 3

  return (
    <Card className="overflow-hidden">
      <div className="flex h-36 items-center justify-center bg-muted">
        <Film className="h-10 w-10 text-muted-foreground" />
      </div>
      <CardContent className="p-4 space-y-2">
        <p className="font-medium line-clamp-1">
          {upload.title ?? upload.original_filename}
        </p>
        {upload.description && (
          <p className="text-sm text-muted-foreground line-clamp-2">{upload.description}</p>
        )}
        {displayHashtags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {displayHashtags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"
              >
                #{tag}
              </span>
            ))}
            {extraCount > 0 && (
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                +{extraCount} more
              </span>
            )}
          </div>
        )}
        <div className="flex items-center justify-between pt-1">
          <p className="text-xs text-muted-foreground">
            {formatRelativeTime(upload.created_at)}
          </p>
          <Badge
            variant={
              upload.status === 'ready'
                ? 'success'
                : upload.status === 'failed'
                ? 'destructive'
                : 'warning'
            }
          >
            {upload.status}
          </Badge>
        </div>
        <div className="flex gap-2 pt-1">
          <Link href={`/create?upload_id=${upload.id}`} className="flex-1">
            <Button variant="outline" size="sm" className="w-full gap-1.5">
              <RefreshCw className="h-3.5 w-3.5" />
              Reuse
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(upload.id)}
            className="gap-1.5 text-destructive hover:bg-destructive/10 hover:text-destructive"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default function LibraryPage() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const deleteUpload = useDeleteUpload()

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300)
    return () => clearTimeout(timer)
  }, [query])

  const isSearching = debouncedQuery.length > 1
  const { data: allUploads, isLoading: loadingAll } = useUploads(50)
  const { data: searchResults, isLoading: loadingSearch } = useSearchUploads(debouncedQuery)

  const uploads = isSearching ? (searchResults ?? []) : (allUploads ?? [])
  const isLoading = isSearching ? loadingSearch : loadingAll

  const handleDelete = (id: string) => {
    if (confirm('Delete this upload? This cannot be undone.')) {
      deleteUpload.mutate(id)
    }
  }

  return (
    <div className="flex-1 space-y-6 p-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Content Library</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {allUploads?.length ?? 0} file{(allUploads?.length ?? 0) !== 1 ? 's' : ''} uploaded
          </p>
        </div>
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search uploads…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-72 w-full rounded-xl" />
          ))}
        </div>
      ) : !uploads.length ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20">
          <Film className="mb-3 h-10 w-10 text-muted-foreground" />
          <p className="text-sm font-medium">
            {isSearching ? 'No results found' : 'No uploads yet'}
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            {isSearching
              ? `No files match "${debouncedQuery}"`
              : 'Upload a file to get started'}
          </p>
          {!isSearching && (
            <Link href="/create">
              <Button variant="outline" size="sm" className="mt-4">
                Create Post
              </Button>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {uploads.map((u) => (
            <UploadCard key={u.id} upload={u} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  )
}
