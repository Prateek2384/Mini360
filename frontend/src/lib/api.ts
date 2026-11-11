export type ApiErrorDetail = { field: string; message: string };

export class ApiError extends Error {
  status: number;
  code: string;
  details: ApiErrorDetail[];

  constructor(status: number, code: string, message: string, details: ApiErrorDetail[] = []) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

type Options = { method?: string; body?: unknown };

export async function api<T>(path: string, options: Options = {}): Promise<T> {
  const hasBody = options.body !== undefined;
  const res = await fetch(`${BASE_URL}${path}`, {
    method: options.method ?? "GET",
    credentials: "include",
    headers: hasBody ? { "Content-Type": "application/json" } : undefined,
    body: hasBody ? JSON.stringify(options.body) : undefined,
  });

  if (res.status === 204) return undefined as T;

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = data?.error;
    throw new ApiError(
      res.status,
      err?.code ?? "unknown_error",
      err?.message ?? `Request failed (${res.status})`,
      err?.details ?? [],
    );
  }
  return data as T;
}

export function apiUrl(path: string): string {
  return `${BASE_URL}${path}`;
}
