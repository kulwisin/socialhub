"use client";

import Link from "next/link";
import { Smartphone, Trash2, Instagram, Facebook, Music2 } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useDeleteDevice } from "@/hooks/useDevices";
import type { Device, Platform } from "@/types";
import { cn } from "@/lib/utils";

const PLATFORM_ICON: Record<Platform, React.ReactNode> = {
  instagram: <Instagram className="h-3.5 w-3.5" />,
  facebook: <Facebook className="h-3.5 w-3.5" />,
  tiktok: <Music2 className="h-3.5 w-3.5" />,
};

const PLATFORM_BADGE: Record<Platform, "instagram" | "facebook" | "tiktok"> = {
  instagram: "instagram",
  facebook: "facebook",
  tiktok: "tiktok",
};

interface DeviceCardProps {
  device: Device;
}

export function DeviceCard({ device }: DeviceCardProps) {
  const deleteDevice = useDeleteDevice();

  function handleDelete(e: React.MouseEvent) {
    e.preventDefault();
    if (confirm(`Delete "${device.name}"? All connected accounts will be disconnected.`)) {
      deleteDevice.mutate(device.id);
    }
  }

  const activeAccounts = device.social_accounts.filter((a) => a.is_active);

  return (
    <Link href={`/devices/${device.id}`}>
      <Card className={cn("card-hover cursor-pointer h-full")}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            {/* Icon + name */}
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Smartphone className="h-5 w-5" />
              </div>
              <div>
                <p className="font-semibold leading-tight">{device.name}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {activeAccounts.length} account{activeAccounts.length !== 1 ? "s" : ""} connected
                </p>
              </div>
            </div>

            {/* Delete */}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 shrink-0 text-muted-foreground hover:text-destructive"
              onClick={handleDelete}
              loading={deleteDevice.isPending}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent>
          {device.description && (
            <p className="mb-3 text-xs text-muted-foreground line-clamp-2">
              {device.description}
            </p>
          )}

          {/* Connected platforms */}
          <div className="flex flex-wrap gap-1.5">
            {device.social_accounts.length === 0 ? (
              <span className="text-xs text-muted-foreground">No accounts connected</span>
            ) : (
              device.social_accounts.map((account) => (
                <Badge
                  key={account.id}
                  variant={PLATFORM_BADGE[account.platform]}
                  className="gap-1"
                >
                  {PLATFORM_ICON[account.platform]}
                  @{account.username}
                </Badge>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
