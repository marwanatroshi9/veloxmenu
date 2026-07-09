export interface TranslatedText {
  name?: string | null;
  description?: string | null;
}
/** Map of language code ("ar" | "ckb") to translated fields. */
export type Translations = Record<string, TranslatedText>;

export type UserRole = "super_admin" | "restaurant_manager";
export type RestaurantStatus = "active" | "suspended";
export type SubscriptionPlan = "free" | "basic" | "pro" | "enterprise";
export type SubscriptionStatus = "active" | "trialing" | "past_due" | "canceled";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  restaurant_id: number | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface Restaurant {
  id: number;
  name: string;
  slug: string;
  status: RestaurantStatus;
  description: string | null;
  logo_url: string | null;
  cover_url: string | null;
  theme_color: string;
  phone: string | null;
  whatsapp: string | null;
  instagram: string | null;
  facebook: string | null;
  tiktok: string | null;
  website: string | null;
  address: string | null;
  google_maps_url: string | null;
  opening_hours: string | null;
  currency: string;
  default_language: string;
  created_at: string;
}

export interface RestaurantSummary {
  id: number;
  name: string;
  slug: string;
  status: RestaurantStatus;
  logo_url: string | null;
  created_at: string;
}

export interface Category {
  id: number;
  restaurant_id: number;
  name: string;
  description: string | null;
  image_url: string | null;
  icon: string | null;
  translations: Translations;
  is_visible: boolean;
  sort_order: number;
  created_at: string;
}

export type SpicyLevel = 0 | 1 | 2 | 3 | 4;

export interface MenuItem {
  id: number;
  restaurant_id: number;
  category_id: number;
  name: string;
  description: string | null;
  image_url: string | null;
  price: string;
  discount_price: string | null;
  is_available: boolean;
  is_featured: boolean;
  preparation_time: number | null;
  calories: number | null;
  spicy_level: SpicyLevel;
  ingredients: string[];
  tags: string[];
  translations: Translations;
  sort_order: number;
  created_at: string;
}

export interface PageMeta {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Page<T> {
  items: T[];
  meta: PageMeta;
}

export interface SuperAdminStats {
  total_restaurants: number;
  active_restaurants: number;
  suspended_restaurants: number;
  total_menu_items: number;
  total_categories: number;
  total_managers: number;
  active_subscriptions: number;
  storage_bytes: number;
}

export interface RestaurantStats {
  total_categories: number;
  visible_categories: number;
  total_menu_items: number;
  available_items: number;
  featured_items: number;
  storage_bytes: number;
}

// Public menu shapes
export interface PublicMenuItem {
  id: number;
  name: string;
  description: string | null;
  image_url: string | null;
  price: string;
  discount_price: string | null;
  is_featured: boolean;
  preparation_time: number | null;
  calories: number | null;
  spicy_level: SpicyLevel;
  ingredients: string[];
  tags: string[];
  translations: Translations;
}

export interface PublicCategory {
  id: number;
  name: string;
  description: string | null;
  image_url: string | null;
  icon: string | null;
  translations: Translations;
  items: PublicMenuItem[];
}

export interface PublicMenuResponse {
  restaurant: Restaurant;
  categories: PublicCategory[];
  featured: PublicMenuItem[];
}
