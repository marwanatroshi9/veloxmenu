import { api } from "@/lib/api";
import type {
  Page,
  Restaurant,
  RestaurantStatus,
  RestaurantSummary,
  SuperAdminStats,
} from "@/types";

export async function getSuperAdminStats() {
  const { data } = await api.get<SuperAdminStats>("/admin/stats");
  return data;
}

export interface RestaurantQuery {
  page?: number;
  page_size?: number;
  search?: string;
  status?: RestaurantStatus;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export async function listRestaurants(query: RestaurantQuery = {}) {
  const { data } = await api.get<Page<RestaurantSummary>>("/admin/restaurants", {
    params: query,
  });
  return data;
}

export interface CreateRestaurantPayload {
  name: string;
  slug?: string;
  description?: string;
  manager_email: string;
  manager_password: string;
  manager_full_name?: string;
}

export async function createRestaurant(payload: CreateRestaurantPayload) {
  const { data } = await api.post<Restaurant>("/admin/restaurants", payload);
  return data;
}

export async function getRestaurant(id: number) {
  const { data } = await api.get<Restaurant>(`/admin/restaurants/${id}`);
  return data;
}

export async function updateRestaurant(id: number, payload: Partial<Restaurant>) {
  const { data } = await api.patch<Restaurant>(`/admin/restaurants/${id}`, payload);
  return data;
}

export async function deleteRestaurant(id: number) {
  await api.delete(`/admin/restaurants/${id}`);
}

export async function suspendRestaurant(id: number) {
  const { data } = await api.post<Restaurant>(`/admin/restaurants/${id}/suspend`);
  return data;
}

export async function activateRestaurant(id: number) {
  const { data } = await api.post<Restaurant>(`/admin/restaurants/${id}/activate`);
  return data;
}

export async function resetManagerPassword(id: number) {
  const { data } = await api.post<{ manager_email: string; temporary_password: string }>(
    `/admin/restaurants/${id}/reset-manager-password`
  );
  return data;
}
