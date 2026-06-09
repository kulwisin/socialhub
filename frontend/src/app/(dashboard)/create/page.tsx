'use client'

import { useState, useCallback, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useDropzone } from 'react-dropzone'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Upload,
  X,
  CheckSquare,
  Square,
  Film,
  Hash,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Skeleton } from '@/components/ui/skeleton'
import { useUploadFile, useUpload } from '@/hooks/useUploads'
import { useAccounts } from '@/hooks/useAccounts'
import { usePublish } from '@/hooks/usePosts'
import { PLATFORM_META } from '@/types'
import type { Platform } from '@/types'
import { cn, formatFileSize } from '@/lib/utils'

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

export default function CreatePostPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const preloadUploadId = searchParams.get('upload_id')

  const [uploadId, setUploadId] = useState<string | null>(preloadUploadId)
  const [uploadedFile, setUploadedFile] = useState<{ name: string; size: number } | null>(null)
  const [hashtags, setHashtags] = useState<string[]>([])
  const [hashtagInput, setHashtagInput] = useState('')
  const [selectedAccountIds, setSelectedAccountIds] = useState<Set<string>>(new Set())

  const uploadFile = useUploadFile()
  const { data: accounts, isLoading: loadingAccounts } = useAccounts()
  const publish = usePublish()
  const { data: preloadedUpload } = useUpload(preloadUploadId ?? '')

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const watchedTitle = watch('title', '')
  const watchedDescription = watch('description', '')

  // Pre-fill from existing upload
  useEffect(() => {
    if (preloadedUpload) {
      setUploadedFile({
        name: preloadedUpload.original_filename,
        size: preloadedUpload.file_size_bytes ?? 0,
      })
      if (preloadedUpload.title) setValue('title', preloadedUpload.title)
      if (preloadedUpload.description) setValue('description', preloadedUpload.description)
      if (preloadedUpload.hashtags) setHashtags(preloadedUpload.hashtags)
    }
  }, [preloadedUpload, setValue])

  const onDrop = useCallback(
    (accepted: File[]) => {
      const file = accepted[0]
      if (!file) return
      setUploadedFile({ name: file.name, size: file.size })
      uploadFile.mutate(
        { file },
        {
          onSuccess: (upload) => {
            setUploadId(upload.id)
          },
        }
      )
    },
    [uploadFile]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'video/*': [], 'image/*': [] },
    maxFiles: 1,
    disabled: uploadFile.isPending,
  })

  const addHashtag = (raw: string) => {
    const tag = raw.replace(/^#/, '').trim()
    if (tag && !hashtags.includes(tag)) {
      setHashtags((prev) => [...prev, tag])
    }
    setHashtagInput('')
  }

  const handleHashtagKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addHashtag(hashtagInput)
    }
  }

  const removeHashtag = (tag: string) => {
    setHashtags((prev) => prev.filter((t) => t !== tag))
  }

  // Group accounts by platform
  const byPlatform = (accounts ?? []).reduce<Record<Platform, typeof accounts>>(
    (acc, a) => {
      if (!acc[a.platform]) acc[a.platform] = []
      acc[a.platform]!.push(a)
      return acc
    },
    {} as Record<Platform, typeof accounts>
  )

  const toggleAccount = (id: string) => {
    setSelectedAccountIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const togglePlatform = (platform: Platform) => {
    const platformAccounts = byPlatform[platform] ?? []
    const allSelected = platformAccounts.every((a) => selectedAccountIds.has(a!.id))
    setSelectedAccountIds((prev) => {
      const next = new Set(prev)
      if (allSelected) {
        platformAccounts.forEach((a) => next.delete(a!.id))
      } else {
        platformAccounts.forEach((a) => next.add(a!.id))
      }
      return next
    })
  }

  const canPublish =
    !!uploadId && !uploadFile.isPending && selectedAccountIds.size > 0

  const onSubmit = (values: FormValues) => {
    if (!uploadId) return
    publish.mutate(
      {
        upload_id: uploadId,
        account_ids: Array.from(selectedAccountIds),
        title: values.title,
        description: values.description,
        hashtags,
      },
      {
        onSuccess: () => router.push('/library'),
      }
    )
  }

  return (
    <div className="flex-1 p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Create Post</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Upload media and publish to your connected platforms
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Left: Form */}
          <div className="space-y-6">
            {/* Upload zone */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">1. Upload Media</CardTitle>
              </CardHeader>
              <CardContent>
                {uploadedFile ? (
                  <div className="flex items-center gap-3 rounded-lg border border-border bg-muted/30 p-4">
                    <Film className="h-8 w-8 shrink-0 text-primary" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{uploadedFile.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatFileSize(uploadedFile.size)}
                        {uploadFile.isPending && ' — uploading…'}
                        {uploadId && !uploadFile.isPending && ' — ready'}
                      </p>
                    </div>
                    {!uploadFile.isPending && (
                      <button
                        type="button"
                        onClick={() => {
                          setUploadedFile(null)
                          setUploadId(null)
                        }}
                        className="shrink-0 text-muted-foreground hover:text-foreground"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                ) : (
                  <div
                    {...getRootProps()}
                    className={cn(
                      'flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-border p-10 text-center transition-colors',
                      isDragActive && 'border-primary bg-primary/5'
                    )}
                  >
                    <input {...getInputProps()} />
                    <Upload className="h-8 w-8 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">
                        {isDragActive ? 'Drop your file here' : 'Drag & drop or click to upload'}
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Video or image files supported
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Title + Description */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">2. Content Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="title">Title *</Label>
                  <Input id="title" placeholder="Give your post a title" {...register('title')} />
                  {errors.title && (
                    <p className="text-xs text-destructive">{errors.title.message}</p>
                  )}
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Write a description…"
                    rows={4}
                    {...register('description')}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>Hashtags</Label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add tag and press Enter"
                      value={hashtagInput}
                      onChange={(e) => setHashtagInput(e.target.value)}
                      onKeyDown={handleHashtagKey}
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => addHashtag(hashtagInput)}
                      disabled={!hashtagInput.trim()}
                    >
                      <Hash className="h-4 w-4" />
                    </Button>
                  </div>
                  {hashtags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {hashtags.map((tag) => (
                        <span
                          key={tag}
                          className="flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary"
                        >
                          #{tag}
                          <button
                            type="button"
                            onClick={() => removeHashtag(tag)}
                            className="hover:text-destructive"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Platform & Account selection */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">3. Select Platforms & Accounts</CardTitle>
              </CardHeader>
              <CardContent>
                {loadingAccounts ? (
                  <div className="space-y-3">
                    {[1, 2].map((i) => <Skeleton key={i} className="h-14 w-full" />)}
                  </div>
                ) : !accounts?.length ? (
                  <p className="text-sm text-muted-foreground">
                    No accounts connected. <a href="/accounts" className="text-primary underline">Add one first.</a>
                  </p>
                ) : (
                  <div className="space-y-4">
                    {(Object.keys(byPlatform) as Platform[]).map((platform) => {
                      const platformAccounts = byPlatform[platform] ?? []
                      const allSelected = platformAccounts.every((a) =>
                        selectedAccountIds.has(a!.id)
                      )
                      const meta = PLATFORM_META[platform]
                      return (
                        <div key={platform}>
                          <div className="mb-2 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span>{meta.icon}</span>
                              <span className="text-sm font-medium">{meta.label}</span>
                            </div>
                            <button
                              type="button"
                              onClick={() => togglePlatform(platform)}
                              className="text-xs text-primary hover:underline"
                            >
                              {allSelected ? 'Deselect All' : 'Select All'}
                            </button>
                          </div>
                          <div className="space-y-1.5">
                            {platformAccounts.map((a) => {
                              if (!a) return null
                              const checked = selectedAccountIds.has(a.id)
                              return (
                                <button
                                  key={a.id}
                                  type="button"
                                  onClick={() => toggleAccount(a.id)}
                                  className={cn(
                                    'flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors',
                                    checked
                                      ? 'border-primary bg-primary/5'
                                      : 'border-border hover:bg-accent/50'
                                  )}
                                >
                                  {checked ? (
                                    <CheckSquare className="h-4 w-4 shrink-0 text-primary" />
                                  ) : (
                                    <Square className="h-4 w-4 shrink-0 text-muted-foreground" />
                                  )}
                                  <div className="min-w-0">
                                    <p className="truncate text-sm font-medium">
                                      @{a.username}
                                    </p>
                                    {a.display_name && (
                                      <p className="truncate text-xs text-muted-foreground">
                                        {a.display_name}
                                      </p>
                                    )}
                                  </div>
                                </button>
                              )
                            })}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            <Button
              type="submit"
              size="lg"
              className="w-full"
              disabled={!canPublish || publish.isPending}
            >
              {publish.isPending
                ? 'Publishing…'
                : `Publish to ${selectedAccountIds.size} account${selectedAccountIds.size !== 1 ? 's' : ''}`}
            </Button>
          </div>

          {/* Right: Preview */}
          <div className="hidden lg:block">
            <div className="sticky top-8">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Preview</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex h-48 items-center justify-center rounded-xl bg-muted">
                    {uploadedFile ? (
                      <Film className="h-12 w-12 text-muted-foreground" />
                    ) : (
                      <Upload className="h-12 w-12 text-muted-foreground/50" />
                    )}
                  </div>
                  <div>
                    <p className="font-semibold">
                      {watchedTitle || <span className="text-muted-foreground">Post title</span>}
                    </p>
                    {watchedDescription && (
                      <p className="mt-2 text-sm text-muted-foreground line-clamp-3">
                        {watchedDescription}
                      </p>
                    )}
                    {hashtags.length > 0 && (
                      <p className="mt-2 text-sm text-primary">
                        {hashtags.map((t) => `#${t}`).join(' ')}
                      </p>
                    )}
                  </div>
                  {selectedAccountIds.size > 0 && (
                    <div className="rounded-lg bg-muted/50 p-3">
                      <p className="text-xs text-muted-foreground">
                        Publishing to {selectedAccountIds.size} account
                        {selectedAccountIds.size !== 1 ? 's' : ''}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </form>
    </div>
  )
}
