import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { socialAccountService } from "@/services/social-account.service";
import { DEVICE_KEY, DEVICES_KEY } from "./useDevices";

export const ACCOUNTS_KEY = (deviceId: string) =>
  ["devices", deviceId, "accounts"] as const;

export const MEDIA_KEY = (accountId: string) =>
  ["accounts", accountId, "media"] as const;

export function useSocialAccounts(deviceId: string) {
  return useQuery({
    queryKey: ACCOUNTS_KEY(deviceId),
    queryFn: () => socialAccountService.listByDevice(deviceId),
    enabled: !!deviceId,
  });
}

export function useAccountMedia(accountId: string, limit = 12) {
  return useQuery({
    queryKey: MEDIA_KEY(accountId),
    queryFn: () => socialAccountService.getMedia(accountId, limit),
    enabled: !!accountId,
    staleTime: 60_000,
  });
}

export function useDisconnectAccount(deviceId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (accountId: string) =>
      socialAccountService.disconnect(accountId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ACCOUNTS_KEY(deviceId) });
      qc.invalidateQueries({ queryKey: DEVICE_KEY(deviceId) });
      qc.invalidateQueries({ queryKey: DEVICES_KEY });
      toast.success("Account disconnected");
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useSyncAccount(deviceId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (accountId: string) =>
      socialAccountService.sync(accountId),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ACCOUNTS_KEY(deviceId) });
      qc.invalidateQueries({ queryKey: DEVICE_KEY(deviceId) });
      toast.success(
        `@${res.account.username} synced: ${res.account.followers_count.toLocaleString()} followers`
      );
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useRefreshToken() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (accountId: string) =>
      socialAccountService.refreshToken(accountId),
    onSuccess: (res) => {
      if (res.refreshed) {
        toast.success("Token refreshed — valid for another 60 days");
      } else {
        toast.info(res.message);
      }
    },
    onError: (err: Error) => toast.error(err.message),
  });
}
