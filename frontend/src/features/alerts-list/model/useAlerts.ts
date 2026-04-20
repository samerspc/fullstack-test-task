"use client";

import { useCallback, useEffect, useState } from "react";

import { alertsApi } from "@/shared/api/alerts";
import type { AlertItem } from "@/entities/alert/model/types";

export function useAlerts() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    try {
      const data = await alertsApi.list();
      setAlerts(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить алерты");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refetch();
  }, [refetch]);

  return { alerts, isLoading, error, refetch };
}
