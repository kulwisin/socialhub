import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { DeviceCreate, DeviceUpdate } from "@/types";
import { deviceService } from "@/services/device.service";

export const DEVICES_KEY = ["devices"] as const;
export const DEVICE_KEY = (id: string) => ["devices", id] as const;

export function useDevices() {
  return useQuery({
    queryKey: DEVICES_KEY,
    queryFn: deviceService.list,
  });
}

export function useDevice(id: string) {
  return useQuery({
    queryKey: DEVICE_KEY(id),
    queryFn: () => deviceService.get(id),
    enabled: !!id,
  });
}

export function useCreateDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: DeviceCreate) => deviceService.create(data),
    onSuccess: (device) => {
      qc.invalidateQueries({ queryKey: DEVICES_KEY });
      toast.success(`Device "${device.name}" created`);
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useUpdateDevice(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: DeviceUpdate) => deviceService.update(id, data),
    onSuccess: (device) => {
      qc.invalidateQueries({ queryKey: DEVICES_KEY });
      qc.invalidateQueries({ queryKey: DEVICE_KEY(id) });
      toast.success(`Device "${device.name}" updated`);
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useDeleteDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deviceService.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: DEVICES_KEY });
      toast.success("Device deleted");
    },
    onError: (err: Error) => toast.error(err.message),
  });
}
