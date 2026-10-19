"use client";

import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";

interface TextInputProps {
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
  maxChars?: number;
  rows?: number;
}

export function TextInput({
  value,
  onChange,
  placeholder,
  maxChars = 5000,
  rows = 8,
}: TextInputProps) {
  const { lang } = useLanguage();
  const remaining = maxChars - value.length;
  const isNearLimit = remaining < maxChars * 0.1;

  const defaultPlaceholder = lang === "fr" ? "Saisissez votre texte ici…" : "Enter your text here…";
  const remainingLabel = remaining === 1
    ? t(lang, "text.remaining_1")
    : t(lang, "text.remaining");

  return (
    <div className="space-y-2">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value.slice(0, maxChars))}
        placeholder={placeholder ?? defaultPlaceholder}
        rows={rows}
        className="w-full rounded-2xl border border-border bg-card px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-colors"
      />
      <p className={`text-xs text-right ${isNearLimit ? "text-destructive" : "text-muted-foreground"}`}>
        {remaining.toLocaleString()} {remainingLabel}
      </p>
    </div>
  );
}
