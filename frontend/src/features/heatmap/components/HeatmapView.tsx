import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { PageHeader } from "@/shared/components/layout/PageHeader";
import { Panel } from "@/shared/components/ui/Panel";
import type { ActivityDay, DashboardRange } from "@/features/dashboard";
import { HeatmapTable } from "./HeatmapTable";
import { HeatmapLegend } from "./HeatmapLegend";

export function HeatmapView({
  activity,
  period,
  range,
}: {
  activity: ActivityDay[];
  period: string;
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
      <PageHeader
        title="Collaboration Heatmap"
        meta={`${period} · Sample data`}
      />
      <Panel title="Collaboration activity">
        <HeatmapTable activity={activity} period={period} />
        <HeatmapLegend />
      </Panel>
    </div>
  );
}
