import type { ContentFile, ContentFolder, ContentFolderCreate, ScanResult } from "@/types";
import { api } from "./api";

export const contentService = {
  // ── folders ────────────────────────────────────────────────────────────

  addFolder: async (data: ContentFolderCreate): Promise<ContentFolder> => {
    const { data: result } = await api.post<ContentFolder>("/content/folders", data);
    return result;
  },

  listFolders: async (): Promise<ContentFolder[]> => {
    const { data } = await api.get<ContentFolder[]>("/content/folders");
    return data;
  },

  deleteFolder: async (id: string): Promise<void> => {
    await api.delete(`/content/folders/${id}`);
  },

  scanFolder: async (id: string): Promise<ScanResult> => {
    const { data } = await api.post<ScanResult>(`/content/folders/${id}/scan`);
    return data;
  },

  // ── files ──────────────────────────────────────────────────────────────

  listFiles: async (
    folderId?: string,
    status?: string,
    skip = 0,
    limit = 50
  ): Promise<ContentFile[]> => {
    const { data } = await api.get<ContentFile[]>("/content/files", {
      params: { folder_id: folderId, status, skip, limit },
    });
    return data;
  },
};
