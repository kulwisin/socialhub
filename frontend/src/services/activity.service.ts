import type { ActivityLog } from "@/types";
import { api } from "./api";

export const activityService = {
  list: async (limit = 50): Promise<ActivityLog[]> => {
    const { data } = await api.get<ActivityLog[]>("/activity", {
      params: { limit },
    });
    return data;
  },
};
