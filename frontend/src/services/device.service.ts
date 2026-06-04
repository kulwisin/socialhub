import type { Device, DeviceCreate, DeviceUpdate } from "@/types";
import { api } from "./api";

export const deviceService = {
  list: async (): Promise<Device[]> => {
    const { data } = await api.get<Device[]>("/devices");
    return data;
  },

  get: async (id: string): Promise<Device> => {
    const { data } = await api.get<Device>(`/devices/${id}`);
    return data;
  },

  create: async (body: DeviceCreate): Promise<Device> => {
    const { data } = await api.post<Device>("/devices", body);
    return data;
  },

  update: async (id: string, body: DeviceUpdate): Promise<Device> => {
    const { data } = await api.patch<Device>(`/devices/${id}`, body);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/devices/${id}`);
  },

  getAuthorizeUrl: async (deviceId: string): Promise<{ url: string }> => {
    const { data } = await api.get<{ url: string }>(
      `/auth/meta/authorize?device_id=${deviceId}`
    );
    return data;
  },
};
