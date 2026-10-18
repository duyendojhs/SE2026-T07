import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitGauge } from "@/components/telemetry/RateLimitGauge";
import { sampleQuota } from "@/mocks/rate-limit";
describe("quota", () => {
  it("shows fixture values and an accessible percentage", () => {
    render(<RateLimitGauge quota={sampleQuota} />);
    expect(screen.getByRole("progressbar")).toHaveAttribute(
      "aria-valuenow",
      "85",
    );
    expect(screen.getByText("4,250 / 5,000 remaining")).toBeInTheDocument();
  });
  it("handles exhausted quota", () => {
    render(<RateLimitGauge quota={{ ...sampleQuota, remaining: 0 }} />);
    expect(screen.getByRole("progressbar")).toHaveAttribute(
      "aria-valuenow",
      "0",
    );
  });
  it.each([
    null,
    { ...sampleQuota, limit: 0 },
    { ...sampleQuota, remaining: -1 },
  ])("handles unavailable or invalid quota", (quota) => {
    render(<RateLimitGauge quota={quota} />);
    expect(screen.getByText("Quota unavailable")).toBeInTheDocument();
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });
});
