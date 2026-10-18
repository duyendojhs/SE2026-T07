import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardView } from "@/features/dashboard/components/DashboardView";
import { sampleDashboard } from "@/mocks/dashboard";
import HeatmapPage from "@/app/heatmap/page";
vi.mock("next/navigation", () => ({ usePathname: () => "/stale-alerts" }));
describe("dashboard interactions", () => {
  it("nests analysis links under Dashboard and leaves Audit Logs in System", () => {
    render(<AppShell>Content</AppShell>);
    const nav = screen.getByRole("navigation", { name: "Main navigation" });
    const dashboard = within(nav).getByRole("group", { name: "Dashboard" });
    expect(
      within(dashboard).getByRole("link", { name: "Collaboration Heatmap" }),
    ).toBeInTheDocument();
    expect(
      within(dashboard).getByRole("link", { name: "Stale Alerts" }),
    ).toHaveAttribute("aria-current", "page");
    expect(
      within(within(nav).getByRole("group", { name: "System" })).getByRole(
        "link",
        { name: "Audit Logs" },
      ),
    ).toBeInTheDocument();
  });
  it("updates period metrics and detail links while preserving snapshot counts", () => {
    render(<DashboardView data={sampleDashboard} />);
    expect(screen.getByLabelText("Merged PRs: 5")).toBeInTheDocument();
    expect(
      screen.getByLabelText("Median review wait: 18h"),
    ).toBeInTheDocument();
    fireEvent.change(screen.getByRole("combobox", { name: "Period" }), {
      target: { value: "3d" },
    });
    expect(screen.getByLabelText("Merged PRs: 1")).toBeInTheDocument();
    expect(
      screen.getByLabelText("Median review wait: 30h"),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Awaiting review: 3")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "View details" })).toHaveAttribute(
      "href",
      "/heatmap?range=3d",
    );
    expect(
      screen.getByRole("region", { name: "Period summary" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("img", { name: /Activity by day: Fri/ }),
    ).toBeInTheDocument();
  });
  it("handles missing activity and limits attention preview to three entries", () => {
    render(
      <DashboardView
        data={{
          ...sampleDashboard,
          activity: [],
          alerts: [
            ...sampleDashboard.alerts,
            { ...sampleDashboard.alerts[0], id: "PR #30" },
            { ...sampleDashboard.alerts[0], id: "PR #31" },
          ],
        }}
      />,
    );
    expect(screen.getByLabelText("Median review wait: —")).toBeInTheDocument();
    expect(screen.getByText("No activity in this period.")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "View all (4)" }),
    ).toBeInTheDocument();
    expect(screen.queryByText(/PR #31/)).not.toBeInTheDocument();
  });
  it("renders detailed heatmap and preserves the selected range on return", () => {
    render(<HeatmapPage searchParams={{ range: "3d" }} />);
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute(
      "href",
      "/?range=3d",
    );
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.queryByText("Mon")).not.toBeInTheDocument();
    expect(screen.getByText("Fri")).toBeInTheDocument();
  });
});
