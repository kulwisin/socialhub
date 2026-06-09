'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { useAuthStore } from '@/lib/auth'

const profileSchema = z.object({
  name: z.string().optional(),
})

const passwordSchema = z
  .object({
    current_password: z.string().min(1, 'Current password is required'),
    new_password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string().min(1, 'Please confirm your password'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
  })

type ProfileValues = z.infer<typeof profileSchema>
type PasswordValues = z.infer<typeof passwordSchema>

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user)

  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors },
  } = useForm<ProfileValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: { name: user?.name ?? '' },
  })

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    reset: resetPassword,
    formState: { errors: passwordErrors },
  } = useForm<PasswordValues>({ resolver: zodResolver(passwordSchema) })

  const onProfileSave = (_values: ProfileValues) => {
    toast.success('Profile saved')
  }

  const onPasswordSave = (_values: PasswordValues) => {
    toast.success('Password updated')
    resetPassword()
  }

  return (
    <div className="flex-1 space-y-8 p-8">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage your account preferences
        </p>
      </div>

      {/* Profile */}
      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileSubmit(onProfileSave)} className="space-y-4 max-w-md">
            <div className="space-y-1.5">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                placeholder="Your name"
                {...registerProfile('name')}
              />
              {profileErrors.name && (
                <p className="text-xs text-destructive">{profileErrors.name.message}</p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={user?.email ?? ''}
                readOnly
                disabled
                className="opacity-60"
              />
              <p className="text-xs text-muted-foreground">Email cannot be changed</p>
            </div>
            <Button type="submit">Save Profile</Button>
          </form>
        </CardContent>
      </Card>

      <Separator />

      {/* Change Password */}
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handlePasswordSubmit(onPasswordSave)}
            className="space-y-4 max-w-md"
          >
            <div className="space-y-1.5">
              <Label htmlFor="current_password">Current Password</Label>
              <Input
                id="current_password"
                type="password"
                placeholder="••••••••"
                {...registerPassword('current_password')}
              />
              {passwordErrors.current_password && (
                <p className="text-xs text-destructive">
                  {passwordErrors.current_password.message}
                </p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="new_password">New Password</Label>
              <Input
                id="new_password"
                type="password"
                placeholder="Min. 8 characters"
                {...registerPassword('new_password')}
              />
              {passwordErrors.new_password && (
                <p className="text-xs text-destructive">
                  {passwordErrors.new_password.message}
                </p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="confirm_password">Confirm New Password</Label>
              <Input
                id="confirm_password"
                type="password"
                placeholder="Re-enter new password"
                {...registerPassword('confirm_password')}
              />
              {passwordErrors.confirm_password && (
                <p className="text-xs text-destructive">
                  {passwordErrors.confirm_password.message}
                </p>
              )}
            </div>
            <Button type="submit">Update Password</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
