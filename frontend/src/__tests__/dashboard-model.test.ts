import { describe, expect, it } from "vitest";
import {
  median,
  parseDashboardRange,
  selectDashboard,
} from "@/features/dashboard/model";
import { sampleDashboard } from "@/mocks/dashboard";
describe("dashboard calculations", () => {
  it("calculates median without changing input and excludes invalid durations", () => {
    const values = [24, 12, 18];
    expect(median(values)).toBe(18);
    expect(values).toEqual([24, 12, 18]);
    expect(median([10, 20])).toBe(15);
    expect(median([-1, Number.NaN, Number.POSITIVE_INFINITY, 0])).toBe(0);
    expect(median([])).toBeNull();
  });
  it("derives selected-period counts and keeps stale classification specific", () => {
    expect(selectDashboard(sampleDashboard, "7d")).toMatchObject({
      merged: 5,
      reviews: 17,
      opened: 9,
      medianWait: 18,
      staleCount: 1,
    });
    expect(selectDashboard(sampleDashboard, "3d")).toMatchObject({
      merged: 1,
      reviews: 6,
      opened: 3,
      medianWait: 30,
    });
    expect(
      selectDashboard({ ...sampleDashboard, activity: [] }, "7d"),
    ).toMatchObject({ merged: 0, medianWait: null, period: "No activity" });
  });
  it("normalizes URL ranges", () => {
    expect(parseDashboardRange("3d")).toBe("3d");
    expect(parseDashboardRange("unknown")).toBe("7d");
    expect(parseDashboardRange(["3d"])).toBe("7d");
  });
});
