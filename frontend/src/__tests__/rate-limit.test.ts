import { describe, expect, it } from "vitest";
import {
  getQuotaRatio,
  getQuotaLevel,
  formatQuotaReset,
} from "@/lib/rate-limit";
import { sampleQuota } from "@/mocks/rate-limit";

describe("quota calculations", () => {
  it("handles ratio bounds and invalid quota", () => {
    expect(getQuotaRatio(sampleQuota)).toBe(0.85);
    expect(getQuotaRatio({ ...sampleQuota, remaining: 0 })).toBe(0);
    expect(getQuotaRatio({ ...sampleQuota, remaining: 5000 })).toBe(1);
    for (const quota of [
      null,
      { ...sampleQuota, limit: 0 },
      { ...sampleQuota, remaining: -1 },
      { ...sampleQuota, remaining: 5001 },
      { ...sampleQuota, remaining: NaN },
    ])
      expect(getQuotaRatio(quota)).toBeNull();
  });
  it("classifies the remaining fraction", () => {
    expect(getQuotaLevel(null)).toBe("unknown");
    expect(getQuotaLevel(0)).toBe("warning");
    expect(getQuotaLevel(0.2)).toBe("warning");
    expect(getQuotaLevel(0.21)).toBe("healthy");
  });
  it("formats reset time in UTC without depending on the machine timezone", () => {
    expect(formatQuotaReset("2026-10-18T13:25:00Z")).toBe("13:25 UTC");
    expect(formatQuotaReset(null)).toBeNull();
    expect(formatQuotaReset("invalid")).toBeNull();
  });
});
