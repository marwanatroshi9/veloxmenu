"use client";

import { useState } from "react";
import Image from "next/image";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Plus, Trash2, Pencil, Copy, Loader2, Search, Upload, ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  createMenuItem,
  deleteMenuItem,
  duplicateMenuItem,
  listCategories,
  listMenuItems,
  updateMenuItem,
  uploadMenuItemImage,
} from "@/services/restaurant.service";
import { extractErrorMessage } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import type { MenuItem } from "@/types";

interface Draft {
  name: string;
  description: string;
  price: string;
  discount_price: string;
  category_id: number | "";
  is_featured: boolean;
  image_url: string;
  preparation_time: string;
  calories: string;
  spicy_level: number;
  name_ar: string;
  description_ar: string;
  name_ckb: string;
  description_ckb: string;
}

const emptyDraft: Draft = {
  name: "",
  description: "",
  price: "",
  discount_price: "",
  category_id: "",
  is_featured: false,
  image_url: "",
  preparation_time: "",
  calories: "",
  spicy_level: 0,
  name_ar: "",
  description_ar: "",
  name_ckb: "",
  description_ckb: "",
};

export default function MenuPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<MenuItem | null>(null);
  const [draft, setDraft] = useState<Draft>(emptyDraft);
  const [uploading, setUploading] = useState(false);

  const { data: categories } = useQuery({ queryKey: ["categories"], queryFn: listCategories });
  const { data, isLoading } = useQuery({
    queryKey: ["menu-items", search],
    queryFn: () => listMenuItems({ search: search || undefined, page_size: 100 }),
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ["menu-items"] });

  const save = useMutation({
    mutationFn: async () => {
      const translations: Record<string, { name?: string; description?: string }> = {};
      if (draft.name_ar || draft.description_ar) {
        translations.ar = { name: draft.name_ar || undefined, description: draft.description_ar || undefined };
      }
      if (draft.name_ckb || draft.description_ckb) {
        translations.ckb = { name: draft.name_ckb || undefined, description: draft.description_ckb || undefined };
      }
      const payload = {
        name: draft.name,
        description: draft.description || null,
        price: draft.price,
        discount_price: draft.discount_price ? draft.discount_price : null,
        category_id: Number(draft.category_id),
        is_featured: draft.is_featured,
        image_url: draft.image_url || null,
        preparation_time: draft.preparation_time ? Number(draft.preparation_time) : null,
        calories: draft.calories ? Number(draft.calories) : null,
        spicy_level: draft.spicy_level,
        translations,
      };
      return editing
        ? updateMenuItem(editing.id, payload as Partial<MenuItem>)
        : createMenuItem(payload as Partial<MenuItem>);
    },
    onSuccess: () => {
      invalidate();
      toast.success(editing ? "Item updated" : "Item created");
      setOpen(false);
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  });

  const toggleAvailable = useMutation({
    mutationFn: (i: MenuItem) => updateMenuItem(i.id, { is_available: !i.is_available }),
    onSuccess: invalidate,
    onError: (err) => toast.error(extractErrorMessage(err)),
  });

  const remove = useMutation({
    mutationFn: (id: number) => deleteMenuItem(id),
    onSuccess: () => {
      invalidate();
      toast.success("Item deleted");
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  });

  const duplicate = useMutation({
    mutationFn: (id: number) => duplicateMenuItem(id),
    onSuccess: () => {
      invalidate();
      toast.success("Item duplicated");
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  });

  function openCreate() {
    setEditing(null);
    setDraft({ ...emptyDraft, category_id: categories?.[0]?.id ?? "" });
    setOpen(true);
  }

  function openEdit(i: MenuItem) {
    setEditing(i);
    setDraft({
      name: i.name,
      description: i.description ?? "",
      price: i.price,
      discount_price: i.discount_price ?? "",
      category_id: i.category_id,
      is_featured: i.is_featured,
      image_url: i.image_url ?? "",
      preparation_time: i.preparation_time != null ? String(i.preparation_time) : "",
      calories: i.calories != null ? String(i.calories) : "",
      spicy_level: i.spicy_level ?? 0,
      name_ar: i.translations?.ar?.name ?? "",
      description_ar: i.translations?.ar?.description ?? "",
      name_ckb: i.translations?.ckb?.name ?? "",
      description_ckb: i.translations?.ckb?.description ?? "",
    });
    setOpen(true);
  }

  async function onUploadImage(file?: File) {
    if (!file || !editing) return;
    setUploading(true);
    try {
      const updated = await uploadMenuItemImage(editing.id, file);
      setDraft((d) => ({ ...d, image_url: updated.image_url ?? "" }));
      invalidate();
      toast.success("Image uploaded");
    } catch (err) {
      toast.error(extractErrorMessage(err));
    } finally {
      setUploading(false);
    }
  }

  const items = data?.items ?? [];
  const hasCategories = (categories?.length ?? 0) > 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Menu items</h1>
          <p className="text-muted-foreground">{data?.meta.total ?? 0} items</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button onClick={openCreate} disabled={!hasCategories}>
            <Plus className="h-4 w-4" /> New item
          </Button>
        </div>
      </div>

      {!hasCategories && (
        <Card>
          <CardContent className="py-6 text-center text-muted-foreground">
            Create a category first before adding menu items.
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : (
        <div className="grid gap-3">
          {items.map((i) => (
            <Card key={i.id}>
              <CardContent className="flex items-center justify-between gap-4 p-4">
                <div className="flex min-w-0 items-center gap-3">
                  <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-lg border bg-muted">
                    {i.image_url ? (
                      <Image src={i.image_url} alt="" fill sizes="48px" className="object-cover" />
                    ) : (
                      <div className="flex h-full items-center justify-center text-muted-foreground">
                        <ImageIcon className="h-4 w-4" />
                      </div>
                    )}
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="truncate font-medium">{i.name}</p>
                      {i.is_featured && (
                        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">
                          Featured
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {formatCurrency(i.discount_price ?? i.price)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={i.is_available}
                    onCheckedChange={() => toggleAvailable.mutate(i)}
                  />
                  <Button variant="ghost" size="icon" onClick={() => duplicate.mutate(i.id)}>
                    <Copy className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => openEdit(i)}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => remove.mutate(i.id)}>
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit item" : "New item"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} />
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Input
                value={draft.description}
                onChange={(e) => setDraft({ ...draft, description: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Image</Label>
              <div className="flex items-center gap-3">
                <div className="relative h-16 w-16 shrink-0 overflow-hidden rounded-lg border bg-muted">
                  {draft.image_url ? (
                    <Image src={draft.image_url} alt="" fill sizes="64px" className="object-cover" />
                  ) : (
                    <div className="flex h-full items-center justify-center text-muted-foreground">
                      <ImageIcon className="h-5 w-5" />
                    </div>
                  )}
                </div>
                <div className="flex-1 space-y-2">
                  <Input
                    placeholder="Paste an image URL…"
                    value={draft.image_url}
                    onChange={(e) => setDraft({ ...draft, image_url: e.target.value })}
                  />
                  {editing ? (
                    <label className="flex h-9 w-fit cursor-pointer items-center gap-2 rounded-lg border px-3 text-sm hover:bg-accent">
                      {uploading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Upload className="h-4 w-4" />
                      )}
                      Upload file
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => onUploadImage(e.target.files?.[0])}
                      />
                    </label>
                  ) : (
                    <p className="text-xs text-muted-foreground">
                      Save the item first to upload a file, or paste a URL now.
                    </p>
                  )}
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Price</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={draft.price}
                  onChange={(e) => setDraft({ ...draft, price: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Discount price</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={draft.discount_price}
                  onChange={(e) => setDraft({ ...draft, discount_price: e.target.value })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Category</Label>
              <select
                className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
                value={draft.category_id}
                onChange={(e) => setDraft({ ...draft, category_id: Number(e.target.value) })}
              >
                {categories?.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>Prep time (min)</Label>
                <Input
                  type="number"
                  min="0"
                  placeholder="e.g. 5"
                  value={draft.preparation_time}
                  onChange={(e) => setDraft({ ...draft, preparation_time: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Calories</Label>
                <Input
                  type="number"
                  min="0"
                  value={draft.calories}
                  onChange={(e) => setDraft({ ...draft, calories: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Spicy</Label>
                <select
                  className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
                  value={draft.spicy_level}
                  onChange={(e) => setDraft({ ...draft, spicy_level: Number(e.target.value) })}
                >
                  <option value={0}>None</option>
                  <option value={1}>Mild</option>
                  <option value={2}>Medium</option>
                  <option value={3}>Hot</option>
                  <option value={4}>Extra hot</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Switch
                checked={draft.is_featured}
                onCheckedChange={(v) => setDraft({ ...draft, is_featured: v })}
              />
              <Label>Featured</Label>
            </div>

            {/* Translations */}
            <div className="space-y-3 rounded-lg border p-3">
              <p className="text-sm font-medium">Translations (optional)</p>
              <p className="text-xs text-muted-foreground">
                The main Name/Description above are the default language. Add Arabic &amp; Kurdish
                below — visitors switch language on the public menu.
              </p>
              <div className="space-y-2">
                <Label className="text-xs">العربية — Name</Label>
                <Input
                  dir="rtl"
                  value={draft.name_ar}
                  onChange={(e) => setDraft({ ...draft, name_ar: e.target.value })}
                />
                <Label className="text-xs">العربية — Description</Label>
                <Input
                  dir="rtl"
                  value={draft.description_ar}
                  onChange={(e) => setDraft({ ...draft, description_ar: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">کوردی — Name</Label>
                <Input
                  dir="rtl"
                  value={draft.name_ckb}
                  onChange={(e) => setDraft({ ...draft, name_ckb: e.target.value })}
                />
                <Label className="text-xs">کوردی — Description</Label>
                <Input
                  dir="rtl"
                  value={draft.description_ckb}
                  onChange={(e) => setDraft({ ...draft, description_ckb: e.target.value })}
                />
              </div>
            </div>

            <Button
              className="w-full"
              onClick={() => save.mutate()}
              disabled={!draft.name.trim() || !draft.price || !draft.category_id || save.isPending}
            >
              {save.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Save
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
