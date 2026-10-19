"use client";

import Link from "next/link";
import { Zap } from "lucide-react";
import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";

export function Footer() {
  const { lang } = useLanguage();

  return (
    <footer className="border-t border-border bg-background mt-24">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-accent">
              <Zap className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="text-sm font-semibold text-foreground">AITools Platform</span>
          </div>

          <p className="text-xs text-muted-foreground text-center">
            {t(lang, "footer.desc")}
          </p>

          <div className="flex items-center gap-6">
            <Link href="/" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              {t(lang, "footer.tools")}
            </Link>
            <Link href="/auth/register" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              {t(lang, "footer.register")}
            </Link>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
