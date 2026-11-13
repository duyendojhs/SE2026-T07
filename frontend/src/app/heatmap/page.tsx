import { parseDashboardRange } from "@/domain/analytics";
import { sampleDashboard } from "@/features/dashboard";
import { HeatmapView, selectHeatmapActivity } from "@/features/heatmap";

export const metadata = { title: "Collaboration Heatmap" };

export default function HeatmapPage({
  searchParams = {},
}: {
  searchParams?: { range?: string | string[] };
}): React.JSX.Element {
  const range = parseDashboardRange(searchParams.range);
  const { activity, period } = selectHeatmapActivity(
    sampleDashboard.activity,
    range,
    sampleDashboard.year,
  );

  return <HeatmapView activity={activity} period={period} range={range} />;
}
