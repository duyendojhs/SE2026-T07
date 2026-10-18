import type {
  ActivityDay,
  DashboardData,
  DashboardRange,
} from "@/types/dashboard";

export function parseDashboardRange(value?: string | string[]): DashboardRange {
  return value === "3d" ? "3d" : "7d";
}

export function median(values: number[]): number | null {
  const sorted = values
    .filter((value) => Number.isFinite(value) && value >= 0)
    .sort((a, b) => a - b);
  if (!sorted.length) return null;
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2
    ? sorted[middle]
    : (sorted[middle - 1] + sorted[middle]) / 2;
}

export function selectDashboard(
  data: DashboardData,
  range: DashboardRange,
): {
  activity: ActivityDay[];
  period: string;
  merged: number;
  reviews: number;
  opened: number;
  medianWait: number | null;
  staleCount: number;
} {
  const activity = data.activity.slice(range === "3d" ? -3 : -7);
  return {
    activity,
    period: activity.length
      ? `${activity[0].date} – ${activity[activity.length - 1].date} ${data.year}`
      : "No activity",
    merged: activity.reduce((sum, day) => sum + day.mergedPullRequests, 0),
    reviews: activity.reduce((sum, day) => sum + day.reviews, 0),
    opened: activity.reduce((sum, day) => sum + day.pullRequests, 0),
    medianWait: median(activity.flatMap((day) => day.reviewWaitHours)),
    staleCount: data.alerts.filter((alert) => alert.rule === "STALE_PR").length,
  };
}
