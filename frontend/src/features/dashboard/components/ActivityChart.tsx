import type { ActivityDay } from "@/types/dashboard";

const series = [
  { key: "pullRequests", label: "PRs opened", color: "bg-primary" },
  { key: "mergedPullRequests", label: "PRs merged", color: "bg-success" },
  { key: "reviews", label: "Reviews", color: "bg-chart-review" },
] as const;

export function ActivityChart({
  days,
}: {
  days: ActivityDay[];
}): React.JSX.Element {
  const maximum = Math.max(
    1,
    ...days.flatMap((day) => series.map((item) => day[item.key])),
  );
  if (!days.length)
    return (
      <p className="py-16 text-center text-sm text-muted">
        No activity in this period.
      </p>
    );
  return (
    <>
      <div className="mb-5 flex flex-wrap gap-4 text-xs text-secondary">
        {series.map((item) => (
          <span key={item.key} className="inline-flex items-center gap-1.5">
            <span className={`h-2 w-2 rounded-sm ${item.color}`} />
            {item.label}
          </span>
        ))}
      </div>
      <div className="flex gap-3">
        <div
          aria-hidden="true"
          className="flex h-44 flex-col justify-between pb-1 text-[10px] text-muted"
        >
          <span>{maximum}</span>
          <span>{Math.round(maximum / 2)}</span>
          <span>0</span>
        </div>
        <div
          role="img"
          aria-label={`Activity by day: ${days.map((day) => `${day.day}, ${day.pullRequests} PRs opened, ${day.mergedPullRequests} PRs merged, ${day.reviews} reviews`).join("; ")}`}
          className="flex min-w-0 flex-1 gap-2"
        >
          {days.map((day) => (
            <div key={day.date} className="min-w-0 flex-1 text-center">
              <div className="flex h-44 items-end justify-center gap-1 border-b border-line bg-[linear-gradient(to_top,transparent_49%,var(--border)_50%,transparent_51%)]">
                {series.map((item) => (
                  <div
                    key={item.key}
                    title={`${day.date}: ${day[item.key]} ${item.label}`}
                    className={`w-2 rounded-t-sm sm:w-3 ${item.color}`}
                    style={{ height: `${(day[item.key] / maximum) * 100}%` }}
                  />
                ))}
              </div>
              <p className="mt-3 text-[10px] text-muted">{day.day}</p>
            </div>
          ))}
        </div>
      </div>
      <details className="mt-4 text-xs text-muted">
        <summary className="w-fit cursor-pointer hover:text-primary">
          View values
        </summary>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left">
            <caption className="sr-only">Daily PR and review counts</caption>
            <thead>
              <tr>
                <th scope="col" className="py-2">
                  Date
                </th>
                {series.map((item) => (
                  <th scope="col" key={item.key} className="px-2">
                    {item.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {days.map((day) => (
                <tr key={day.date}>
                  <th scope="row" className="py-1 font-normal">
                    {day.date}
                  </th>
                  {series.map((item) => (
                    <td className="px-2" key={item.key}>
                      {day[item.key]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </>
  );
}
