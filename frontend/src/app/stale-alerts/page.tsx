import { parseDashboardRange } from "@/domain/analytics";
import { sampleDashboard } from "@/features/dashboard";
import { StaleAlertsView } from "@/features/stale-alerts";

export const metadata = { title: "Stale Alerts" };

export default function AlertsPage({
  searchParams = {},
}: {
  searchParams?: { range?: string | string[] };
}): React.JSX.Element {
  const range = parseDashboardRange(searchParams.range);

  return <StaleAlertsView alerts={sampleDashboard.alerts} range={range} />;
}
