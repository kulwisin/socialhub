"use client";

import { useState } from "react";
import { FolderPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogHeader } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAddFolder } from "@/hooks/useContent";

export function AddFolderDialog() {
  const [open, setOpen] = useState(false);
  const [path, setPath] = useState("");
  const [label, setLabel] = useState("");
  const addFolder = useAddFolder();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!path.trim() || !label.trim()) return;
    await addFolder.mutateAsync({ path: path.trim(), label: label.trim() });
    setPath("");
    setLabel("");
    setOpen(false);
  };

  return (
    <>
      <Button size="sm" onClick={() => setOpen(true)}>
        <FolderPlus className="mr-2 h-4 w-4" />
        Add folder
      </Button>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogHeader
          title="Add content folder"
          onClose={() => setOpen(false)}
        />
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="folder-path">Folder path</Label>
            <Input
              id="folder-path"
              placeholder="/Users/you/Videos/MyContent"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              required
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="folder-label">Label</Label>
            <Input
              id="folder-label"
              placeholder="My Videos"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              required
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={addFolder.isPending}>
              {addFolder.isPending ? "Adding…" : "Add folder"}
            </Button>
          </div>
        </form>
      </Dialog>
    </>
  );
}
