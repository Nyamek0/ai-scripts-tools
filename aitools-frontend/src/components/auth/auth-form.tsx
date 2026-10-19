"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { apiFetch } from "@/lib/api";
import { saveAuth } from "@/lib/auth";
import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";

interface AuthFormProps {
  mode: "login" | "register";
}

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const { lang } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === "register") {
        await apiFetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, full_name: fullName || undefined }),
        });
        const data = await apiFetch<{ access_token: string; expires_at: string; user: any }>(
          "/api/auth/login",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password, remember_me: false }),
          }
        );
        saveAuth(data.access_token, data.user, false);
      } else {
        const data = await apiFetch<{ access_token: string; expires_at: string; user: any }>(
          "/api/auth/login",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password, remember_me: rememberMe }),
          }
        );
        saveAuth(data.access_token, data.user, rememberMe);
      }
      router.push("/");
      router.refresh();
    } catch (err: any) {
      setError(err.message || t(lang, "auth.error"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-sm mx-auto space-y-8">
      {/* En-tête */}
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          {mode === "login" ? t(lang, "auth.login_title") : t(lang, "auth.register_title")}
        </h1>
        <p className="text-sm text-muted-foreground">
          {mode === "login" ? t(lang, "auth.login_sub") : t(lang, "auth.register_sub")}
        </p>
      </div>

      {/* Formulaire */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {mode === "register" && (
          <div className="space-y-1.5">
            <Label htmlFor="fullname">
              {t(lang, "auth.full_name")}{" "}
              <span className="text-muted-foreground">{t(lang, "auth.optional")}</span>
            </Label>
            <Input
              id="fullname"
              type="text"
              placeholder="Jean Dupont"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              autoComplete="name"
            />
          </div>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="email">{t(lang, "auth.email")}</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="password">{t(lang, "auth.password")}</Label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder={mode === "register" ? t(lang, "auth.pwd_hint_reg") : t(lang, "auth.pwd_hint_login")}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={mode === "register" ? 8 : undefined}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              className="pr-10"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {mode === "login" && (
          <div className="flex items-center justify-between">
            <Checkbox
              id="remember"
              label={t(lang, "auth.remember")}
              checked={rememberMe}
              onChange={(e) => setRememberMe((e.target as HTMLInputElement).checked)}
            />
            <span className="text-xs text-muted-foreground">
              {rememberMe ? "30 jours" : "1 heure"}
            </span>
          </div>
        )}

        {error && (
          <div className="rounded-xl bg-destructive/10 border border-destructive/20 px-4 py-3">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        <Button type="submit" className="w-full" loading={loading}>
          {mode === "login" ? t(lang, "auth.btn_login") : t(lang, "auth.btn_register")}
        </Button>
      </form>

      {/* Lien alternatif */}
      <p className="text-center text-sm text-muted-foreground">
        {mode === "login" ? (
          <>
            {t(lang, "auth.no_account")}{" "}
            <Link href="/auth/register" className="text-accent font-medium hover:underline">
              {t(lang, "auth.link_register")}
            </Link>
          </>
        ) : (
          <>
            {t(lang, "auth.has_account")}{" "}
            <Link href="/auth/login" className="text-accent font-medium hover:underline">
              {t(lang, "auth.link_login")}
            </Link>
          </>
        )}
      </p>
    </div>
  );
}
