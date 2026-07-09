"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getProfile } from "@/services/restaurant.service";
import { api, extractErrorMessage } from "@/lib/api";

const FORMATS = ["png", "svg", "pdf"] as const;
type Fmt = (typeof FORMATS)[number];

export default function QrCodePage() {
  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: getProfile });
  const [loading, setLoading] = useState<Fmt | null>(null);

  const publicUrl =
    typeof window !== "undefined" && profile
      ? `${window.location.origin}/${profile.slug}`
      : "";

  async function download(fmt: Fmt) {
    setLoading(fmt);
    try {
      // Fetch through the axios client so the auth header is attached, then save the blob.
      const res = await api.get(`/restaurant/qrcode?format=${fmt}`, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${profile?.slug ?? "restaurant"}-qr.${fmt}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      toast.error(extractErrorMessage(err));
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">QR Code</h1>
        <p className="text-muted-foreground">
          Print this on tables and flyers. It links customers straight to your live menu.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Your public menu</CardTitle>
          <CardDescription className="break-all">{publicUrl}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          {FORMATS.map((fmt) => (
            <Button key={fmt} variant="outline" onClick={() => download(fmt)} disabled={!!loading}>
              {loading === fmt ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              Download {fmt.toUpperCase()}
            </Button>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
