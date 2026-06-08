"use client";

import { useState } from "react";
import { Library } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Skeleton } from "@/components/ui/skeleton";
import { AddFolderDialog } from "@/features/content/AddFolderDialog";
import { AnalysisPanel } from "@/features/content/AnalysisPanel";
import { FileTable } from "@/features/content/FileTable";
import { FolderCard } from "@/features/content/FolderCard";
import { useContentFiles, useContentFolders } from "@/hooks/useContent";
import type { ContentFile } from "@/types";

export default function ContentPage() {
  const [selectedFolderId, setSelectedFolderId] = useState<string | undefined>();
  const [selectedFile, setSelectedFile] = useState<ContentFile | null>(null);

  const { data: folders, isLoading: foldersLoading } = useContentFolders();
  const { data: files, isLoading: filesLoading } = useContentFiles(selectedFolderId);

  const handleSelectFolder = (id: string) => {
    setSelectedFolderId((prev) => (prev === id ? undefined : id));
    setSelectedFile(null);
  };

  const handleSelectFile = (file: ContentFile) => {
    setSelectedFile((prev) => (prev?.id === file.id ? null : file));
  };

  return (
    <>
      <Header
        title="Content Library"
        description="Manage video and audio files. Scan folders, analyze with Claude AI, generate platform copy."
        action={<AddFolderDialog />}
      />

      <div className="flex-1 space-y-8 p-8">
        {/* Folders */}
        <section>
          <h2 className="mb-4 text-sm font-medium uppercase tracking-wider text-muted-foreground">
            Watched folders
          </h2>

          {foldersLoading ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-40 w-full rounded-xl" />
              ))}
            </div>
          ) : !folders?.length ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-12 text-center">
              <Library className="mb-3 h-10 w-10 text-muted-foreground/40" />
              <p className="font-medium">No folders yet</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Click &ldquo;Add folder&rdquo; above to register a directory to
                scan.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
              {folders.map((folder) => (
                <FolderCard
                  key={folder.id}
                  folder={folder}
                  onSelect={handleSelectFolder}
                  isSelected={folder.id === selectedFolderId}
                />
              ))}
            </div>
          )}
        </section>

        {/* Files + Analysis panel side by side */}
        <section>
          <h2 className="mb-4 text-sm font-medium uppercase tracking-wider text-muted-foreground">
            {selectedFolderId
              ? `Files in "${
                  folders?.find((f) => f.id === selectedFolderId)?.label ??
                  "folder"
                }"`
              : "All files"}
          </h2>

          <div
            className={`flex gap-6 ${selectedFile ? "items-start" : ""}`}
          >
            <div className={selectedFile ? "flex-1 min-w-0" : "w-full"}>
              <FileTable
                files={files}
                isLoading={filesLoading}
                onSelectFile={handleSelectFile}
                selectedFileId={selectedFile?.id}
              />
            </div>

            {selectedFile && (
              <div className="w-96 shrink-0">
                <AnalysisPanel
                  file={selectedFile}
                  onClose={() => setSelectedFile(null)}
                />
              </div>
            )}
          </div>
        </section>
      </div>
    </>
  );
}
