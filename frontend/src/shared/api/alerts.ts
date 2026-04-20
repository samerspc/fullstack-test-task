import { apiFetch } from "@/shared/api/client";
import type { AlertItem } from "@/entities/alert/model/types";

export const alertsApi = {
  list(): Promise<AlertItem[]> {
    return apiFetch<AlertItem[]>("/alerts");
  },
};
