import { api } from "@/lib/api";
import { setAccessToken } from "@/lib/token";
import type { TokenResponse, User } from "@/types";

export async function login(email: string, password: string): Promise<User> {
  const { data } = await api.post<TokenResponse>("/auth/login", { email, password });
  setAccessToken(data.access_token);
  return getCurrentUser();
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout");
  } finally {
    setAccessToken(null);
  }
}

export async function changePassword(current_password: string, new_password: string) {
  await api.post("/auth/change-password", { current_password, new_password });
}

export async function changeEmail(current_password: string, new_email: string): Promise<User> {
  const { data } = await api.post<User>("/auth/change-email", {
    current_password,
    new_email,
  });
  return data;
}

/** Attempt to restore a session from the refresh cookie (called on app load). */
export async function restoreSession(): Promise<User | null> {
  try {
    const { data } = await api.post<TokenResponse>("/auth/refresh", {});
    setAccessToken(data.access_token);
    return getCurrentUser();
  } catch {
    setAccessToken(null);
    return null;
  }
}
