"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuthStore } from "@/hooks/use-auth-store";
import type { UserRole } from "@/types";

/**
 * Client-side route guard. On mount it restores the session from the refresh
 * cookie; it redirects to /login when unauthenticated and enforces the required
 * role. Server-side data access is independently protected by the API — this
 * guard is a UX layer, not the security boundary.
 */
export function AuthGuard({
  role,
  children,
}: {
  role: UserRole;
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, status, restore } = useAuthStore();

  useEffect(() => {
    if (status === "idle") void restore();
  }, [status, restore]);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    } else if (status === "authenticated" && user && user.role !== role) {
      router.replace(user.role === "super_admin" ? "/admin" : "/dashboard");
    }
  }, [status, user, role, router]);

  if (status !== "authenticated" || !user || user.role !== role) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return <>{children}</>;
}
