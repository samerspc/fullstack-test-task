"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { filesApi } from "@/shared/api/files";
import { type FileItem, isInProgress } from "@/entities/file/model/types";

const POLL_INTERVAL_MS = 2000;

export function useFiles() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const refetch = useCallback(async () => {
    try {
      const data = await filesApi.list();
      setFiles(data);
      setError(null);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить файлы");
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refetch();
  }, [refetch]);

  useEffect(() => {
    if (!files.some(isInProgress)) return;
    timerRef.current = setTimeout(() => {
      void refetch();
    }, POLL_INTERVAL_MS);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [files, refetch]);

  return { files, isLoading, error, refetch };
}
