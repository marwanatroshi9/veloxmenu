import { api } from "@/lib/api";
import type {
  Category,
  MenuItem,
  Page,
  Restaurant,
  RestaurantStats,
} from "@/types";

// --- Profile ---
export async function getProfile() {
  const { data } = await api.get<Restaurant>("/restaurant/profile");
  return data;
}

export async function updateProfile(payload: Partial<Restaurant>) {
  const { data } = await api.patch<Restaurant>("/restaurant/profile", payload);
  return data;
}

export async function getRestaurantStats() {
  const { data } = await api.get<RestaurantStats>("/restaurant/stats");
  return data;
}

export async function uploadBranding(kind: "logo" | "cover", file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<Restaurant>(`/restaurant/${kind}`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

// --- Categories ---
export async function listCategories() {
  const { data } = await api.get<Category[]>("/restaurant/categories");
  return data;
}

export async function createCategory(payload: Partial<Category>) {
  const { data } = await api.post<Category>("/restaurant/categories", payload);
  return data;
}

export async function updateCategory(id: number, payload: Partial<Category>) {
  const { data } = await api.patch<Category>(`/restaurant/categories/${id}`, payload);
  return data;
}

export async function deleteCategory(id: number) {
  await api.delete(`/restaurant/categories/${id}`);
}

export async function reorderCategories(items: { id: number; sort_order: number }[]) {
  await api.patch("/restaurant/categories/reorder", { items });
}

// --- Menu items ---
export interface MenuItemQuery {
  page?: number;
  page_size?: number;
  search?: string;
  category_id?: number;
  available?: boolean;
  featured?: boolean;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export async function listMenuItems(query: MenuItemQuery = {}) {
  const { data } = await api.get<Page<MenuItem>>("/restaurant/menu-items", {
    params: query,
  });
  return data;
}

export async function createMenuItem(payload: Partial<MenuItem>) {
  const { data } = await api.post<MenuItem>("/restaurant/menu-items", payload);
  return data;
}

export async function updateMenuItem(id: number, payload: Partial<MenuItem>) {
  const { data } = await api.patch<MenuItem>(`/restaurant/menu-items/${id}`, payload);
  return data;
}

export async function deleteMenuItem(id: number) {
  await api.delete(`/restaurant/menu-items/${id}`);
}

export async function duplicateMenuItem(id: number) {
  const { data } = await api.post<MenuItem>(`/restaurant/menu-items/${id}/duplicate`);
  return data;
}

export async function uploadMenuItemImage(id: number, file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<MenuItem>(`/restaurant/menu-items/${id}/image`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export function qrCodeUrl(format: "png" | "svg" | "pdf") {
  return `${api.defaults.baseURL}/restaurant/qrcode?format=${format}`;
}
