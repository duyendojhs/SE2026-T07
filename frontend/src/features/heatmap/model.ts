export const heatmapRows = [
  { key: "commits", label: "Commits" },
  { key: "pullRequests", label: "PRs opened" },
  { key: "mergedPullRequests", label: "PRs merged" },
  { key: "reviews", label: "Reviews" },
] as const;

export type HeatmapRowKey = (typeof heatmapRows)[number]["key"];

export function activityColor(count: number): string {
  if (count === 0) return "bg-surface-subtle text-secondary";
  if (count <= 2) return "bg-success-soft text-success-deep";
  if (count <= 4) return "bg-success-medium text-success-deep";
  if (count <= 6) return "bg-success-strong text-on-color";
  return "bg-success-deep text-on-color";
}
