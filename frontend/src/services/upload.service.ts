import type { Upload } from '@/types'
import { api } from './api'

export const uploadService = {
  upload: async (
    file: File,
    title?: string,
    description?: string,
    hashtags?: string[]
  ): Promise<Upload> => {
    const form = new FormData()
    form.append('file', file)
    if (title) form.append('title', title)
    if (description) form.append('description', description)
    if (hashtags && hashtags.length > 0) form.append('hashtags', hashtags.join(','))

    const { data } = await api.post<Upload>('/uploads', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  list: async (skip = 0, limit = 20): Promise<Upload[]> => {
    const { data } = await api.get<Upload[]>('/uploads', { params: { skip, limit } })
    return data
  },

  search: async (q: string, skip = 0, limit = 20): Promise<Upload[]> => {
    const { data } = await api.get<Upload[]>('/uploads/search', { params: { q, skip, limit } })
    return data
  },

  get: async (id: string): Promise<Upload> => {
    const { data } = await api.get<Upload>(`/uploads/${id}`)
    return data
  },

  update: async (
    id: string,
    payload: Partial<{ title: string; description: string; hashtags: string[] }>
  ): Promise<Upload> => {
    const { data } = await api.patch<Upload>(`/uploads/${id}`, payload)
    return data
  },

  remove: async (id: string): Promise<void> => {
    await api.delete(`/uploads/${id}`)
  },
}
