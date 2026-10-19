"use client";

import { Download, CheckCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";
import { getResultUrl } from "@/lib/api";
import { formatDuration } from "@/lib/utils";

interface ResultDisplayProps {
  resultUrl: string;
  message?: string;
  processingTimeMs?: number;
  filename?: string;
  previewText?: string;
  previewImageUrl?: string;
}

export function ResultDisplay({
  resultUrl,
  message,
  processingTimeMs,
  filename = "résultat",
  previewText,
  previewImageUrl,
}: ResultDisplayProps) {
  const { lang } = useLanguage();
  const fullUrl = resultUrl.startsWith("http") ? resultUrl : getResultUrl(resultUrl);

  return (
    <div className="rounded-2xl border border-success/30 bg-success/5 p-6 space-y-4 animate-slide-up">
      {/* Header */}
      <div className="flex items-start gap-3">
        <CheckCircle className="h-5 w-5 text-success mt-0.5 shrink-0" />
        <div className="flex-1">
          <p className="text-sm font-semibold text-foreground">
            {message || t(lang, "result.done")}
          </p>
          {processingTimeMs !== undefined && (
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
              <Clock className="h-3 w-3" />
              {t(lang, "result.processed_in")} {formatDuration(processingTimeMs)}
            </p>
          )}
        </div>
      </div>

      {/* Preview image */}
      {previewImageUrl && (
        <div className="overflow-hidden rounded-xl border border-border bg-muted/30">
          <img
            src={previewImageUrl}
            alt="result"
            className="max-h-64 w-full object-contain p-2"
          />
        </div>
      )}

      {/* Preview texte */}
      {previewText && (
        <div className="rounded-xl border border-border bg-card p-4 max-h-48 overflow-y-auto">
          <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
            {previewText}
          </p>
        </div>
      )}

      {/* Bouton télécharger */}
      <a href={fullUrl} download={filename} target="_blank" rel="noopener noreferrer">
        <Button className="w-full gap-2">
          <Download className="h-4 w-4" />
          {t(lang, "result.download")}
        </Button>
      </a>
    </div>
  );
}
