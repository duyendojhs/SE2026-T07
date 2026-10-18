"use client";
import Link from "next/link";
import { useState } from "react";
import { ArrowRight, GitPullRequest, Info } from "lucide-react";
import { Panel } from "@/components/ui/Panel";
import { PageHeader } from "@/components/layout/PageHeader";
import { selectDashboard } from "../model";
import { ActivityChart } from "./ActivityChart";
import type { DashboardData, DashboardRange } from "@/types/dashboard";

export function DashboardView({
  data,
  initialRange = "7d",
}: {
  data: DashboardData;
  initialRange?: DashboardRange;
}): React.JSX.Element {
  const [range, setRange] = useState<DashboardRange>(initialRange);
  const view = selectDashboard(data, range);
  const alertsHref = `/stale-alerts?range=${range}`;
  const metrics = [
    {
      label: "Awaiting review",
      value: data.awaitingReview,
      hint: "Current open PRs waiting for review",
      color: "text-foreground",
      scope: "Current snapshot",
    },
    {
      label: "Stale PRs",
      value: view.staleCount,
      hint: "Current PRs that meet the stale activity rule",
      color: "text-warning",
      scope: "Current snapshot",
    },
    {
      label: "Merged PRs",
      value: view.merged,
      hint: "PRs merged during the selected period",
      color: "text-success",
      scope: "Selected period",
    },
    {
      label: "Median review wait",
      value: view.medianWait === null ? "—" : `${view.medianWait}h`,
      hint: "Median hours from PR opening to first review, for first reviews in the selected period",
      color: "text-foreground",
      scope: "Selected period",
    },
  ];
  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        action={
          <span className="rounded border border-line bg-surface px-2 py-1 text-[11px] text-muted">
            Sample data
          </span>
        }
      />
      <div className="flex flex-wrap items-end justify-between gap-4 rounded-lg border border-line bg-surface px-4 py-3">
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-medium text-muted">Repository</p>
          <p className="mt-2 break-words text-sm font-medium">
            {data.repository}
          </p>
        </div>
        <label className="text-[11px] font-medium text-muted">
          Period
          <select
            aria-label="Period"
            value={range}
            onChange={(event) => {
              const nextRange = event.target.value === "3d" ? "3d" : "7d";
              setRange(nextRange);
              const url = new URL(window.location.href);
              url.searchParams.set("range", nextRange);
              window.history.replaceState(null, "", url);
            }}
            className="mt-1.5 block rounded border border-line bg-surface px-3 py-2 text-sm text-foreground"
          >
            <option value="7d">Last 7 days</option>
            <option value="3d">Last 3 days</option>
          </select>
        </label>
        <p className="pb-2 text-xs text-muted">{view.period}</p>
      </div>
      <section
        aria-label="Project metrics"
        className="grid grid-cols-2 gap-3 xl:grid-cols-4"
      >
        {metrics.map((metric) => (
          <article
            key={metric.label}
            className="rounded-lg border border-line bg-surface p-5"
          >
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-xs font-medium text-secondary">
                {metric.label}
              </h2>
              <span
                tabIndex={0}
                role="note"
                aria-label={metric.hint}
                title={metric.hint}
                className="cursor-help text-muted"
              >
                <Info size={13} />
              </span>
            </div>
            <p
              className={`my-4 font-mono text-3xl font-semibold ${metric.color}`}
              aria-label={`${metric.label}: ${metric.value}`}
            >
              {metric.value}
            </p>
            <p className="text-[10px] text-muted">{metric.scope}</p>
          </article>
        ))}
      </section>
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
        <Panel
          title="Activity trend"
          className="order-2 xl:order-1"
          action={
            <Link
              href={`/heatmap?range=${range}`}
              className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
            >
              View details <ArrowRight size={13} />
            </Link>
          }
        >
          <ActivityChart days={view.activity} />
        </Panel>
        <Panel
          title="Needs attention"
          className="order-1 xl:order-2"
          action={
            <Link
              href={alertsHref}
              className="text-xs text-primary hover:underline"
            >
              View all ({data.alerts.length})
            </Link>
          }
        >
          {data.alerts.length ? (
            <ul className="divide-y divide-line">
              {data.alerts.slice(0, 3).map((alert, index) => (
                <li key={alert.id} className="py-4 first:pt-0 last:pb-0">
                  <Link
                    href={`${alertsHref}#alert-${index}`}
                    className="group flex gap-2.5"
                  >
                    <GitPullRequest
                      size={16}
                      className="mt-0.5 shrink-0 text-warning"
                    />
                    <div className="min-w-0">
                      <p className="text-xs font-medium group-hover:text-primary">
                        {alert.id} · {alert.title}
                      </p>
                      <p className="mt-2 text-xs leading-5 text-secondary">
                        {alert.reason}
                      </p>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="py-8 text-sm text-muted">No alerts need attention.</p>
          )}
        </Panel>
      </div>
      <Panel title={range === "7d" ? "Weekly summary" : "Period summary"}>
        <div className="grid gap-5 text-sm md:grid-cols-3">
          <div>
            <h3 className="text-[10px] font-semibold uppercase tracking-wider text-muted">
              Progress
            </h3>
            <p className="mt-2 leading-6">
              {view.merged} PRs merged · {view.reviews} reviews
            </p>
          </div>
          <div>
            <h3 className="text-[10px] font-semibold uppercase tracking-wider text-muted">
              Bottleneck
            </h3>
            <p className="mt-2 leading-6">
              {data.awaitingReview} PRs awaiting review
            </p>
          </div>
          <div>
            <h3 className="text-[10px] font-semibold uppercase tracking-wider text-muted">
              Next step
            </h3>
            <Link
              href={alertsHref}
              className="mt-2 inline-block leading-6 text-primary hover:underline"
            >
              {data.alerts.length
                ? "Review flagged pull requests"
                : "Check the review queue"}{" "}
              →
            </Link>
          </div>
        </div>
      </Panel>
    </div>
  );
}
