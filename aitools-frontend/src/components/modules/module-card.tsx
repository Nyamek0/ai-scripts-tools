"use client";

import Link from "next/link";
import {
  Scissors, Mic, ScanText, FileStack, Volume2, Film, AlignLeft, ImageDown,
  ArrowRight
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { type ModuleConfig } from "@/lib/modules-config";
import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";
import { cn } from "@/lib/utils";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  Scissors, Mic, ScanText, FileStack, Volume2, Film, AlignLeft, ImageDown,
};

interface ModuleCardProps {
  module: ModuleConfig;
}

export function ModuleCard({ module }: ModuleCardProps) {
  const { lang } = useLanguage();
  const Icon = ICONS[module.icon] || Scissors;

  const name = t(lang, `module.${module.slug}.name`) || module.name;
  const desc = t(lang, `module.${module.slug}.desc`) || module.description;

  return (
    <Link href={`/tools/${module.slug}`} className="group block">
      <Card className="h-full hover:shadow-md cursor-pointer group-hover:-translate-y-0.5 transition-all duration-200">
        <CardContent className="p-6 flex flex-col gap-4">
          {/* Icône */}
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted transition-colors group-hover:bg-muted/70">
            <Icon className={cn("h-6 w-6", module.color)} />
          </div>

          {/* Contenu */}
          <div className="flex-1 space-y-1.5">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-foreground text-sm leading-tight">
                {name}
              </h3>
              {module.badge && (
                <Badge variant="default" className="text-[10px] px-1.5 py-0">{module.badge}</Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {desc}
            </p>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-muted-foreground">
              → {module.outputFormat}
            </span>
            <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200" />
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
