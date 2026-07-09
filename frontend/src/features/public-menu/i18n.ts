import type { Translations } from "@/types";

export const MENU_LANGUAGES = [
  { code: "en", label: "English" },
  { code: "ar", label: "العربية" },
  { code: "ckb", label: "کوردی" },
] as const;

export const RTL_LANGS = new Set(["ar", "ckb", "fa", "ur", "he"]);

export function isRtl(lang: string): boolean {
  return RTL_LANGS.has(lang);
}

/** Resolve a translated field, falling back to the base (primary language) value. */
export function tr(
  base: string | null | undefined,
  translations: Translations | undefined,
  lang: string,
  field: "name" | "description"
): string {
  const value = translations?.[lang]?.[field];
  if (value && value.trim()) return value;
  return base ?? "";
}

type UiKey =
  | "favorites"
  | "featured"
  | "search"
  | "min"
  | "all"
  | "poweredBy"
  | "noResults";

const UI: Record<string, Record<UiKey, string>> = {
  en: {
    favorites: "Favorites",
    featured: "Featured",
    search: "Search the menu…",
    min: "min",
    all: "All",
    poweredBy: "Powered by MenuHub",
    noResults: "No items match your search.",
  },
  ar: {
    favorites: "المفضلة",
    featured: "المميزة",
    search: "ابحث في القائمة…",
    min: "دقيقة",
    all: "الكل",
    poweredBy: "مدعوم من MenuHub",
    noResults: "لا توجد عناصر مطابقة لبحثك.",
  },
  ckb: {
    favorites: "دڵخوازەکان",
    featured: "تایبەت",
    search: "لە مێنیو بگەڕێ…",
    min: "خولەک",
    all: "هەموو",
    poweredBy: "پشتگیریکراوە لەلایەن MenuHub",
    noResults: "هیچ شتێک نەدۆزرایەوە.",
  },
};

export function ui(lang: string, key: UiKey): string {
  return (UI[lang] ?? UI.en)[key];
}
