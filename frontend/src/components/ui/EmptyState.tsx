import type { LucideIcon } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
export function EmptyState({
  title,
  description,
  icon: Icon,
  detail,
}: {
  title: string;
  description: string;
  icon: LucideIcon;
  detail: string;
}): React.JSX.Element {
  return (
    <>
      <PageHeader title={title} meta={description} />
      <section className="mt-8 rounded-md border border-dashed border-line bg-surface px-6 py-16 text-center">
        <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-md bg-primary-soft text-primary">
          <Icon size={26} />
        </span>
        <h2 className="mt-5 font-semibold">No repository data connected</h2>
        <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-secondary">
          {detail}
        </p>
        <p className="mt-5 text-xs text-muted">
          Frontend preview · Metadata integration pending
        </p>
      </section>
    </>
  );
}
