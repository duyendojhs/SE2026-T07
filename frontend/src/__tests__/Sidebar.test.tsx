import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Sidebar } from "@/components/layout/Sidebar";
vi.mock("next/navigation", () => ({ usePathname: () => "/heatmap" }));
describe("sidebar routes", () => {
  it("uses the flat heatmap URL and marks only the current page", () => {
    render(<Sidebar />);
    const nav = screen.getByRole("navigation", { name: "Main navigation" });
    expect(
      within(nav).getByRole("link", { name: "Collaboration Heatmap" }),
    ).toHaveAttribute("href", "/heatmap");
    expect(
      within(nav).getByRole("link", { name: "Collaboration Heatmap" }),
    ).toHaveAttribute("aria-current", "page");
    expect(
      within(nav).getByRole("link", { name: "Dashboard" }),
    ).not.toHaveAttribute("aria-current");
  });
});
