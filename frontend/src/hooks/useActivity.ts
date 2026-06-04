import { useQuery } from "@tanstack/react-query";
import { activityService } from "@/services/activity.service";

export const ACTIVITY_KEY = ["activity"] as const;

export function useActivity(limit = 50) {
  return useQuery({
    queryKey: [...ACTIVITY_KEY, limit],
    queryFn: () => activityService.list(limit),
    refetchInterval: 30_000,
  });
}
