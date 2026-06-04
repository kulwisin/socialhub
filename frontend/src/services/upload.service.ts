import type { Upload } from "@/types";
import { api } from "./api";
import { env } from "@/lib/env";

export const uploadService = {
  list: async (skip = 0, limit = 20): Promise<Upload[]> => {
    const { data } = await api.get<Upload[]>("/uploads", {
      params: { skip, limit },
    });
    return data;
  },

  get: async (id: string): Promise<Upload> => {
    const { data } = await api.get<Upload>(`/uploads/${id}`);
    return data;
  },

  upload: async (
    file: File,
    caption?: string,
    onProgress?: (pct: number) => void
  ): Promise<Upload> => {
    const form = new FormData();
    form.append("file", file);
    if (caption) form.append("caption", caption);

    const { data } = await api.post<Upload>("/uploads", form, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (evt) => {
        if (evt.total && onProgress) {
          onProgress(Math.round((evt.loaded / evt.total) * 100));
        }
      },
    });
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/uploads/${id}`);
  },

  mediaUrl: (filePath: string): string =>
    `${env.API_URL}/media/${filePath}`,

  thumbnailUrl: (thumbnailPath: string | null): string | null =>
    thumbnailPath ? `${env.API_URL}/media/${thumbnailPath}` : null,
};
