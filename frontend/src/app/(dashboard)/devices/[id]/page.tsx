"use client";

import { use, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, Plus } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { AccountCard } from "@/features/accounts/AccountCard";
import { ConnectButton } from "@/features/accounts/ConnectButton";
import { useDevice } from "@/hooks/useDevices";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function DeviceDetailPage({ params }: PageProps) {
  const { id } = use(params);
  const { data: device, isLoading, isError } = useDevice(id);
  const searchParams = useSearchParams();

  // Show success toast when redirected back from OAuth
  useEffect(() => {
    if (searchParams.get("connected") === "true") {
      toast.success("Accounts connected successfully!");
      // Clean URL without reload
      window.history.replaceState({}, "", `/devices/${id}`);
    }
  }, [id, searchParams]);

  return (
    <>
      <Header
        title={device?.name ?? "Device"}
        description={device?.description ?? "Manage connected social accounts"}
        action={
          <Link href="/devices">
            <Button variant="outline" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              All devices
            </Button>
          </Link>
        }
      />

      <div className="flex-1 space-y-8 p-8">
        {isLoading && (
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            {[1, 2].map((i) => (
              <Skeleton key={i} className="h-52 w-full rounded-xl" />
            ))}
          </div>
        )}

        {isError && (
          <p className="text-center text-sm text-destructive">
            Device not found or failed to load.
          </p>
        )}

        {!isLoading && !isError && device && (
          <>
            {/* Connected accounts grid */}
            {device.social_accounts.length > 0 && (
              <div>
                <h2 className="mb-4 text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  Connected accounts
                </h2>
                <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                  {device.social_accounts.map((account) => (
                    <AccountCard
                      key={account.id}
                      account={account as any}
                      deviceId={device.id}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Connect new account */}
            <div>
              <h2 className="mb-4 text-sm font-medium text-muted-foreground uppercase tracking-wider">
                {device.social_accounts.length > 0 ? "Add another account" : "Connect an account"}
              </h2>
              <ConnectButton deviceId={device.id} />
            </div>
          </>
        )}
      </div>
    </>
  );
}
