import { API_URL } from "@/lib/api";
import type { PublicMenuResponse } from "@/types";

/**
 * Fetch a restaurant's public menu. Used by React Server Components, so it uses
 * fetch (not the axios client) to participate in Next.js caching / revalidation.
 */
export async function getPublicMenu(
  slug: string,
  revalidate = 60
): Promise<PublicMenuResponse | null> {
  const res = await fetch(`${API_URL}/public/restaurants/${slug}`, {
    next: { revalidate },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Failed to load menu (${res.status})`);
  return res.json();
}
