import { describe, expect, it } from "vitest";
import type { ActivityDay } from "@/domain/analytics";
import { selectHeatmapActivity } from "@/features/heatmap";

const activity: ActivityDay[] = [
  {
    day: "Mon",
    date: "12 Oct",
    commits: 1,
    pullRequests: 0,
    mergedPullRequests: 0,
    reviews: 0,
  },
  {
    day: "Tue",
    date: "13 Oct",
    commits: 2,
    pullRequests: 1,
    mergedPullRequests: 1,
    reviews: 1,
  },
  {
    day: "Wed",
    date: "14 Oct",
    commits: 3,
    pullRequests: 1,
    mergedPullRequests: 0,
    reviews: 2,
  },
  {
    day: "Thu",
    date: "15 Oct",
    commits: 4,
    pullRequests: 2,
    mergedPullRequests: 1,
    reviews: 3,
  },
];

describe("heatmap activity selection", () => {
  it("selects the requested trailing period and labels it", () => {
    expect(selectHeatmapActivity(activity, "3d", 2026)).toEqual({
      activity: activity.slice(-3),
      period: "13 Oct – 15 Oct 2026",
    });
    expect(selectHeatmapActivity(activity, "7d", 2026)).toEqual({
      activity,
      period: "12 Oct – 15 Oct 2026",
    });
  });

  it("handles an empty period", () => {
    expect(selectHeatmapActivity([], "7d", 2026)).toEqual({
      activity: [],
      period: "No activity",
    });
  });
});
