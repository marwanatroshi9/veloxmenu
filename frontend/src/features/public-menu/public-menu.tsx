"use client";

import { useMemo, useRef, useState } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { Search, Heart, Globe, ChevronDown, LayoutGrid, Flame, Clock, X, Check } from "lucide-react";
import { cn, formatCurrency } from "@/lib/utils";
import { iconForCategory } from "@/features/menu-icons";
import { MENU_LANGUAGES, isRtl, tr, ui } from "./i18n";
import type { PublicMenuItem, PublicMenuResponse, Translations } from "@/types";

export function PublicMenu({ data }: { data: PublicMenuResponse }) {
  const { restaurant, categories } = data;
  const accent = restaurant.theme_color || "#F5333F";

  const [lang, setLang] = useState<string>(restaurant.default_language || "en");
  const [langOpen, setLangOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [featuredOnly, setFeaturedOnly] = useState(false);
  const [active, setActive] = useState<number | null>(categories[0]?.id ?? null);
  const sectionRefs = useRef<Record<number, HTMLElement | null>>({});

  const rtl = isRtl(lang);

  const sections = useMemo(() => {
    const q = query.trim().toLowerCase();
    return categories
      .map((c) => ({
        ...c,
        items: c.items.filter((i) => {
          if (featuredOnly && !i.is_featured) return false;
          if (!q) return true;
          const name = tr(i.name, i.translations, lang, "name").toLowerCase();
          const desc = tr(i.description, i.translations, lang, "description").toLowerCase();
          return name.includes(q) || desc.includes(q) || i.tags.some((t) => t.toLowerCase().includes(q));
        }),
      }))
      .filter((c) => c.items.length > 0);
  }, [categories, query, featuredOnly, lang]);

  function scrollTo(id: number) {
    setActive(id);
    sectionRefs.current[id]?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  const style = { ["--accent" as string]: accent } as React.CSSProperties;
  const activeLangLabel = MENU_LANGUAGES.find((l) => l.code === lang)?.label ?? lang;

  return (
    <div dir={rtl ? "rtl" : "ltr"} style={style} className="min-h-screen bg-[#0b0b0d] text-white">
      {/* Top bar */}
      <header className="sticky top-0 z-20 bg-[#0b0b0d]/90 pt-[env(safe-area-inset-top)] backdrop-blur">
        <div className="mx-auto flex w-full max-w-2xl items-center justify-between px-4 py-4 sm:px-6 lg:max-w-5xl">
          <LayoutGrid className="h-6 w-6 shrink-0" />
          <div className="flex min-w-0 items-center gap-2 px-3">
            {restaurant.logo_url && (
              <Image
                src={restaurant.logo_url}
                alt=""
                width={28}
                height={28}
                className="h-7 w-7 shrink-0 rounded-full object-cover"
              />
            )}
            <h1 className="truncate text-center text-base font-semibold sm:text-lg">
              {restaurant.name}
            </h1>
          </div>
          <button
            aria-label={searchOpen ? "Close search" : "Search"}
            onClick={() => {
              if (searchOpen) setQuery("");
              setSearchOpen((v) => !v);
            }}
            className="transition-opacity hover:opacity-70"
          >
            {searchOpen ? <X className="h-6 w-6" /> : <Search className="h-6 w-6" />}
          </button>
        </div>

        {/* Search field */}
        {searchOpen && (
          <div className="mx-auto w-full max-w-2xl px-4 pb-3 sm:px-6 lg:max-w-5xl">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 opacity-60" />
              <input
                autoFocus
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={ui(lang, "search")}
                className="h-11 w-full rounded-xl border border-white/10 bg-white/5 px-9 text-sm text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
              />
            </div>
          </div>
        )}

        {/* Action pills */}
        <div className="mx-auto flex w-full max-w-2xl gap-3 px-4 pb-4 sm:px-6 lg:max-w-5xl">
          <button
            onClick={() => setFeaturedOnly((v) => !v)}
            className={cn(
              "flex h-12 flex-1 items-center justify-center gap-2 rounded-2xl font-medium transition-transform active:scale-[0.98]",
              featuredOnly ? "ring-2 ring-white/70" : ""
            )}
            style={{ backgroundColor: accent }}
          >
            <Heart className={cn("h-5 w-5", featuredOnly && "fill-current")} />
            {featuredOnly ? ui(lang, "featured") : ui(lang, "favorites")}
          </button>

          {/* Language switcher */}
          <div className="relative flex-1">
            <button
              onClick={() => setLangOpen((v) => !v)}
              aria-haspopup="listbox"
              aria-expanded={langOpen}
              className="flex h-12 w-full items-center justify-center gap-2 rounded-2xl font-medium"
              style={{ backgroundColor: accent }}
            >
              <Globe className="h-5 w-5" />
              <span>{activeLangLabel}</span>
              <ChevronDown className={cn("h-4 w-4 transition-transform", langOpen && "rotate-180")} />
            </button>
            {langOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setLangOpen(false)} />
                <ul
                  role="listbox"
                  className="absolute z-20 mt-2 w-full overflow-hidden rounded-xl border border-white/10 bg-[#16161a] shadow-xl"
                >
                  {MENU_LANGUAGES.map((l) => (
                    <li key={l.code}>
                      <button
                        role="option"
                        aria-selected={lang === l.code}
                        onClick={() => {
                          setLang(l.code);
                          setLangOpen(false);
                        }}
                        className="flex w-full items-center justify-between px-4 py-2.5 text-sm hover:bg-white/10"
                      >
                        {l.label}
                        {lang === l.code && <Check className="h-4 w-4" style={{ color: accent }} />}
                      </button>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </div>

        {/* Category icon rail */}
        <nav className="mx-auto w-full max-w-2xl overflow-x-auto px-4 pb-4 sm:px-6 lg:max-w-5xl [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          <ul className="flex gap-6 sm:gap-7">
            {categories.map((c) => {
              const Icon = iconForCategory(c.name, c.icon);
              const isActive = active === c.id;
              return (
                <li key={c.id}>
                  <button
                    onClick={() => scrollTo(c.id)}
                    className="flex w-16 flex-col items-center gap-2 transition-opacity"
                    style={{ opacity: isActive ? 1 : 0.6, color: isActive ? accent : "#fff" }}
                  >
                    {c.image_url ? (
                      <Image
                        src={c.image_url}
                        alt=""
                        width={44}
                        height={44}
                        className="h-11 w-11 rounded-full object-cover"
                      />
                    ) : (
                      <Icon className="h-9 w-9" strokeWidth={1.5} />
                    )}
                    <span className="w-full truncate text-center text-xs font-medium">
                      {tr(c.name, c.translations, lang, "name")}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </header>

      {/* Sections */}
      <main className="mx-auto w-full max-w-2xl space-y-8 px-4 py-6 sm:px-6 lg:max-w-5xl">
        {sections.length === 0 && (
          <p className="py-20 text-center text-white/50">{ui(lang, "noResults")}</p>
        )}
        {sections.map((section) => (
          <section
            key={section.id}
            id={`sec-${section.id}`}
            ref={(el) => {
              sectionRefs.current[section.id] = el;
            }}
            className="scroll-mt-52 sm:scroll-mt-56"
          >
            <SectionTitle title={tr(section.name, section.translations, lang, "name")} />
            <div className="grid grid-cols-1 gap-4 sm:gap-5 lg:grid-cols-2">
              {section.items.map((item) => (
                <ItemCard
                  key={item.id}
                  item={item}
                  accent={accent}
                  currency={restaurant.currency}
                  lang={lang}
                />
              ))}
            </div>
          </section>
        ))}
      </main>

      <footer className="pb-[max(2.5rem,env(safe-area-inset-bottom))] pt-4 text-center text-xs text-white/40">
        {ui(lang, "poweredBy")}
      </footer>
    </div>
  );
}

function SectionTitle({ title }: { title: string }) {
  return (
    <div className="mb-5 flex items-center gap-3">
      <LayoutGrid className="h-5 w-5 shrink-0 opacity-80" />
      <span className="h-px flex-1 bg-white/15" />
      <h2 className="text-center text-lg font-bold tracking-wide">{title}</h2>
      <span className="h-px flex-1 bg-white/15" />
    </div>
  );
}

function Price({
  item,
  currency,
  locale,
}: {
  item: PublicMenuItem;
  currency: string;
  locale: string;
}) {
  if (item.discount_price) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-lg font-semibold">
          {formatCurrency(item.discount_price, currency, locale)}
        </span>
        <span className="text-sm text-white/60 line-through">
          {formatCurrency(item.price, currency, locale)}
        </span>
      </div>
    );
  }
  return (
    <span className="text-lg font-semibold">{formatCurrency(item.price, currency, locale)}</span>
  );
}

function ItemCard({
  item,
  accent,
  currency,
  lang,
}: {
  item: PublicMenuItem;
  accent: string;
  currency: string;
  lang: string;
}) {
  const hasImage = Boolean(item.image_url);
  const name = tr(item.name, item.translations, lang, "name");
  const description = tr(item.description, item.translations, lang, "description");
  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.35 }}
      className={cn(
        "grid min-h-[170px] overflow-hidden rounded-3xl text-white shadow-lg sm:min-h-[190px]",
        hasImage ? "grid-cols-[1fr_42%] sm:grid-cols-[1fr_44%]" : "grid-cols-1"
      )}
      style={{ backgroundColor: accent }}
    >
      <div className="flex flex-col justify-center gap-1.5 p-4 sm:gap-2 sm:p-5">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-bold leading-tight sm:text-xl">{name}</h3>
          {item.spicy_level > 0 && (
            <span className="flex text-white/90" title={`Spicy ${item.spicy_level}/4`}>
              {Array.from({ length: item.spicy_level }).map((_, i) => (
                <Flame key={i} className="h-4 w-4" />
              ))}
            </span>
          )}
        </div>
        <Price item={item} currency={currency} locale={lang} />
        {description && (
          <p className="line-clamp-3 text-sm leading-relaxed text-white/85">{description}</p>
        )}
        {item.preparation_time != null && (
          <span className="mt-1 inline-flex w-fit items-center gap-1 text-xs text-white/70">
            <Clock className="h-3.5 w-3.5" /> {item.preparation_time} {ui(lang, "min")}
          </span>
        )}
      </div>

      {hasImage && (
        <div className="relative p-3">
          <div className="relative h-full w-full overflow-hidden rounded-2xl">
            <Image
              src={item.image_url as string}
              alt={name}
              fill
              sizes="(max-width: 768px) 44vw, 300px"
              loading="lazy"
              className="object-cover"
            />
          </div>
        </div>
      )}
    </motion.article>
  );
}
