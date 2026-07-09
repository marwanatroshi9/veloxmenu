"use client";

import {
  LayoutDashboard,
  Store,
  FolderTree,
  UtensilsCrossed,
  QrCode,
  UserCog,
} from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";
import { DashboardShell, type NavItem } from "@/components/dashboard-shell";

const nav: NavItem[] = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/profile", label: "Profile", icon: Store },
  { href: "/dashboard/categories", label: "Categories", icon: FolderTree },
  { href: "/dashboard/menu", label: "Menu Items", icon: UtensilsCrossed },
  { href: "/dashboard/qrcode", label: "QR Code", icon: QrCode },
  { href: "/dashboard/account", label: "Account", icon: UserCog },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard role="restaurant_manager">
      <DashboardShell nav={nav} title="MenuHub">
        {children}
      </DashboardShell>
    </AuthGuard>
  );
}
