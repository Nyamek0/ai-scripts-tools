import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { LanguageProvider } from "@/contexts/language-context";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AITools Platform — Outils IA gratuits",
  description: "Plateforme d'outils IA open-source : suppression de fond, transcription, OCR, TTS, résumé, compression vidéo et plus encore.",
  keywords: ["IA", "outils", "gratuit", "OCR", "transcription", "suppression fond", "TTS"],
  authors: [{ name: "AITools Platform" }],
  openGraph: {
    title: "AITools Platform",
    description: "Des outils IA. Gratuits. Puissants.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className={inter.variable} suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <ThemeProvider>
          <LanguageProvider>
            {children}
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
