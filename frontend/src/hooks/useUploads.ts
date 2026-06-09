import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { uploadService } from '@/services/upload.service'

export const UPLOADS_KEY = ['uploads'] as const
export const UPLOAD_KEY = (id: string) => ['uploads', id] as const

export function useUploads(limit = 20) {
  return useQuery({
    queryKey: [...UPLOADS_KEY, limit],
    queryFn: () => uploadService.list(0, limit),
  })
}

export function useUpload(id: string) {
  return useQuery({
    queryKey: UPLOAD_KEY(id),
    queryFn: () => uploadService.get(id),
    enabled: !!id,
  })
}

export function useSearchUploads(q: string) {
  return useQuery({
    queryKey: ['uploads', 'search', q],
    queryFn: () => uploadService.search(q),
    enabled: q.length > 1,
  })
}

export function useUploadFile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      file,
      title,
      description,
      hashtags,
    }: {
      file: File
      title?: string
      description?: string
      hashtags?: string[]
    }) => uploadService.upload(file, title, description, hashtags),
    onSuccess: (upload) => {
      qc.invalidateQueries({ queryKey: UPLOADS_KEY })
      toast.success(`"${upload.original_filename}" uploaded`)
    },
    onError: (err: Error) => toast.error(err.message),
  })
}

export function useUpdateUpload() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string
      data: Partial<{ title: string; description: string; hashtags: string[] }>
    }) => uploadService.update(id, data),
    onSuccess: (upload) => {
      qc.invalidateQueries({ queryKey: UPLOADS_KEY })
      qc.invalidateQueries({ queryKey: UPLOAD_KEY(upload.id) })
      toast.success('Upload updated')
    },
    onError: (err: Error) => toast.error(err.message),
  })
}

export function useDeleteUpload() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => uploadService.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: UPLOADS_KEY })
      toast.success('Upload deleted')
    },
    onError: (err: Error) => toast.error(err.message),
  })
}
