import { activityColor } from "../model";

export function HeatmapLegend(): React.JSX.Element {
  return (
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
  );
}
