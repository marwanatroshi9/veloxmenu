import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getPublicMenu } from "@/services/public.service";
import { PublicMenu } from "@/features/public-menu/public-menu";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const data = await getPublicMenu(slug);
  if (!data) return { title: "Menu not found" };

  const { restaurant } = data;
  const title = restaurant.name;
  const description =
    restaurant.description ?? `Explore the digital menu of ${restaurant.name}.`;
  const images = restaurant.cover_url ? [restaurant.cover_url] : undefined;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      images,
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images,
    },
  };
}

export default async function RestaurantMenuPage({ params }: Props) {
  const { slug } = await params;
  const data = await getPublicMenu(slug);
  if (!data) notFound();

  // Schema.org structured data for rich results.
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    name: data.restaurant.name,
    description: data.restaurant.description ?? undefined,
    image: data.restaurant.cover_url ?? undefined,
    telephone: data.restaurant.phone ?? undefined,
    address: data.restaurant.address ?? undefined,
    servesCuisine: data.categories.map((c) => c.name),
    hasMenu: {
      "@type": "Menu",
      hasMenuSection: data.categories.map((c) => ({
        "@type": "MenuSection",
        name: c.name,
        hasMenuItem: c.items.map((i) => ({
          "@type": "MenuItem",
          name: i.name,
          description: i.description ?? undefined,
          offers: {
            "@type": "Offer",
            price: i.discount_price ?? i.price,
            priceCurrency: data.restaurant.currency,
          },
        })),
      })),
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        // Escape "<" so restaurant/menu text cannot break out of the <script> tag.
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c"),
        }}
      />
      <PublicMenu data={data} />
    </>
  );
}
