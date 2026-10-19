"use client";

import { useRef, useState, useCallback } from "react";
import { Upload, X, File } from "lucide-react";
import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";
import { cn, formatBytes } from "@/lib/utils";

interface FileUploadProps {
  accept?: string;
  multiple?: boolean;
  maxSizeMB?: number;
  label?: string;
  onChange: (files: File[]) => void;
}

export function FileUpload({
  accept,
  multiple = false,
  maxSizeMB = 50,
  label,
  onChange,
}: FileUploadProps) {
  const { lang } = useLanguage();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);

  const dropLabel = label ?? (lang === "fr" ? "Déposez votre fichier ici" : "Drop your file here");

  const handleFiles = useCallback((incoming: FileList | null) => {
    if (!incoming) return;
    setError(null);

    const arr = Array.from(incoming);
    const tooBig = arr.find((f) => f.size > maxSizeMB * 1024 * 1024);
    if (tooBig) {
      setError(t(lang, "upload.too_big", { n: maxSizeMB }));
      return;
    }

    setFiles(arr);
    onChange(arr);
  }, [maxSizeMB, onChange, lang]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const removeFile = (index: number) => {
    const updated = files.filter((_, i) => i !== index);
    setFiles(updated);
    onChange(updated);
  };

  return (
    <div className="space-y-3">
      {/* Zone de drop */}
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={cn(
          "relative flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-10 cursor-pointer transition-all duration-200",
          dragging
            ? "border-accent bg-accent/5 scale-[1.01]"
            : "border-border bg-muted/30 hover:border-accent/50 hover:bg-muted/50"
        )}
      >
        <div className={cn(
          "flex h-12 w-12 items-center justify-center rounded-2xl transition-colors",
          dragging ? "bg-accent/10" : "bg-muted"
        )}>
          <Upload className={cn("h-5 w-5", dragging ? "text-accent" : "text-muted-foreground")} />
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-foreground">{dropLabel}</p>
          <p className="text-xs text-muted-foreground mt-1">
            {t(lang, "upload.browse", { n: maxSizeMB })}
          </p>
          {accept && (
            <p className="text-xs text-muted-foreground/70 mt-0.5">
              {accept.replace(/,/g, ", ")}
            </p>
          )}
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {/* Erreur */}
      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      {/* Fichiers sélectionnés */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, i) => (
            <div
              key={i}
              className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3"
            >
              <File className="h-4 w-4 text-muted-foreground shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">{file.name}</p>
                <p className="text-xs text-muted-foreground">{formatBytes(file.size)}</p>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); removeFile(i); }}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
