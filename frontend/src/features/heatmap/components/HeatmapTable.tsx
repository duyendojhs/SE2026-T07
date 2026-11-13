import type { ActivityDay } from "@/domain/analytics";
import { heatmapRows, activityColor } from "../model";

export function HeatmapTable({
  activity,
  period,
}: {
  activity: ActivityDay[];
  period: string;
}): React.JSX.Element {
  return (
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
          {heatmapRows.map((row) => (
            <tr key={row.key}>
              <th scope="row" className="text-left font-medium text-secondary">
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
  );
}
