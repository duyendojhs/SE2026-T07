import { DashboardView } from "@/features/dashboard/components/DashboardView";
import { parseDashboardRange } from "@/features/dashboard/model";
import { sampleDashboard } from "@/mocks/dashboard";

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
