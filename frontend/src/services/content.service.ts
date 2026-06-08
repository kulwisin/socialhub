import type {
  AiAnalysis,
  ContentFile,
  ContentFolder,
  ContentFolderCreate,
  GeneratedContent,
  ScanResult,
} from "@/types";
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

  // ── AI analysis ────────────────────────────────────────────────────────

  analyzeFile: async (id: string): Promise<AiAnalysis> => {
    const { data } = await api.post<AiAnalysis>(`/content/files/${id}/analyze`);
    return data;
  },

  getAnalysis: async (id: string): Promise<AiAnalysis> => {
    const { data } = await api.get<AiAnalysis>(`/content/files/${id}/analysis`);
    return data;
  },

  generateCopy: async (
    id: string,
    platforms?: string[]
  ): Promise<GeneratedContent[]> => {
    const { data } = await api.post<GeneratedContent[]>(
      `/content/files/${id}/generate`,
      platforms ? { platforms } : {}
    );
    return data;
  },

  listGenerated: async (id: string): Promise<GeneratedContent[]> => {
    const { data } = await api.get<GeneratedContent[]>(
      `/content/files/${id}/generated`
    );
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
