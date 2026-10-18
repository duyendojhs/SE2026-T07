export function PageHeader({
  title,
  meta,
  action,
}: {
  title: string;
  meta?: string;
  action?: React.ReactNode;
}): React.JSX.Element {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {meta && <p className="mt-2 text-xs text-muted">{meta}</p>}
      </div>
      {action}
    </div>
  );
}
