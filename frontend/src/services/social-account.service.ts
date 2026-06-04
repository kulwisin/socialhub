import type { MediaFeedResponse, SocialAccount, SyncResponse, TokenRefreshResponse } from "@/types";
import { api } from "./api";

export const socialAccountService = {
  listByDevice: async (deviceId: string): Promise<SocialAccount[]> => {
    const { data } = await api.get<SocialAccount[]>(
      `/devices/${deviceId}/accounts`
    );
    return data;
  },

  disconnect: async (accountId: string): Promise<void> => {
    await api.delete(`/accounts/${accountId}`);
  },

  sync: async (accountId: string): Promise<SyncResponse> => {
    const { data } = await api.post<SyncResponse>(`/accounts/${accountId}/sync`);
    return data;
  },

  refreshToken: async (accountId: string): Promise<TokenRefreshResponse> => {
    const { data } = await api.post<TokenRefreshResponse>(
      `/accounts/${accountId}/refresh-token`
    );
    return data;
  },

  getMedia: async (accountId: string, limit = 12): Promise<MediaFeedResponse> => {
    const { data } = await api.get<MediaFeedResponse>(
      `/accounts/${accountId}/media`,
      { params: { limit } }
    );
    return data;
  },
};
