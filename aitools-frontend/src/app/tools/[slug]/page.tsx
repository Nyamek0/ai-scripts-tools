"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import {
  Scissors, Mic, ScanText, FileStack, Volume2, Film, AlignLeft, ImageDown,
} from "lucide-react";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { FileUpload } from "@/components/modules/file-upload";
import { TextInput } from "@/components/modules/text-input";
import { ResultDisplay } from "@/components/modules/result-display";
import { getModule } from "@/lib/modules-config";
import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";
import { apiUpload } from "@/lib/api";
import { cn } from "@/lib/utils";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  Scissors, Mic, ScanText, FileStack, Volume2, Film, AlignLeft, ImageDown,
};

export default function ToolPage() {
  const { slug } = useParams<{ slug: string }>();
  const { lang } = useLanguage();
  const module = getModule(slug);

  const [files, setFiles] = useState<File[]>([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    url: string;
    message: string;
    processingTimeMs?: number;
    previewText?: string;
  } | null>(null);

  if (!module) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-4">
            <p className="text-lg font-semibold text-foreground">{t(lang, "tool.not_found")}</p>
            <Link href="/">
              <Button variant="outline">{t(lang, "tool.back_home")}</Button>
            </Link>
          </div>
        </main>
      </div>
    );
  }

  const Icon = ICONS[module.icon] || Scissors;
  const isText = module.inputType === "text";
  const isMultiFile = module.inputType === "pdf-multi";

  const moduleName = t(lang, `module.${module.slug}.name`) || module.name;
  const moduleDesc = t(lang, `module.${module.slug}.desc`) || module.description;

  async function handleProcess() {
    setError(null);
    setResult(null);
    setLoading(true);

    try {
      const formData = new FormData();

      if (isText) {
        if (!text.trim()) throw new Error(t(lang, "tool.err_text"));
        formData.append("text", text);
      } else {
        if (files.length === 0) throw new Error(t(lang, "tool.err_file"));
        if (isMultiFile) {
          files.forEach((f) => formData.append("files", f));
        } else {
          formData.append("file", files[0]);
        }
      }

      const data = await apiUpload<{
        job_id?: string;
        result_url?: string;
        message?: string;
        processing_time_ms?: number;
        data?: { text?: string; summary?: string; result_url?: string; processing_time_ms?: number; message?: string };
      }>(module!.apiPath, formData);

      const url = data.result_url || data.data?.result_url || "";
      const msg = data.message || data.data?.message || t(lang, "tool.done");
      const timeMs = data.processing_time_ms || data.data?.processing_time_ms;
      const previewText = data.data?.text || data.data?.summary;

      setResult({ url, message: msg, processingTimeMs: timeMs, previewText });
    } catch (err: any) {
      setError(err.message || t(lang, "tool.err_generic"));
    } finally {
      setLoading(false);
    }
  }

  const canProcess = isText ? text.trim().length > 0 : files.length > 0;

  const fileLabel = isMultiFile
    ? t(lang, "tool.drop_pdf")
    : `${lang === "fr" ? "Déposez votre" : "Drop your"} ${t(lang, module.inputType === "image" ? "tool.img" : module.inputType === "audio" ? "tool.audio" : "tool.video")}`;

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 mx-auto w-full max-w-2xl px-6 py-12">
        {/* Retour */}
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors mb-8"
        >
          <ArrowLeft className="h-4 w-4" />
          {t(lang, "tool.back_all")}
        </Link>

        {/* Header module */}
        <div className="flex items-start gap-4 mb-10">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted shrink-0">
            <Icon className={cn("h-7 w-7", module.color)} />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">
              {moduleName}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">{moduleDesc}</p>
          </div>
        </div>

        {/* Zone d'entrée */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <p className="text-sm font-medium text-foreground">
              {isText
                ? t(lang, "tool.label_text")
                : isMultiFile
                ? t(lang, "tool.label_pdfs")
                : t(lang, "tool.label_file")}
            </p>

            {isText ? (
              <TextInput
                value={text}
                onChange={setText}
                maxChars={module.slug === "summarize" ? 50000 : 5000}
                placeholder={
                  module.slug === "tts"
                    ? t(lang, "tool.tts_ph")
                    : t(lang, "tool.sum_ph")
                }
              />
            ) : (
              <FileUpload
                accept={module.acceptedMimes}
                multiple={isMultiFile}
                label={fileLabel}
                onChange={setFiles}
              />
            )}
          </div>

          {/* Erreur */}
          {error && (
            <div className="rounded-xl bg-destructive/10 border border-destructive/20 px-4 py-3">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          {/* Bouton traiter */}
          {!result && (
            <Button
              className="w-full"
              size="lg"
              onClick={handleProcess}
              loading={loading}
              disabled={!canProcess}
            >
              {loading ? t(lang, "tool.processing") : t(lang, "tool.process")}
            </Button>
          )}

          {/* Résultat */}
          {result && (
            <>
              <ResultDisplay
                resultUrl={result.url}
                message={result.message}
                processingTimeMs={result.processingTimeMs}
                filename={`${module.slug}-result`}
                previewText={result.previewText}
              />
              <Button
                variant="outline"
                className="w-full"
                onClick={() => { setResult(null); setFiles([]); setText(""); }}
              >
                {t(lang, "tool.new")}
              </Button>
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
