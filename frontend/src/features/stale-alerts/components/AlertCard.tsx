import type { CollaborationAlert } from "@/domain/analytics";

export function AlertCard({
  alert,
  index,
}: {
  alert: CollaborationAlert;
  index: number;
}): React.JSX.Element {
  return (
    <article
      id={`alert-${index}`}
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
  );
}
