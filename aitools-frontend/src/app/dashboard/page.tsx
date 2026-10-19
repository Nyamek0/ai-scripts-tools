"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Clock, CheckCircle, XCircle, Loader2, Download, Search } from "lucide-react";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { apiFetch, getResultUrl } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { useLanguage } from "@/contexts/language-context";
import { t } from "@/lib/i18n";
import { formatDate, formatDuration } from "@/lib/utils";

interface Job {
  id: string;
  module_name: string;
  status: "pending" | "processing" | "success" | "failed";
  input_filename: string | null;
  processing_time_ms: number | null;
  result_url: string | null;
  error_message: string | null;
  created_at: string;
}

interface JobsResponse {
  jobs: Job[];
  total: number;
  pages: number;
}

const STATUSES = ["success", "failed", "processing", "pending"] as const;

export default function DashboardPage() {
  const router = useRouter();
  const { lang } = useLanguage();

  const STATUS_CONFIG = {
    success:    { label: t(lang, "status.success"),    variant: "success"     as const, icon: CheckCircle },
    failed:     { label: t(lang, "status.failed"),     variant: "destructive" as const, icon: XCircle },
    processing: { label: t(lang, "status.processing"), variant: "default"     as const, icon: Loader2 },
    pending:    { label: t(lang, "status.pending"),    variant: "secondary"   as const, icon: Clock },
  };

  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filtres
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Debounce search
  useEffect(() => {
    const id = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(id);
  }, [search]);

  // Reset page quand les filtres changent
  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, statusFilter]);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/auth/login");
      return;
    }
    fetchJobs();
  }, [page, debouncedSearch, statusFilter]);

  async function fetchJobs() {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        per_page: "15",
      });
      if (debouncedSearch) params.set("module_name", debouncedSearch);
      if (statusFilter) params.set("status", statusFilter);

      const data = await apiFetch<JobsResponse>(`/api/jobs/mine?${params}`);
      setJobs(data.jobs);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 mx-auto w-full max-w-5xl px-6 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">
              {t(lang, "dash.title")}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              {total} {t(lang, total > 1 ? "dash.total_n" : "dash.total_1")}
            </p>
          </div>
          <Link href="/">
            <Button variant="outline" size="sm">{t(lang, "dash.new_tool")}</Button>
          </Link>
        </div>

        {/* Filtres */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t(lang, "dash.search")}
              className="w-full rounded-xl border border-border bg-card pl-9 pr-4 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-colors"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-border bg-card px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-colors"
          >
            <option value="">{t(lang, "dash.all_statuses")}</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>{t(lang, `status.${s}`)}</option>
            ))}
          </select>
        </div>

        {/* Erreur */}
        {error && (
          <div className="rounded-xl bg-destructive/10 border border-destructive/20 px-4 py-3 mb-6">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        {/* Table */}
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <p className="text-muted-foreground text-sm">{t(lang, "dash.empty")}</p>
            <Link href="/">
              <Button>{t(lang, "dash.try_tool")}</Button>
            </Link>
          </div>
        ) : (
          <div className="rounded-2xl border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-6 py-3.5 text-left text-xs font-medium text-muted-foreground">{t(lang, "dash.col_module")}</th>
                  <th className="px-6 py-3.5 text-left text-xs font-medium text-muted-foreground">{t(lang, "dash.col_file")}</th>
                  <th className="px-6 py-3.5 text-left text-xs font-medium text-muted-foreground">{t(lang, "dash.col_status")}</th>
                  <th className="px-6 py-3.5 text-left text-xs font-medium text-muted-foreground">{t(lang, "dash.col_duration")}</th>
                  <th className="px-6 py-3.5 text-left text-xs font-medium text-muted-foreground">{t(lang, "dash.col_date")}</th>
                  <th className="px-6 py-3.5 text-right text-xs font-medium text-muted-foreground">{t(lang, "dash.col_action")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-card">
                {jobs.map((job) => {
                  const cfg = STATUS_CONFIG[job.status] || STATUS_CONFIG.pending;
                  const StatusIcon = cfg.icon;
                  return (
                    <tr key={job.id} className="hover:bg-muted/30 transition-colors">
                      <td className="px-6 py-4 font-medium text-foreground">
                        {job.module_name.replace(/_/g, " ")}
                      </td>
                      <td className="px-6 py-4 text-muted-foreground max-w-[160px] truncate">
                        {job.input_filename || "—"}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={cfg.variant} className="gap-1">
                          <StatusIcon className={`h-3 w-3 ${job.status === "processing" ? "animate-spin" : ""}`} />
                          {cfg.label}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">
                        {job.processing_time_ms ? formatDuration(job.processing_time_ms) : "—"}
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">
                        {formatDate(job.created_at)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {job.result_url && job.status === "success" && (
                          <a
                            href={getResultUrl(job.result_url)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-accent hover:underline"
                          >
                            <Download className="h-3 w-3" />
                            {t(lang, "dash.download")}
                          </a>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {/* Pagination */}
            {pages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-muted/20">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  {t(lang, "dash.prev")}
                </Button>
                <span className="text-xs text-muted-foreground">
                  {t(lang, "dash.page", { p: page, total: pages })}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(pages, p + 1))}
                  disabled={page === pages}
                >
                  {t(lang, "dash.next")}
                </Button>
              </div>
            )}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
