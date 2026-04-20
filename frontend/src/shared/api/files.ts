import { apiFetch, downloadUrl } from "@/shared/api/client";
import type { FileItem } from "@/entities/file/model/types";

export const filesApi = {
  list(): Promise<FileItem[]> {
    return apiFetch<FileItem[]>("/files");
  },

  create(title: string, file: File): Promise<FileItem> {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);
    return apiFetch<FileItem>("/files", { method: "POST", body: formData });
  },

  rename(id: string, title: string): Promise<FileItem> {
    return apiFetch<FileItem>(`/files/${id}`, {
      method: "PATCH",
      body: { title },
    });
  },

  remove(id: string): Promise<void> {
    return apiFetch<void>(`/files/${id}`, { method: "DELETE" });
  },

  downloadUrl(id: string): string {
    return downloadUrl(`/files/${id}/download`);
  },
};
