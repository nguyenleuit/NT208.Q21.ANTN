"use client";

import { useCallback, useRef, useState } from "react";
import { api, showApiError } from "@/lib/api";
import { toast } from "sonner";

interface UseFileUploadOptions {
  token: string | null;
  sessionId: string | null;
  onSuccess?: () => void;
}

export function useFileUpload({ token, sessionId, onSuccess }: UseFileUploadOptions) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const reset = useCallback(() => {
    setSelectedFile(null);
    setProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, []);

  const upload = useCallback(
    async (file: File) => {
      if (!token || !sessionId) return;
      setIsUploading(true);
      setProgress(30); // simulate start
      try {
        await api.uploadFile(token, sessionId, file);
        setProgress(100);
        toast.success(`Uploaded ${file.name}`);
        reset();
        onSuccess?.();
      } catch (err) {
        showApiError(err);
      } finally {
        setIsUploading(false);
        setProgress(0);
      }
    },
    [token, sessionId, reset, onSuccess],
  );

  const onFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0] ?? null;
      setSelectedFile(file);
      if (file) upload(file);
    },
    [upload],
  );

  const openFilePicker = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return {
    selectedFile,
    isUploading,
    progress,
    fileInputRef,
    onFileChange,
    openFilePicker,
    reset,
    setSelectedFile,
  };
}
