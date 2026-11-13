import { describe, expect, it } from "vitest";
import {
  parseDashboardRange,
  type ActivityDay,
  type CollaborationAlert,
} from "@/domain/analytics";

describe("shared analytics domain contracts", () => {
  it("keeps shared activity and alert shapes usable by multiple features", () => {
    const activity: ActivityDay = {
      day: "Mon",
      date: "12 Oct",
      commits: 4,
      pullRequests: 1,
      mergedPullRequests: 1,
      reviews: 2,
    };
    const alert: CollaborationAlert = {
      id: "PR #24",
      title: "Metadata ingestion pipeline",
      reason: "No review received for 3 days",
      rule: "REVIEW_WAIT",
      metric: "72 hours without a review",
      label: "Review needed",
    };

    expect(activity.pullRequests).toBe(1);
    expect(alert.rule).toBe("REVIEW_WAIT");
  });

  it("normalizes supported URL range values", () => {
    expect(parseDashboardRange("3d")).toBe("3d");
    expect(parseDashboardRange("7d")).toBe("7d");
    expect(parseDashboardRange("unknown")).toBe("7d");
    expect(parseDashboardRange(["3d"])).toBe("7d");
  });
});
