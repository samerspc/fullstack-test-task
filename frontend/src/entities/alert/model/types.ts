export type AlertLevel = "info" | "warning" | "critical";

export type AlertItem = {
  id: number;
  file_id: string;
  level: AlertLevel | string;
  message: string;
  created_at: string;
};
