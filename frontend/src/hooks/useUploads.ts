import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { uploadService } from "@/services/upload.service";

export const UPLOADS_KEY = ["uploads"] as const;
export const UPLOAD_KEY = (id: string) => ["uploads", id] as const;

export function useUploads(limit = 20) {
  return useQuery({
    queryKey: [...UPLOADS_KEY, limit],
    queryFn: () => uploadService.list(0, limit),
  });
}

export function useUpload(id: string) {
  return useQuery({
    queryKey: UPLOAD_KEY(id),
    queryFn: () => uploadService.get(id),
    enabled: !!id,
  });
}

export function useUploadFile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      file,
      caption,
      onProgress,
    }: {
      file: File;
      caption?: string;
      onProgress?: (pct: number) => void;
    }) => uploadService.upload(file, caption, onProgress),
    onSuccess: (upload) => {
      qc.invalidateQueries({ queryKey: UPLOADS_KEY });
      toast.success(`"${upload.original_filename}" uploaded and ready`);
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useDeleteUpload() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => uploadService.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: UPLOADS_KEY });
      toast.success("Upload deleted");
    },
    onError: (err: Error) => toast.error(err.message),
  });
}
