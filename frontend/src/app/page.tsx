import { DashboardView, sampleDashboard } from "@/features/dashboard";
import { parseDashboardRange } from "@/domain/analytics";

export const metadata = { title: "Dashboard" };

export default function DashboardPage({
  searchParams = {},
}: {
  searchParams?: { range?: string | string[] };
}): React.JSX.Element {
  const range = parseDashboardRange(searchParams.range);
  return (
    <DashboardView key={range} data={sampleDashboard} initialRange={range} />
  );
}
