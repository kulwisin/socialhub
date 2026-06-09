import type { SocialAccount, SocialAccountCreate } from '@/types'
import { api } from './api'

export const accountService = {
  list: async (): Promise<SocialAccount[]> => {
    const { data } = await api.get<SocialAccount[]>('/accounts')
    return data
  },

  add: async (payload: SocialAccountCreate): Promise<SocialAccount> => {
    const { data } = await api.post<SocialAccount>('/accounts', payload)
    return data
  },

  remove: async (id: string): Promise<void> => {
    await api.delete(`/accounts/${id}`)
  },

  toggle: async (id: string): Promise<SocialAccount> => {
    const { data } = await api.patch<SocialAccount>(`/accounts/${id}/toggle`)
    return data
  },
}
