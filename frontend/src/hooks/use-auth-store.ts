import { create } from "zustand";
import type { User } from "@/types";
import * as authService from "@/services/auth.service";

interface AuthState {
  user: User | null;
  status: "idle" | "loading" | "authenticated" | "unauthenticated";
  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  restore: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  status: "idle",

  login: async (email, password) => {
    set({ status: "loading" });
    const user = await authService.login(email, password);
    set({ user, status: "authenticated" });
    return user;
  },

  logout: async () => {
    await authService.logout();
    set({ user: null, status: "unauthenticated" });
  },

  restore: async () => {
    set({ status: "loading" });
    const user = await authService.restoreSession();
    set({ user, status: user ? "authenticated" : "unauthenticated" });
  },

  setUser: (user) => set({ user, status: user ? "authenticated" : "unauthenticated" }),
}));
