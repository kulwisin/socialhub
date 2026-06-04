"use client";

import { useState } from "react";
import { Plus, Smartphone } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { DeviceCard } from "@/features/devices/DeviceCard";
import { CreateDeviceModal } from "@/features/devices/CreateDeviceModal";
import { useDevices } from "@/hooks/useDevices";

export default function DevicesPage() {
  const { data: devices, isLoading, isError } = useDevices();
  const [createOpen, setCreateOpen] = useState(false);

  return (
    <>
      <Header
        title="Devices"
        description="Each device holds a set of connected social accounts."
        action={
          <Button onClick={() => setCreateOpen(true)} className="gap-2">
            <Plus className="h-4 w-4" />
            New Device
          </Button>
        }
      />

      <div className="flex-1 p-8">
        {isLoading && (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-44 w-full rounded-xl" />
            ))}
          </div>
        )}

        {isError && (
          <p className="text-center text-sm text-destructive">
            Failed to load devices. Is the backend running?
          </p>
        )}

        {!isLoading && !isError && devices?.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
              <Smartphone className="h-8 w-8 text-primary" />
            </div>
            <h2 className="text-lg font-semibold">No devices yet</h2>
            <p className="mt-2 max-w-sm text-sm text-muted-foreground">
              Create your first device to start connecting Instagram and Facebook accounts.
            </p>
            <Button className="mt-6 gap-2" onClick={() => setCreateOpen(true)}>
              <Plus className="h-4 w-4" />
              Create your first device
            </Button>
          </div>
        )}

        {!isLoading && !isError && (devices?.length ?? 0) > 0 && (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {devices!.map((device) => (
              <DeviceCard key={device.id} device={device} />
            ))}
          </div>
        )}
      </div>

      <CreateDeviceModal open={createOpen} onClose={() => setCreateOpen(false)} />
    </>
  );
}
