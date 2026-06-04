"use client";

import { useState } from "react";
import { Instagram, Facebook, Music2, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { deviceService } from "@/services/device.service";
import { toast } from "sonner";

interface ConnectButtonProps {
  deviceId: string;
}

export function ConnectButton({ deviceId }: ConnectButtonProps) {
  const [loading, setLoading] = useState(false);

  async function handleConnect() {
    setLoading(true);
    try {
      const { url } = await deviceService.getAuthorizeUrl(deviceId);
      // Open in current tab — Meta redirects back to /api/v1/auth/meta/callback
      // which then redirects to /devices/{id}?connected=true
      window.location.href = url;
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to start OAuth");
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-dashed border-border p-6 text-center">
      <div className="mx-auto mb-4 flex items-center justify-center gap-3">
        {/* Platform icons */}
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-pink-500 via-red-500 to-yellow-400 text-white shadow-sm">
          <Instagram className="h-5 w-5" />
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
          <Facebook className="h-5 w-5" />
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gray-800 text-white shadow-sm">
          <Music2 className="h-5 w-5" />
        </div>
      </div>

      <h3 className="font-semibold">Connect social accounts</h3>
      <p className="mt-1 text-sm text-muted-foreground">
        Log in with Meta to link Instagram and Facebook accounts to this device.
        TikTok coming soon.
      </p>

      <Button
        className="mt-5 gap-2"
        onClick={handleConnect}
        loading={loading}
      >
        <ExternalLink className="h-4 w-4" />
        Connect via Meta
      </Button>
    </div>
  );
}
