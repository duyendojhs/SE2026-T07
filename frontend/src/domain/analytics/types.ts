/**
 * Domain contracts shared by the dashboard, heatmap, and stale-alert views.
 * Keep this module independent from fixtures, UI, and feature implementations.
 */

export type DashboardRange = "7d" | "3d";

export type ActivityDay = {
  day: string;
  date: string;
  commits: number;
  pullRequests: number;
  mergedPullRequests: number;
  reviews: number;
};

export type CollaborationAlert = {
  id: string;
  title: string;
  reason: string;
  rule: string;
  metric: string;
  label: string;
};
