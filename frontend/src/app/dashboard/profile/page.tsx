"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Loader2, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getProfile, updateProfile, uploadBranding } from "@/services/restaurant.service";
import { extractErrorMessage } from "@/lib/api";
import type { Restaurant } from "@/types";

type FormValues = Partial<Restaurant>;

const FIELDS: { name: keyof Restaurant; label: string; type?: string }[] = [
  { name: "name", label: "Business name" },
  { name: "description", label: "Description" },
  { name: "phone", label: "Phone" },
  { name: "whatsapp", label: "WhatsApp" },
  { name: "instagram", label: "Instagram" },
  { name: "facebook", label: "Facebook" },
  { name: "tiktok", label: "TikTok" },
  { name: "website", label: "Website" },
  { name: "address", label: "Address" },
  { name: "google_maps_url", label: "Google Maps URL" },
  { name: "theme_color", label: "Theme color", type: "color" },
];

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "ar", label: "العربية (Arabic)" },
  { value: "ckb", label: "کوردی (Kurdish)" },
];

const CURRENCIES = ["USD", "EUR", "GBP", "IQD", "AED", "SAR", "TRY", "EGP"];

export default function ProfilePage() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["profile"], queryFn: getProfile });
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<FormValues>();
  const [uploading, setUploading] = useState<"logo" | "cover" | null>(null);

  useEffect(() => {
    if (data) reset(data);
  }, [data, reset]);

  async function onSubmit(values: FormValues) {
    try {
      await updateProfile(values);
      await qc.invalidateQueries({ queryKey: ["profile"] });
      toast.success("Profile saved");
    } catch (err) {
      toast.error(extractErrorMessage(err));
    }
  }

  async function onUpload(kind: "logo" | "cover", file?: File) {
    if (!file) return;
    setUploading(kind);
    try {
      await uploadBranding(kind, file);
      await qc.invalidateQueries({ queryKey: ["profile"] });
      toast.success(`${kind} updated`);
    } catch (err) {
      toast.error(extractErrorMessage(err));
    } finally {
      setUploading(null);
    }
  }

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">Restaurant profile</h1>

      <Card>
        <CardHeader>
          <CardTitle>Branding</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-6">
          {(["logo", "cover"] as const).map((kind) => (
            <div key={kind} className="space-y-2">
              <Label className="capitalize">{kind}</Label>
              <label className="flex h-10 cursor-pointer items-center gap-2 rounded-lg border px-4 text-sm hover:bg-accent">
                {uploading === kind ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="h-4 w-4" />
                )}
                Upload {kind}
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => onUpload(kind, e.target.files?.[0])}
                />
              </label>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4 sm:grid-cols-2">
            {FIELDS.map((f) => (
              <div key={f.name} className="space-y-2">
                <Label htmlFor={f.name}>{f.label}</Label>
                <Input
                  id={f.name}
                  type={f.type ?? "text"}
                  {...register(f.name as keyof FormValues)}
                />
              </div>
            ))}

            <div className="space-y-2">
              <Label htmlFor="default_language">Language</Label>
              <select
                id="default_language"
                className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
                {...register("default_language")}
              >
                {LANGUAGES.map((l) => (
                  <option key={l.value} value={l.value}>
                    {l.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-muted-foreground">
                Sets the public menu language and enables RTL for Arabic/Kurdish.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="currency">Currency</Label>
              <select
                id="currency"
                className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
                {...register("currency")}
              >
                {CURRENCIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div className="sm:col-span-2">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
                Save changes
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
