'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus, Trash2, Users } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Dialog, DialogHeader } from '@/components/ui/dialog'
import { Select } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { useAccounts, useAddAccount, useRemoveAccount, useToggleAccount } from '@/hooks/useAccounts'
import { PLATFORM_META } from '@/types'
import type { Platform, SocialAccountCreate } from '@/types'
import { cn, formatNumber } from '@/lib/utils'

const PLATFORMS = Object.keys(PLATFORM_META) as Platform[]
const ALL_TAB = 'all'

const schema = z.object({
  platform: z.enum(['instagram', 'youtube', 'tiktok', 'x', 'threads', 'snapchat']),
  username: z.string().min(1, 'Username is required'),
  platform_user_id: z.string().min(1, 'Platform User ID is required'),
  access_token: z.string().min(1, 'Access token is required'),
  display_name: z.string().optional(),
  refresh_token: z.string().optional(),
  token_expires_at: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

export default function AccountsPage() {
  const { data: accounts, isLoading } = useAccounts()
  const addAccount = useAddAccount()
  const removeAccount = useRemoveAccount()
  const toggleAccount = useToggleAccount()

  const [activeTab, setActiveTab] = useState<Platform | typeof ALL_TAB>(ALL_TAB)
  const [showDialog, setShowDialog] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { platform: 'instagram' } })

  const filtered =
    activeTab === ALL_TAB
      ? (accounts ?? [])
      : (accounts ?? []).filter((a) => a.platform === activeTab)

  const onSubmit = (values: FormValues) => {
    const payload: SocialAccountCreate = {
      platform: values.platform,
      username: values.username,
      platform_user_id: values.platform_user_id,
      access_token: values.access_token,
      ...(values.display_name ? { display_name: values.display_name } : {}),
      ...(values.refresh_token ? { refresh_token: values.refresh_token } : {}),
      ...(values.token_expires_at ? { token_expires_at: values.token_expires_at } : {}),
    }
    addAccount.mutate(payload, {
      onSuccess: () => {
        setShowDialog(false)
        reset()
      },
    })
  }

  const handleRemove = (id: string, username: string) => {
    if (confirm(`Remove @${username}? This cannot be undone.`)) {
      removeAccount.mutate(id)
    }
  }

  return (
    <div className="flex-1 space-y-6 p-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Connected Accounts</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage your social media accounts
          </p>
        </div>
        <Button onClick={() => setShowDialog(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Account
        </Button>
      </div>

      {/* Platform filter tabs */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setActiveTab(ALL_TAB)}
          className={cn(
            'rounded-full px-4 py-1.5 text-sm font-medium transition-colors',
            activeTab === ALL_TAB
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground hover:bg-accent hover:text-foreground'
          )}
        >
          All
        </button>
        {PLATFORMS.map((p) => (
          <button
            key={p}
            onClick={() => setActiveTab(p)}
            className={cn(
              'rounded-full px-4 py-1.5 text-sm font-medium transition-colors',
              activeTab === p
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-accent hover:text-foreground'
            )}
          >
            {PLATFORM_META[p].icon} {PLATFORM_META[p].label}
          </button>
        ))}
      </div>

      {/* Account cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-40 w-full rounded-xl" />
          ))}
        </div>
      ) : !filtered.length ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16">
          <Users className="mb-3 h-10 w-10 text-muted-foreground" />
          <p className="text-sm font-medium">No accounts connected</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Add an account to start publishing
          </p>
          <Button variant="outline" size="sm" className="mt-4 gap-2" onClick={() => setShowDialog(true)}>
            <Plus className="h-3.5 w-3.5" /> Add Account
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((account) => {
            const meta = PLATFORM_META[account.platform]
            return (
              <Card key={account.id}>
                <CardContent className="p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-lg text-white',
                          meta.color
                        )}
                      >
                        {meta.icon}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium">{meta.label}</p>
                        <p className="truncate text-xs text-muted-foreground">
                          @{account.username}
                        </p>
                      </div>
                    </div>
                    <Switch
                      checked={account.is_active}
                      onCheckedChange={() => toggleAccount.mutate(account.id)}
                      disabled={toggleAccount.isPending}
                    />
                  </div>

                  <div className="mt-4 space-y-1">
                    {account.display_name && (
                      <p className="text-sm font-medium">{account.display_name}</p>
                    )}
                    <p className="text-xs text-muted-foreground">
                      {formatNumber(account.followers_count)} followers
                    </p>
                  </div>

                  <div className="mt-4 flex items-center justify-between">
                    <Badge variant={account.is_active ? 'success' : 'default'}>
                      {account.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemove(account.id, account.username)}
                      disabled={removeAccount.isPending}
                      className="gap-1.5 text-destructive hover:bg-destructive/10 hover:text-destructive"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      Remove
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Add Account Dialog */}
      <Dialog open={showDialog} onClose={() => setShowDialog(false)} className="max-w-xl">
        <DialogHeader title="Add Account" onClose={() => setShowDialog(false)} />
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="platform">Platform</Label>
            <Select id="platform" {...register('platform')}>
              {PLATFORMS.map((p) => (
                <option key={p} value={p}>
                  {PLATFORM_META[p].icon} {PLATFORM_META[p].label}
                </option>
              ))}
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="username">Username</Label>
              <Input id="username" placeholder="@handle" {...register('username')} />
              {errors.username && (
                <p className="text-xs text-destructive">{errors.username.message}</p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="platform_user_id">Platform User ID</Label>
              <Input id="platform_user_id" placeholder="12345678" {...register('platform_user_id')} />
              {errors.platform_user_id && (
                <p className="text-xs text-destructive">{errors.platform_user_id.message}</p>
              )}
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="access_token">Access Token</Label>
            <Input id="access_token" type="password" placeholder="••••••••" {...register('access_token')} />
            {errors.access_token && (
              <p className="text-xs text-destructive">{errors.access_token.message}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="display_name">Display Name (optional)</Label>
            <Input id="display_name" placeholder="John Doe" {...register('display_name')} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="refresh_token">Refresh Token (optional)</Label>
              <Input id="refresh_token" type="password" placeholder="••••••••" {...register('refresh_token')} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="token_expires_at">Token Expiry (optional)</Label>
              <Input id="token_expires_at" type="datetime-local" {...register('token_expires_at')} />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="outline" onClick={() => setShowDialog(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={addAccount.isPending}>
              {addAccount.isPending ? 'Connecting…' : 'Connect Account'}
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
