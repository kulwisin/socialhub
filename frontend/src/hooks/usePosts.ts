import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { PublishRequest } from "@/types";
import { postService } from "@/services/post.service";
import { UPLOADS_KEY } from "./useUploads";

export const POSTS_KEY = ["posts"] as const;

export function usePosts(limit = 20, statusFilter?: string) {
  return useQuery({
    queryKey: [...POSTS_KEY, limit, statusFilter],
    queryFn: () => postService.list(limit, statusFilter),
  });
}

export function usePublish() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (request: PublishRequest) => postService.publish(request),
    onSuccess: (result) => {
      qc.invalidateQueries({ queryKey: POSTS_KEY });
      qc.invalidateQueries({ queryKey: UPLOADS_KEY });
      if (result.failed === 0) {
        toast.success(
          `Published to ${result.succeeded} account${result.succeeded !== 1 ? "s" : ""}`
        );
      } else if (result.succeeded === 0) {
        toast.error(`All ${result.failed} publishes failed`);
      } else {
        toast.warning(
          `${result.succeeded} published, ${result.failed} failed`
        );
      }
    },
    onError: (err: Error) => toast.error(err.message),
  });
}
