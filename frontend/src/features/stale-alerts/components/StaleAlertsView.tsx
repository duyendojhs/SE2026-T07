import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { PageHeader } from "@/shared/components/layout/PageHeader";
import type { CollaborationAlert, DashboardRange } from "@/features/dashboard";
import { AlertCard } from "./AlertCard";

export function StaleAlertsView({
  alerts,
  range,
}: {
  alerts: CollaborationAlert[];
  range: DashboardRange;
}): React.JSX.Element {
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
        {alerts.map((alert, index) => (
          <AlertCard key={alert.id} alert={alert} index={index} />
        ))}
      </div>
    </div>
  );
}
