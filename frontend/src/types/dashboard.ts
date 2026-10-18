export type DashboardRange = "7d" | "3d";
export type ActivityDay = {
  day: string;
  date: string;
  commits: number;
  pullRequests: number;
  mergedPullRequests: number;
  reviews: number;
  reviewWaitHours: number[];
};
export type CollaborationAlert = {
  id: string;
  title: string;
  reason: string;
  rule: string;
  metric: string;
  label: string;
};
export type DashboardData = {
  repository: string;
  period: string;
  year: number;
  awaitingReview: number;
  alerts: CollaborationAlert[];
  activity: ActivityDay[];
};
