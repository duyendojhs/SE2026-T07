import type { ActivityDay, CollaborationAlert } from "@/domain/analytics";

export type DashboardActivityDay = ActivityDay & {
  reviewWaitHours: number[];
};

export type DashboardData = {
  repository: string;
  period: string;
  year: number;
  awaitingReview: number;
  alerts: CollaborationAlert[];
  activity: DashboardActivityDay[];
};

export type DashboardMetric = {
  label: string;
  value: string | number;
  hint: string;
  color: string;
  scope: string;
};

export type ActivitySummary = {
  activity: DashboardActivityDay[];
  period: string;
  merged: number;
  reviews: number;
  opened: number;
  medianWait: number | null;
  staleCount: number;
};
