import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, QrCode, Sparkles, Store } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -top-40 left-1/2 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-primary/20 blur-[120px]" />
      </div>

      <nav className="container flex items-center justify-between py-6">
        <span className="text-xl font-bold tracking-tight">MenuHub</span>
        <Button asChild variant="outline">
          <Link href="/login">Sign in</Link>
        </Button>
      </nav>

      <section className="container flex flex-col items-center py-24 text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-card/60 px-4 py-1.5 text-sm text-muted-foreground">
          <Sparkles className="h-4 w-4 text-primary" />
          Premium digital menus, in minutes
        </div>
        <h1 className="max-w-3xl text-5xl font-bold tracking-tight sm:text-6xl">
          The menu platform your restaurant deserves
        </h1>
        <p className="mt-6 max-w-xl text-lg text-muted-foreground">
          Manage categories, dishes and branding from one elegant dashboard. Share a
          stunning, mobile-first menu with a single QR code.
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-4">
          <Button asChild size="lg">
            <Link href="/login">
              Open dashboard <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href="/demo-bistro">View demo menu</Link>
          </Button>
        </div>

        <div className="mt-20 grid w-full max-w-4xl gap-6 sm:grid-cols-3">
          {[
            { icon: Store, title: "Multi-restaurant", desc: "Isolated, secure tenants." },
            { icon: QrCode, title: "QR & share", desc: "PNG, SVG and PDF exports." },
            { icon: Sparkles, title: "Beautiful", desc: "Dark mode, RTL, animations." },
          ].map((f) => (
            <div
              key={f.title}
              className="glass rounded-2xl border p-6 text-left animate-fade-in"
            >
              <f.icon className="mb-3 h-6 w-6 text-primary" />
              <h3 className="font-semibold">{f.title}</h3>
              <p className="text-sm text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
