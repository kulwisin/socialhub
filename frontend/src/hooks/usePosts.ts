import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import type { PublishRequest } from '@/types'
import { postService } from '@/services/post.service'
import { UPLOADS_KEY } from './useUploads'

export const POSTS_KEY = ['posts'] as const

export function usePosts(limit = 20) {
  return useQuery({
    queryKey: [...POSTS_KEY, limit],
    queryFn: () => postService.list(0, limit),
  })
}

export function usePost(id: string) {
  return useQuery({
    queryKey: [...POSTS_KEY, id],
    queryFn: () => postService.get(id),
    enabled: !!id,
  })
}

export function usePublish() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (req: PublishRequest) => postService.publish(req),
    onSuccess: (posts) => {
      qc.invalidateQueries({ queryKey: POSTS_KEY })
      qc.invalidateQueries({ queryKey: UPLOADS_KEY })
      toast.success(`Published to ${posts.length} account${posts.length !== 1 ? 's' : ''}`)
    },
    onError: (err: Error) => toast.error(err.message),
  })
}
