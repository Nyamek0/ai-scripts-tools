"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Zap, LogOut, LayoutDashboard } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { getAuth, clearAuth, type User as AuthUser } from "@/lib/auth";
import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";
import { cn } from "@/lib/utils";

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { lang } = useLanguage();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const { user } = getAuth();
    setUser(user);
  }, [pathname]);

  function handleLogout() {
    clearAuth();
    setUser(null);
    setMenuOpen(false);
    router.push("/");
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-semibold text-foreground">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-accent">
            <Zap className="h-4 w-4 text-white" />
          </div>
          <span className="text-sm tracking-tight">AITools</span>
        </Link>

        {/* Nav */}
        <nav className="hidden md:flex items-center gap-1">
          <Link
            href="/"
            className={cn(
              "rounded-full px-4 py-2 text-sm font-medium transition-colors",
              pathname === "/"
                ? "bg-muted text-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            )}
          >
            {t(lang, "nav.tools")}
          </Link>
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-1">
          {/* Toggles thème + langue */}
          <ThemeToggle />
          <LanguageToggle />

          <div className="mx-1 h-5 w-px bg-border" />

          {user ? (
            <div className="relative">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-sm font-medium text-foreground hover:bg-muted transition-colors"
              >
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-accent text-white text-xs font-semibold">
                  {(user.full_name || user.email).charAt(0).toUpperCase()}
                </div>
                <span className="max-w-[120px] truncate">
                  {user.full_name || user.email}
                </span>
              </button>

              {menuOpen && (
                <div className="absolute right-0 mt-2 w-52 rounded-2xl border border-border bg-card shadow-lg py-1 animate-fade-in">
                  <Link
                    href="/dashboard"
                    onClick={() => setMenuOpen(false)}
                    className="flex items-center gap-2 px-4 py-2.5 text-sm text-foreground hover:bg-muted transition-colors"
                  >
                    <LayoutDashboard className="h-4 w-4 text-muted-foreground" />
                    {t(lang, "nav.my_jobs")}
                  </Link>
                  <div className="my-1 border-t border-border" />
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-destructive hover:bg-muted transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                    {t(lang, "nav.logout")}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <>
              <Link href="/auth/login">
                <Button variant="ghost" size="sm">{t(lang, "nav.login")}</Button>
              </Link>
              <Link href="/auth/register">
                <Button size="sm">{t(lang, "nav.register")}</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
