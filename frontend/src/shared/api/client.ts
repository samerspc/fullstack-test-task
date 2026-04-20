import { API_URL } from "@/shared/config/env";

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: BodyInit | object | null;
  json?: boolean;
};

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, json = true, headers, ...rest } = options;

  const init: RequestInit = {
    cache: "no-store",
    ...rest,
    headers: {
      ...(json && body && !(body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
      ...(headers ?? {}),
    },
    body:
      body == null
        ? undefined
        : body instanceof FormData || typeof body === "string"
          ? (body as BodyInit)
          : JSON.stringify(body),
  };

  const response = await fetch(`${API_URL}${path}`, init);

  if (!response.ok) {
    const detail = await safeDetail(response);
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function safeDetail(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string };
    if (typeof data.detail === "string") return data.detail;
  } catch {
    // Ignore JSON parse errors, fall through to status text.
  }
  return response.statusText || `HTTP ${response.status}`;
}

export function downloadUrl(path: string): string {
  return `${API_URL}${path}`;
}
