"use client";

import { LayoutDashboard, Store, UserCog } from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { DashboardShell, type NavItem } from "@/components/dashboard-shell";

const nav: NavItem[] = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard },
  { href: "/admin/restaurants", label: "Restaurants", icon: Store },
  { href: "/admin/account", label: "Account", icon: UserCog },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard role="super_admin">
      <DashboardShell nav={nav} title="MenuHub Admin">
        {children}
      </DashboardShell>
    </AuthGuard>
  );
}
