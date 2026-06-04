"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Dialog, DialogHeader } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useCreateDevice } from "@/hooks/useDevices";

const schema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  description: z.string().max(500).optional(),
});

type FormValues = z.infer<typeof schema>;

interface CreateDeviceModalProps {
  open: boolean;
  onClose: () => void;
}

export function CreateDeviceModal({ open, onClose }: CreateDeviceModalProps) {
  const createDevice = useCreateDevice();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    await createDevice.mutateAsync(values);
    reset();
    onClose();
  }

  function handleClose() {
    reset();
    onClose();
  }

  return (
    <Dialog open={open} onClose={handleClose}>
      <DialogHeader
        title="New Device"
        description="A device holds social accounts for one brand or identity."
        onClose={handleClose}
      />

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="name">Device name</Label>
          <Input
            id="name"
            placeholder="My Brand, Client A, Personal..."
            {...register("name")}
          />
          {errors.name && (
            <p className="text-xs text-destructive">{errors.name.message}</p>
          )}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="description">Description (optional)</Label>
          <Textarea
            id="description"
            placeholder="What's this device for?"
            rows={3}
            {...register("description")}
          />
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button type="submit" loading={createDevice.isPending}>
            Create Device
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
