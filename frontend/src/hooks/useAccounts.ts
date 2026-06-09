import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import type { SocialAccountCreate } from '@/types'
import { accountService } from '@/services/account.service'

export const ACCOUNTS_KEY = ['accounts'] as const

export function useAccounts() {
  return useQuery({
    queryKey: ACCOUNTS_KEY,
    queryFn: () => accountService.list(),
  })
}

export function useAddAccount() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: SocialAccountCreate) => accountService.add(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ACCOUNTS_KEY })
      toast.success('Account connected')
    },
    onError: (err: Error) => toast.error(err.message),
  })
}

export function useRemoveAccount() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => accountService.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ACCOUNTS_KEY })
      toast.success('Account removed')
    },
    onError: (err: Error) => toast.error(err.message),
  })
}

export function useToggleAccount() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => accountService.toggle(id),
    onSuccess: (account) => {
      qc.invalidateQueries({ queryKey: ACCOUNTS_KEY })
      toast.success(account.is_active ? 'Account activated' : 'Account deactivated')
    },
    onError: (err: Error) => toast.error(err.message),
  })
}
