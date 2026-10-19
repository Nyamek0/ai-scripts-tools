"use client";

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_superadmin: boolean;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
}

export function saveAuth(token: string, user: User, rememberMe: boolean): void {
  if (rememberMe) {
    localStorage.setItem("access_token", token);
    localStorage.setItem("user", JSON.stringify(user));
  } else {
    sessionStorage.setItem("access_token", token);
    sessionStorage.setItem("user", JSON.stringify(user));
  }
}

export function getAuth(): AuthState {
  if (typeof window === "undefined") return { user: null, token: null };

  const token =
    localStorage.getItem("access_token") ||
    sessionStorage.getItem("access_token");
  const userStr =
    localStorage.getItem("user") ||
    sessionStorage.getItem("user");

  const user = userStr ? (JSON.parse(userStr) as User) : null;
  return { user, token };
}

export function clearAuth(): void {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("user");
}

export function isAuthenticated(): boolean {
  const { token } = getAuth();
  return !!token;
}
