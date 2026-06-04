import type { Post, PublishRequest, PublishResponse } from "@/types";
import { api } from "./api";

export const postService = {
  list: async (limit = 20, statusFilter?: string): Promise<Post[]> => {
    const { data } = await api.get<Post[]>("/posts", {
      params: { limit, status_filter: statusFilter },
    });
    return data;
  },

  get: async (id: string): Promise<Post> => {
    const { data } = await api.get<Post>(`/posts/${id}`);
    return data;
  },

  publish: async (request: PublishRequest): Promise<PublishResponse> => {
    const { data } = await api.post<PublishResponse>("/posts/publish", request);
    return data;
  },
};
