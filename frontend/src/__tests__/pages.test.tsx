import { render, screen, within } from "@testing-library/react";
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

  it("keeps stale alert details and the selected range on the route", () => {
    render(<AlertsPage searchParams={{ range: "3d" }} />);

    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute(
      "href",
      "/?range=3d",
    );
    const alert = screen.getAllByRole("article")[0];
    expect(within(alert).getByText("REVIEW_WAIT")).toBeInTheDocument();
    expect(
      within(alert).getByText("72 hours without a review"),
    ).toBeInTheDocument();
  });
});
