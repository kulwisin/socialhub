import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { contentService } from "@/services/content.service";
import type { ContentFolderCreate } from "@/types";

export const ANALYSIS_KEY = (fileId: string) =>
  ["content", "analysis", fileId] as const;
export const GENERATED_KEY = (fileId: string) =>
  ["content", "generated", fileId] as const;

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

export function useAnalyzeFile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (fileId: string) => contentService.analyzeFile(fileId),
    onSuccess: (analysis, fileId) => {
      qc.setQueryData(ANALYSIS_KEY(fileId), analysis);
      qc.invalidateQueries({ queryKey: FILES_KEY() });
      toast.success("Analysis complete");
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useGetAnalysis(fileId: string, enabled = false) {
  return useQuery({
    queryKey: ANALYSIS_KEY(fileId),
    queryFn: () => contentService.getAnalysis(fileId),
    enabled,
    retry: false,
  });
}

export function useGenerateCopy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      fileId,
      platforms,
    }: {
      fileId: string;
      platforms?: string[];
    }) => contentService.generateCopy(fileId, platforms),
    onSuccess: (items, { fileId }) => {
      qc.setQueryData(GENERATED_KEY(fileId), items);
      qc.invalidateQueries({ queryKey: FILES_KEY() });
      toast.success(`Generated copy for ${items.length} platform(s)`);
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useListGenerated(fileId: string, enabled = false) {
  return useQuery({
    queryKey: GENERATED_KEY(fileId),
    queryFn: () => contentService.listGenerated(fileId),
    enabled,
    retry: false,
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
