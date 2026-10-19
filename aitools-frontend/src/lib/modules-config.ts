export type InputType = "image" | "audio" | "pdf-multi" | "video" | "text";

export interface ModuleConfig {
  slug: string;
  name: string;
  description: string;
  icon: string;           // nom Lucide React
  inputType: InputType;
  apiPath: string;
  acceptedMimes?: string;
  outputFormat?: string;
  color: string;          // couleur de l'icône (classe Tailwind text-*)
  badge?: string;         // ex: "Nouveau", "Beta"
}

export const MODULES: ModuleConfig[] = [
  {
    slug: "bg-remove",
    name: "Suppression de fond",
    description: "Supprime l'arrière-plan d'une image en un clic grâce à l'IA.",
    icon: "Scissors",
    inputType: "image",
    apiPath: "/api/bg-remove/process",
    acceptedMimes: "image/jpeg,image/png,image/webp",
    outputFormat: "PNG transparent",
    color: "text-purple-500",
  },
  {
    slug: "transcribe",
    name: "Transcription audio",
    description: "Convertit un fichier audio en texte (Whisper, 100% local).",
    icon: "Mic",
    inputType: "audio",
    apiPath: "/api/transcribe/process",
    acceptedMimes: "audio/mpeg,audio/wav,audio/ogg,audio/mp4,video/mp4",
    outputFormat: "TXT / SRT / JSON",
    color: "text-blue-500",
  },
  {
    slug: "ocr",
    name: "OCR — Image vers texte",
    description: "Extrait le texte d'une image ou d'un screenshot (multi-langues).",
    icon: "ScanText",
    inputType: "image",
    apiPath: "/api/ocr/process",
    acceptedMimes: "image/jpeg,image/png,image/webp",
    outputFormat: "Texte brut",
    color: "text-green-500",
  },
  {
    slug: "pdf-merge",
    name: "Fusion PDF",
    description: "Fusionne plusieurs fichiers PDF en un seul document.",
    icon: "FileStack",
    inputType: "pdf-multi",
    apiPath: "/api/pdf-merge/process",
    acceptedMimes: "application/pdf",
    outputFormat: "PDF",
    color: "text-red-500",
  },
  {
    slug: "tts",
    name: "Synthèse vocale",
    description: "Convertit du texte en parole naturelle (12 voix, multi-langues).",
    icon: "Volume2",
    inputType: "text",
    apiPath: "/api/tts/process",
    outputFormat: "MP3",
    color: "text-orange-500",
  },
  {
    slug: "compress-video",
    name: "Compression vidéo",
    description: "Réduit le poids d'une vidéo sans perte de qualité visible.",
    icon: "Film",
    inputType: "video",
    apiPath: "/api/compress-video/process",
    acceptedMimes: "video/mp4,video/quicktime,video/x-msvideo,video/webm",
    outputFormat: "MP4",
    color: "text-pink-500",
  },
  {
    slug: "summarize",
    name: "Résumé de texte",
    description: "Résume automatiquement un texte long en quelques phrases clés.",
    icon: "AlignLeft",
    inputType: "text",
    apiPath: "/api/summarize/process",
    outputFormat: "Texte résumé",
    color: "text-teal-500",
  },
  {
    slug: "convert-image",
    name: "Conversion d'image",
    description: "Convertit une image dans un autre format (JPEG, PNG, WebP, etc.).",
    icon: "ImageDown",
    inputType: "image",
    apiPath: "/api/convert-image/process",
    acceptedMimes: "image/jpeg,image/png,image/webp,image/gif",
    outputFormat: "JPEG / PNG / WebP / BMP / TIFF",
    color: "text-indigo-500",
  },
];

export function getModule(slug: string): ModuleConfig | undefined {
  return MODULES.find((m) => m.slug === slug);
}
