import { Info } from "lucide-react";
import type { DashboardMetric } from "../types";

export function MetricsGrid({
  metrics,
}: {
  metrics: DashboardMetric[];
}): React.JSX.Element {
  return (
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
  );
}
