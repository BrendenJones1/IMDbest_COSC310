const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type RequestOptions = RequestInit & { token?: string };

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  let payload: any = null;
  try {
    payload = await response.json();
  } catch (error) {
    // ignore parse error for empty responses
  }

  if (!response.ok) {
    const message = payload?.detail ?? payload?.message ?? response.statusText;
    throw new Error(message);
  }

  return payload as T;
}

export interface ApiUser {
  id: string;
  username: string;
  email: string;
  role: string;
  penalties: string[];
  reviews: string[];
  watchlist: string[];
}

export interface AuthResponse {
  token: string;
  user: ApiUser;
}

export async function registerRequest(payload: {
  username: string;
  email: string;
  password: string;
  role?: string;
}): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function loginRequest(payload: {
  email: string;
  password: string;
}): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchCurrentUser(token: string): Promise<ApiUser> {
  return request<ApiUser>("/auth/me", { token });
}
