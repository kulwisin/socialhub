import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { contentService } from "@/services/content.service";
import type { ContentFolderCreate } from "@/types";

export const FOLDERS_KEY = ["content", "folders"] as const;
export const FILES_KEY = (folderId?: string) =>
  ["content", "files", folderId ?? "all"] as const;

export function useContentFolders() {
  return useQuery({
    queryKey: FOLDERS_KEY,
    queryFn: () => contentService.listFolders(),
  });
}

export function useContentFiles(folderId?: string) {
  return useQuery({
    queryKey: FILES_KEY(folderId),
    queryFn: () => contentService.listFiles(folderId),
  });
}

export function useAddFolder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ContentFolderCreate) => contentService.addFolder(data),
    onSuccess: (folder) => {
      qc.invalidateQueries({ queryKey: FOLDERS_KEY });
      toast.success(`Folder "${folder.label}" added`);
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useDeleteFolder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => contentService.deleteFolder(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: FOLDERS_KEY });
      qc.invalidateQueries({ queryKey: ["content", "files"] });
      toast.success("Folder removed");
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useScanFolder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => contentService.scanFolder(id),
    onSuccess: (result, id) => {
      qc.invalidateQueries({ queryKey: FOLDERS_KEY });
      qc.invalidateQueries({ queryKey: FILES_KEY(id) });
      qc.invalidateQueries({ queryKey: FILES_KEY() });
      toast.success(
        `Scan complete — ${result.added} added, ${result.updated} updated, ${result.skipped} unchanged`
      );
    },
    onError: (err: Error) => toast.error(err.message),
  });
}
