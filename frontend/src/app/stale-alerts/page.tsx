import Link from "next/link";
import { PageHeader } from "@/components/layout/PageHeader";
import { ArrowLeft } from "lucide-react";
import { sampleDashboard } from "@/mocks/dashboard";
import { parseDashboardRange } from "@/features/dashboard/model";
export const metadata = { title: "Stale Alerts" };
export default function AlertsPage({
  searchParams = {},
}: {
  searchParams?: { range?: string | string[] };
}): React.JSX.Element {
  const range = parseDashboardRange(searchParams.range);
  return (
    <div className="space-y-5">
      <Link
        href={`/?range=${range}`}
        className="inline-flex items-center gap-2 text-xs text-primary hover:underline"
      >
        <ArrowLeft size={14} />
        Dashboard
      </Link>
      <PageHeader title="Stale Alerts" meta="Sample data · Current snapshot" />
      <div className="divide-y divide-line rounded-lg border border-line bg-surface">
        {sampleDashboard.alerts.map((alert, index) => (
          <article
            id={`alert-${index}`}
            key={alert.id}
            className="scroll-mt-6 p-5 target:bg-warning-soft"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-sm font-semibold">
                {alert.id} · {alert.title}
              </h2>
              <span className="rounded bg-warning-soft px-2 py-1 text-xs text-warning">
                {alert.label}
              </span>
            </div>
            <p className="mt-3 text-sm text-secondary">{alert.reason}</p>
            <dl className="mt-4 grid gap-4 text-xs sm:grid-cols-2">
              <div>
                <dt className="text-muted">Rule</dt>
                <dd className="mt-1 font-mono">{alert.rule}</dd>
              </div>
              <div>
                <dt className="text-muted">Evidence</dt>
                <dd className="mt-1">{alert.metric}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </div>
  );
}
