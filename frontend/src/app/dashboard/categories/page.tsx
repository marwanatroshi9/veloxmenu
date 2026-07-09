"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Plus, Trash2, Pencil, Loader2 } from "lucide-react";
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
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  createCategory,
  deleteCategory,
  listCategories,
  updateCategory,
} from "@/services/restaurant.service";
import { extractErrorMessage } from "@/lib/api";
import { ICON_OPTIONS, iconForCategory } from "@/features/menu-icons";
import { cn } from "@/lib/utils";
import type { Category } from "@/types";

export default function CategoriesPage() {
  const qc = useQueryClient();
  const { data: categories, isLoading } = useQuery({
    queryKey: ["categories"],
    queryFn: listCategories,
  });
  const [editing, setEditing] = useState<Category | null>(null);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [icon, setIcon] = useState<string | null>(null);
  const [nameAr, setNameAr] = useState("");
  const [nameCkb, setNameCkb] = useState("");

  const invalidate = () => qc.invalidateQueries({ queryKey: ["categories"] });

  function buildTranslations() {
    const t: Record<string, { name?: string }> = {};
    if (nameAr.trim()) t.ar = { name: nameAr.trim() };
    if (nameCkb.trim()) t.ckb = { name: nameCkb.trim() };
    return t;
  }

  const saveMutation = useMutation({
    mutationFn: async () => {
      const translations = buildTranslations();
      if (editing) {
        return updateCategory(editing.id, { name, description, icon, translations });
      }
      return createCategory({ name, description, icon, translations });
    },
    onSuccess: () => {
      invalidate();
      toast.success(editing ? "Category updated" : "Category created");
      setOpen(false);
      setEditing(null);
      setName("");
      setDescription("");
      setIcon(null);
      setNameAr("");
      setNameCkb("");
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  });

  const toggleVisible = useMutation({
    mutationFn: (c: Category) => updateCategory(c.id, { is_visible: !c.is_visible }),
    onSuccess: invalidate,
    onError: (err) => toast.error(extractErrorMessage(err)),
  });

  const removeMutation = useMutation({
    mutationFn: (id: number) => deleteCategory(id),
    onSuccess: () => {
      invalidate();
      toast.success("Category deleted");
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  });

  function openCreate() {
    setEditing(null);
    setName("");
    setDescription("");
    setIcon(null);
    setNameAr("");
    setNameCkb("");
    setOpen(true);
  }

  function openEdit(c: Category) {
    setEditing(c);
    setName(c.name);
    setDescription(c.description ?? "");
    setIcon(c.icon ?? null);
    setNameAr(c.translations?.ar?.name ?? "");
    setNameCkb(c.translations?.ckb?.name ?? "");
    setOpen(true);
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Categories</h1>
          <p className="text-muted-foreground">Organize your menu into sections.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button onClick={openCreate}>
              <Plus className="h-4 w-4" /> New category
            </Button>
          </DialogTrigger>
          <DialogContent className="max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editing ? "Edit category" : "New category"}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cat-name">Name</Label>
                <Input id="cat-name" value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cat-desc">Description</Label>
                <Input
                  id="cat-desc"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Icon</Label>
                <div className="grid max-h-48 grid-cols-6 gap-2 overflow-y-auto rounded-lg border p-2">
                  {ICON_OPTIONS.map(({ key, label, Icon }) => (
                    <button
                      key={key}
                      type="button"
                      title={label}
                      onClick={() => setIcon(icon === key ? null : key)}
                      className={cn(
                        "flex aspect-square items-center justify-center rounded-md border transition-colors",
                        icon === key
                          ? "border-primary bg-primary/10 text-primary"
                          : "hover:bg-accent"
                      )}
                    >
                      <Icon className="h-5 w-5" strokeWidth={1.5} />
                    </button>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  Optional — leave unset to auto-pick from the category name.
                </p>
              </div>
              <div className="space-y-2 rounded-lg border p-3">
                <p className="text-sm font-medium">Translations (optional)</p>
                <Label className="text-xs">العربية — Name</Label>
                <Input dir="rtl" value={nameAr} onChange={(e) => setNameAr(e.target.value)} />
                <Label className="text-xs">کوردی — Name</Label>
                <Input dir="rtl" value={nameCkb} onChange={(e) => setNameCkb(e.target.value)} />
              </div>
              <Button
                className="w-full"
                onClick={() => saveMutation.mutate()}
                disabled={!name.trim() || saveMutation.isPending}
              >
                {saveMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Save
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : categories && categories.length > 0 ? (
        <div className="space-y-3">
          {categories.map((c) => (
            <Card key={c.id}>
              <CardContent className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  {(() => {
                    const Icon = iconForCategory(c.name, c.icon);
                    return (
                      <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-foreground">
                        <Icon className="h-5 w-5" strokeWidth={1.5} />
                      </span>
                    );
                  })()}
                  <div>
                    <p className="font-medium">{c.name}</p>
                    {c.description && (
                      <p className="text-sm text-muted-foreground">{c.description}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={c.is_visible}
                      onCheckedChange={() => toggleVisible.mutate(c)}
                    />
                    <span className="text-xs text-muted-foreground">Visible</span>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => openEdit(c)}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeMutation.mutate(c.id)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            No categories yet. Create your first one.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
