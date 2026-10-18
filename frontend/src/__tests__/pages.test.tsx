import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DashboardPage from "@/app/page";
import HeatmapPage from "@/app/heatmap/page";
import AlertsPage from "@/app/stale-alerts/page";
import AuditPage from "@/app/audit-logs/page";
describe("pages", () => {
  it.each([
    [DashboardPage, "Dashboard"],
    [HeatmapPage, "Collaboration Heatmap"],
    [AlertsPage, "Stale Alerts"],
    [AuditPage, "Audit Logs"],
  ] as const)("renders page heading", (Page, title) => {
    render(<Page />);
    expect(
      screen.getByRole("heading", { level: 1, name: title }),
    ).toBeInTheDocument();
  });
});
