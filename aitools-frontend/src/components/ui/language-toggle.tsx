"use client";

import { useLanguage } from "@/contexts/language-context";

export function LanguageToggle() {
  const { lang, setLang } = useLanguage();

  return (
    <button
      onClick={() => setLang(lang === "fr" ? "en" : "fr")}
      className="flex h-8 items-center justify-center rounded-full px-2.5 text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-muted transition-colors tracking-wide"
      aria-label={lang === "fr" ? "Switch to English" : "Passer en français"}
    >
      {lang === "fr" ? "EN" : "FR"}
    </button>
  );
}
