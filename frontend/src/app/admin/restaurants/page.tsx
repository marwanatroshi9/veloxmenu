"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Plus, Search, Ban, CheckCircle2, KeyRound, Trash2, Loader2, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  activateRestaurant,
  createRestaurant,
  deleteRestaurant,
  listRestaurants,
  resetManagerPassword,
  suspendRestaurant,
  type CreateRestaurantPayload,
} from "@/services/admin.service";
import { extractErrorMessage } from "@/lib/api";

const emptyForm: CreateRestaurantPayload = {
  name: "",
  manager_email: "",
  manager_password: "",
  manager_full_name: "",
};

export default function AdminRestaurantsPage() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<CreateRestaurantPayload>(emptyForm);

  const { data, isLoading } = useQuery({
    queryKey: ["admin-restaurants", page, search],
    queryFn: () => listRestaurants({ page, page_size: 10, search: search || undefined }),
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ["admin-restaurants"] });

  const create = useMutation({
    mutationFn: () => createRestaurant(form),
    onSuccess: () => {
      invalidate();
      toast.success("Restaurant created");
      setOpen(false);
      setForm(emptyForm);
    },
    onError: (err) => toast.error(extractErrorMessage(err)),
  });

  const suspend = useMutation({
    mutationFn: (id: number) => suspendRestaurant(id),
    onSuccess: () => { invalidate(); toast.success("Suspended"); },
    onError: (err) => toast.error(extractErrorMessage(err)),
  });
  const activate = useMutation({
    mutationFn: (id: number) => activateRestaurant(id),
    onSuccess: () => { invalidate(); toast.success("Activated"); },
    onError: (err) => toast.error(extractErrorMessage(err)),
  });
  const remove = useMutation({
    mutationFn: (id: number) => deleteRestaurant(id),
    onSuccess: () => { invalidate(); toast.success("Deleted"); },
    onError: (err) => toast.error(extractErrorMessage(err)),
  });
  const resetPw = useMutation({
    mutationFn: (id: number) => resetManagerPassword(id),
    onSuccess: (res) =>
      toast.success(`Temp password for ${res.manager_email}: ${res.temporary_password}`, {
        duration: 15000,
      }),
    onError: (err) => toast.error(extractErrorMessage(err)),
  });

  const rows = data?.items ?? [];
  const totalPages = data?.meta.total_pages ?? 1;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Restaurants</h1>
          <p className="text-muted-foreground">{data?.meta.total ?? 0} total</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="pl-9"
            />
          </div>
          <Button onClick={() => setOpen(true)}>
            <Plus className="h-4 w-4" /> New restaurant
          </Button>
        </div>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : (
        <div className="grid gap-3">
          {rows.map((r) => (
            <Card key={r.id}>
              <CardContent className="flex flex-wrap items-center justify-between gap-3 p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{r.name}</p>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs ${
                        r.status === "active"
                          ? "bg-emerald-500/10 text-emerald-600"
                          : "bg-amber-500/10 text-amber-600"
                      }`}
                    >
                      {r.status}
                    </span>
                  </div>
                  <a
                    href={`/${r.slug}`}
                    target="_blank"
                    className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-primary"
                  >
                    /{r.slug} <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  {r.status === "active" ? (
                    <Button variant="outline" size="sm" onClick={() => suspend.mutate(r.id)}>
                      <Ban className="h-4 w-4" /> Suspend
                    </Button>
                  ) : (
                    <Button variant="outline" size="sm" onClick={() => activate.mutate(r.id)}>
                      <CheckCircle2 className="h-4 w-4" /> Activate
                    </Button>
                  )}
                  <Button variant="outline" size="sm" onClick={() => resetPw.mutate(r.id)}>
                    <KeyRound className="h-4 w-4" /> Reset password
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => remove.mutate(r.id)}>
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New restaurant</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {([
              ["name", "Restaurant name", "text"],
              ["manager_full_name", "Manager name", "text"],
              ["manager_email", "Manager email", "email"],
              ["manager_password", "Manager password", "password"],
            ] as const).map(([key, label, type]) => (
              <div key={key} className="space-y-2">
                <Label>{label}</Label>
                <Input
                  type={type}
                  value={(form[key] as string) ?? ""}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                />
              </div>
            ))}
            <Button
              className="w-full"
              onClick={() => create.mutate()}
              disabled={
                !form.name.trim() ||
                !form.manager_email.trim() ||
                form.manager_password.length < 8 ||
                create.isPending
              }
            >
              {create.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Create restaurant
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
