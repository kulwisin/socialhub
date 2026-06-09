import type { Post, PublishRequest } from '@/types'
import { api } from './api'

export const postService = {
  publish: async (req: PublishRequest): Promise<Post[]> => {
    const { data } = await api.post<Post[]>('/posts/publish', req)
    return data
  },

  list: async (skip = 0, limit = 20): Promise<Post[]> => {
    const { data } = await api.get<Post[]>('/posts', { params: { skip, limit } })
    return data
  },

  get: async (id: string): Promise<Post> => {
    const { data } = await api.get<Post>(`/posts/${id}`)
    return data
  },
}
