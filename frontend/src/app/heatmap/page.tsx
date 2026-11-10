import {
  parseDashboardRange,
  selectDashboard,
  sampleDashboard,
} from "@/features/dashboard";
import { HeatmapView } from "@/features/heatmap";

export const metadata = { title: "Collaboration Heatmap" };

export default function HeatmapPage({
  searchParams = {},
}: {
  searchParams?: { range?: string | string[] };
}): React.JSX.Element {
  const range = parseDashboardRange(searchParams.range);
  const { activity, period } = selectDashboard(sampleDashboard, range);

  return <HeatmapView activity={activity} period={period} range={range} />;
}
