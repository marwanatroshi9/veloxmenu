"use client";

import { useQuery } from "@tanstack/react-query";
import { FolderTree, UtensilsCrossed, Star, HardDrive } from "lucide-react";
import { StatCard } from "@/components/stat-card";
import { getRestaurantStats, getProfile } from "@/services/restaurant.service";
import { formatBytes } from "@/lib/utils";

export default function DashboardHome() {
  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: getProfile });
  const { data: stats, isLoading } = useQuery({
    queryKey: ["restaurant-stats"],
    queryFn: getRestaurantStats,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          {profile ? profile.name : "Overview"}
        </h1>
        <p className="text-muted-foreground">Here is how your menu is doing.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Categories"
          value={stats?.total_categories ?? 0}
          icon={FolderTree}
          loading={isLoading}
        />
        <StatCard
          label="Menu items"
          value={stats?.total_menu_items ?? 0}
          icon={UtensilsCrossed}
          loading={isLoading}
        />
        <StatCard
          label="Featured"
          value={stats?.featured_items ?? 0}
          icon={Star}
          loading={isLoading}
        />
        <StatCard
          label="Storage used"
          value={formatBytes(stats?.storage_bytes ?? 0)}
          icon={HardDrive}
          loading={isLoading}
        />
      </div>
    </div>
  );
}
