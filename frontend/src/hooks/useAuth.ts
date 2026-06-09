'use client'

import { useMutation } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { authService } from '@/services/auth.service'
import { useAuthStore } from '@/lib/auth'

export function useRegister() {
  const router = useRouter()
  const setAuth = useAuthStore((s) => s.setAuth)

  return useMutation({
    mutationFn: ({ email, password, name }: { email: string; password: string; name?: string }) =>
      authService.register(email, password, name),
    onSuccess: (data) => {
      setAuth(data.access_token, data.user)
      router.push('/dashboard')
    },
    onError: (err: Error) => toast.error(err.message),
  })
}

export function useLogin() {
  const router = useRouter()
  const setAuth = useAuthStore((s) => s.setAuth)

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authService.login(email, password),
    onSuccess: (data) => {
      setAuth(data.access_token, data.user)
      router.push('/dashboard')
    },
    onError: (err: Error) => toast.error(err.message),
  })
}

export function useLogout() {
  const router = useRouter()
  const logout = useAuthStore((s) => s.logout)

  return () => {
    logout()
    router.push('/login')
  }
}
