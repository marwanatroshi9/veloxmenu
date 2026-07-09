import {
  Coffee,
  CupSoda,
  GlassWater,
  Milk,
  Beer,
  Wine,
  Martini,
  Cake,
  Cookie,
  Croissant,
  Donut,
  IceCream2,
  Pizza,
  Sandwich,
  Salad,
  Soup,
  Fish,
  Beef,
  Drumstick,
  Egg,
  Popcorn,
  Apple,
  Flame,
  Leaf,
  Utensils,
  type LucideIcon,
} from "lucide-react";

export interface IconOption {
  key: string;
  label: string;
  Icon: LucideIcon;
}

/** The curated set of icons a manager can assign to a category. */
export const ICON_OPTIONS: IconOption[] = [
  { key: "coffee", label: "Coffee", Icon: Coffee },
  { key: "cold-cup", label: "Cold cup", Icon: CupSoda },
  { key: "juice", label: "Juice", Icon: GlassWater },
  { key: "milk", label: "Milkshake", Icon: Milk },
  { key: "beer", label: "Beer", Icon: Beer },
  { key: "wine", label: "Wine", Icon: Wine },
  { key: "cocktail", label: "Cocktail", Icon: Martini },
  { key: "dessert", label: "Dessert", Icon: Cake },
  { key: "cookie", label: "Cookie", Icon: Cookie },
  { key: "croissant", label: "Bakery", Icon: Croissant },
  { key: "donut", label: "Donut", Icon: Donut },
  { key: "icecream", label: "Ice cream", Icon: IceCream2 },
  { key: "pizza", label: "Pizza", Icon: Pizza },
  { key: "burger", label: "Burger", Icon: Sandwich },
  { key: "sandwich", label: "Sandwich", Icon: Sandwich },
  { key: "salad", label: "Salad", Icon: Salad },
  { key: "soup", label: "Soup", Icon: Soup },
  { key: "fish", label: "Seafood", Icon: Fish },
  { key: "meat", label: "Grill", Icon: Beef },
  { key: "chicken", label: "Chicken", Icon: Drumstick },
  { key: "breakfast", label: "Breakfast", Icon: Egg },
  { key: "snacks", label: "Snacks", Icon: Popcorn },
  { key: "fruit", label: "Fruit", Icon: Apple },
  { key: "spicy", label: "Spicy", Icon: Flame },
  { key: "vegan", label: "Vegan", Icon: Leaf },
  { key: "other", label: "Other", Icon: Utensils },
];

const BY_KEY: Record<string, LucideIcon> = Object.fromEntries(
  ICON_OPTIONS.map((o) => [o.key, o.Icon])
);

export function iconByKey(key?: string | null): LucideIcon | null {
  return key ? BY_KEY[key] ?? null : null;
}

// Fallback: infer an icon from the category name when none was chosen.
const NAME_RULES: [RegExp, string][] = [
  [/frapp|iced|ice|cold/, "cold-cup"],
  [/latte|cappuc|espresso|coffee|mocha|americano|turkish|tea|hot\s*drink|chocolate/, "coffee"],
  [/juice|smoothie|water|soft|soda|lemonade/, "juice"],
  [/milk|shake/, "milk"],
  [/beer|draft/, "beer"],
  [/wine|cocktail|spirit/, "cocktail"],
  [/dessert|cake|sweet|pastr/, "dessert"],
  [/cookie|biscuit/, "cookie"],
  [/croissant|bakery/, "croissant"],
  [/donut/, "donut"],
  [/scoop|gelato|cream/, "icecream"],
  [/pizza/, "pizza"],
  [/burger/, "burger"],
  [/sandwich|wrap|toast/, "sandwich"],
  [/salad|veg|green/, "salad"],
  [/soup|starter|appetizer|meze/, "soup"],
  [/fish|seafood|sushi/, "fish"],
  [/meat|grill|steak|bbq|kebab|shawarma/, "meat"],
  [/chicken|wing/, "chicken"],
  [/breakfast|egg|omelet/, "breakfast"],
  [/snack|chips|fries|popcorn/, "snacks"],
  [/fruit|apple/, "fruit"],
  [/shisha|hookah|spicy/, "spicy"],
  [/vegan|healthy/, "vegan"],
  [/drink|beverage/, "cold-cup"],
];

export function iconForCategory(name: string, key?: string | null): LucideIcon {
  const chosen = iconByKey(key);
  if (chosen) return chosen;
  const n = (name || "").toLowerCase();
  for (const [re, k] of NAME_RULES) {
    if (re.test(n)) {
      const i = iconByKey(k);
      if (i) return i;
    }
  }
  return Utensils;
}
