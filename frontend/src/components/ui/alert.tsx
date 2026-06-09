import { cn } from '@/lib/utils'
import { AlertCircle, Info } from 'lucide-react'

interface AlertProps {
  variant?: 'default' | 'destructive'
  title: string
  description?: string
}

export function Alert({ variant = 'default', title, description }: AlertProps) {
  const isDestructive = variant === 'destructive'
  return (
    <div
      role="alert"
      className={cn(
        'flex items-start gap-3 rounded-lg border p-4 text-sm',
        isDestructive
          ? 'border-destructive/30 bg-destructive/10 text-destructive'
          : 'border-border bg-muted text-foreground'
      )}
    >
      {isDestructive ? (
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
      ) : (
        <Info className="mt-0.5 h-4 w-4 shrink-0" />
      )}
      <div>
        <p className="font-medium">{title}</p>
        {description && <p className="mt-1 text-muted-foreground">{description}</p>}
      </div>
    </div>
  )
}
