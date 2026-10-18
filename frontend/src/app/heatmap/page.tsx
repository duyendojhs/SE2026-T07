import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { sampleDashboard } from "@/mocks/dashboard";
import {
  parseDashboardRange,
  selectDashboard,
} from "@/features/dashboard/model";
import { PageHeader } from "@/components/layout/PageHeader";
import { Panel } from "@/components/ui/Panel";
const rows = [
  { key: "commits", label: "Commits" },
  { key: "pullRequests", label: "PRs opened" },
  { key: "mergedPullRequests", label: "PRs merged" },
  { key: "reviews", label: "Reviews" },
] as const;
function activityColor(count: number): string {
  if (count === 0) return "bg-surface-subtle text-secondary";
  if (count <= 2) return "bg-success-soft text-success-deep";
  if (count <= 4) return "bg-success-medium text-success-deep";
  if (count <= 6) return "bg-success-strong text-on-color";
  return "bg-success-deep text-on-color";
}
export const metadata = { title: "Collaboration Heatmap" };
export default function HeatmapPage({
  searchParams = {},
}: {
  searchParams?: { range?: string | string[] };
}): React.JSX.Element {
  const range = parseDashboardRange(searchParams.range);
  const { activity, period } = selectDashboard(sampleDashboard, range);
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
        <div className="overflow-x-auto">
          <table className="w-full min-w-[480px] table-fixed border-separate border-spacing-2 text-center text-xs">
            <caption className="sr-only">
              Sample team activity for {period}. Each cell shows an event count.
            </caption>
            <thead>
              <tr>
                <th scope="col" className="w-28" />
                {activity.map((day) => (
                  <th
                    scope="col"
                    key={day.date}
                    className="pb-2 font-normal text-muted"
                  >
                    {day.day}
                    <span className="mt-1 block text-[10px]">{day.date}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.key}>
                  <th
                    scope="row"
                    className="text-left font-medium text-secondary"
                  >
                    {row.label}
                  </th>
                  {activity.map((day) => (
                    <td
                      key={day.date}
                      className={`h-12 rounded font-semibold ${activityColor(day[row.key])}`}
                    >
                      {day[row.key]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex justify-end gap-1.5 text-[10px] text-muted">
          <span>Less</span>
          {[0, 1, 3, 5, 8].map((count) => (
            <span
              key={count}
              aria-hidden="true"
              className={`h-3 w-3 rounded-sm ${activityColor(count)}`}
            />
          ))}
          <span>More activity</span>
        </div>
      </Panel>
    </div>
  );
}
