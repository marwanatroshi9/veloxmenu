"use client";

import { useQuery } from "@tanstack/react-query";
import { Store, UtensilsCrossed, Users, CreditCard, HardDrive, CheckCircle2 } from "lucide-react";
import { StatCard } from "@/components/stat-card";
import { getSuperAdminStats } from "@/services/admin.service";
import { formatBytes } from "@/lib/utils";

export default function AdminHome() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: getSuperAdminStats,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Platform overview</h1>
        <p className="text-muted-foreground">Key metrics across all restaurants.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard label="Restaurants" value={data?.total_restaurants ?? 0} icon={Store} loading={isLoading} />
        <StatCard label="Active" value={data?.active_restaurants ?? 0} icon={CheckCircle2} loading={isLoading} />
        <StatCard label="Menu items" value={data?.total_menu_items ?? 0} icon={UtensilsCrossed} loading={isLoading} />
        <StatCard label="Managers" value={data?.total_managers ?? 0} icon={Users} loading={isLoading} />
        <StatCard label="Active subscriptions" value={data?.active_subscriptions ?? 0} icon={CreditCard} loading={isLoading} />
        <StatCard label="Storage used" value={formatBytes(data?.storage_bytes ?? 0)} icon={HardDrive} loading={isLoading} />
      </div>
    </div>
  );
}
