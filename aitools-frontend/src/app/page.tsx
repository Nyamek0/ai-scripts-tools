"use client";

import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { ModuleCard } from "@/components/modules/module-card";
import { MODULES } from "@/lib/modules-config";
import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";

export default function HomePage() {
  const { lang } = useLanguage();

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1">
        {/* ── Hero ── */}
        <section className="mx-auto max-w-6xl px-6 pt-24 pb-16 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 text-xs text-muted-foreground mb-8">
            <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
            {t(lang, "home.badge")}
          </div>

          <h1 className="text-5xl md:text-6xl font-semibold tracking-tight text-foreground leading-tight max-w-3xl mx-auto text-balance">
            {t(lang, "home.h1_a")}<br />
            <span className="text-accent">{t(lang, "home.h1_b")}</span>{" "}
            {t(lang, "home.h1_c")}
          </h1>

          <p className="mt-6 text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed">
            {t(lang, "home.desc")}
          </p>

          <div className="mt-10 flex items-center justify-center gap-4">
            <a
              href="#tools"
              className="inline-flex items-center justify-center rounded-full bg-accent text-white px-8 py-3 text-sm font-medium hover:bg-accent/90 transition-colors shadow-sm"
            >
              {t(lang, "home.cta")}
            </a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center rounded-full border border-border bg-card text-foreground px-8 py-3 text-sm font-medium hover:bg-muted transition-colors"
            >
              GitHub
            </a>
          </div>
        </section>

        {/* ── Grille des modules ── */}
        <section id="tools" className="mx-auto max-w-6xl px-6 pb-24">
          <div className="mb-10 text-center">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              {t(lang, "home.tools_title", { n: MODULES.length })}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {t(lang, "home.tools_sub")}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {MODULES.map((mod) => (
              <ModuleCard key={mod.slug} module={mod} />
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
