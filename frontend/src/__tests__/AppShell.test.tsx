import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppShell } from "@/components/layout/AppShell";
vi.mock("next/navigation", () => ({ usePathname: () => "/stale-alerts" }));
describe("dashboard shell", () => {
  it("marks the current route and renders all navigation destinations", () => {
    render(<AppShell>Page content</AppShell>);
    const nav = screen.getByRole("navigation", { name: "Main navigation" });
    expect(within(nav).getAllByRole("link")).toHaveLength(4);
    expect(
      within(nav).getByRole("link", { name: "Stale Alerts" }),
    ).toHaveAttribute("aria-current", "page");
    expect(
      within(nav).getByRole("link", { name: "Dashboard" }),
    ).not.toHaveAttribute("aria-current");
  });
  it("opens the mobile dialog and closes on navigation, cancel, and backdrop", () => {
    render(<AppShell>Content</AppShell>);
    const trigger = screen.getByRole("button", { name: "Open navigation" });
    fireEvent.click(trigger);
    let dialog = screen.getByRole("dialog");
    expect(document.body.style.overflow).toBe("hidden");
    const destination = within(dialog).getByRole("link", {
      name: "Audit Logs",
    });
    destination.addEventListener("click", (event) => event.preventDefault());
    fireEvent.click(destination);
    expect(trigger).toHaveAttribute("aria-expanded", "false");
    expect(document.body.style.overflow).toBe("");
    fireEvent.click(trigger);
    dialog = screen.getByRole("dialog");
    fireEvent(dialog, new Event("cancel", { bubbles: true }));
    expect(trigger).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole("dialog"));
    expect(trigger).toHaveAttribute("aria-expanded", "false");
  });
});
