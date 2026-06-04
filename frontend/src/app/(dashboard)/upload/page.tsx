"use client";

import { Film } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { UploadDropzone } from "@/features/upload/UploadDropzone";
import { UploadCard } from "@/features/upload/UploadCard";
import { useUploads } from "@/hooks/useUploads";

export default function UploadPage() {
  const { data: uploads, isLoading } = useUploads(20);

  return (
    <>
      <Header
        title="Upload Studio"
        description="Upload a video or image, add a caption, then publish to any connected account."
      />

      <div className="flex-1 space-y-8 p-8">
        {/* Drop zone */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">New upload</CardTitle>
          </CardHeader>
          <CardContent>
            <UploadDropzone />
          </CardContent>
        </Card>

        {/* Library */}
        <div>
          <h2 className="mb-4 text-sm font-medium uppercase tracking-wider text-muted-foreground">
            Your uploads
          </h2>

          {isLoading ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-72 w-full rounded-xl" />
              ))}
            </div>
          ) : !uploads?.length ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-16 text-center">
              <Film className="mb-3 h-10 w-10 text-muted-foreground/40" />
              <p className="font-medium">No uploads yet</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Drop a video or image above to get started.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {uploads.map((upload) => (
                <UploadCard key={upload.id} upload={upload} />
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
