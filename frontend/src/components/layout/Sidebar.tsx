'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Link2,
  PlusCircle,
  Library,
  Settings,
  Zap,
  LogOut,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/lib/auth'
import { useLogout } from '@/hooks/useAuth'

const NAV = [
  { href: '/dashboard', label: 'Dashboard',           icon: LayoutDashboard },
  { href: '/accounts',  label: 'Connected Accounts',  icon: Link2 },
  { href: '/create',    label: 'Create Post',          icon: PlusCircle },
  { href: '/library',   label: 'Content Library',      icon: Library },
  { href: '/settings',  label: 'Settings',             icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const user = useAuthStore((s) => s.user)
  const logout = useLogout()

  return (
    <aside className="flex h-screen w-60 flex-col border-r border-border bg-card">
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center gap-3 border-b border-border px-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <Zap className="h-4 w-4 text-white" />
        </div>
        <span className="text-base font-semibold tracking-tight">SocialHub</span>
      </div>

      {/* Nav */}
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-3">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active =
            href === '/dashboard'
              ? pathname === '/dashboard' || pathname === '/'
              : pathname.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                active
                  ? 'bg-primary/15 text-primary'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground'
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-border p-4 space-y-3">
        {user && (
          <p className="truncate text-xs text-muted-foreground">{user.email}</p>
        )}
        <button
          onClick={logout}
          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
