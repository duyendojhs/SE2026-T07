import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import NotFound from "@/app/not-found";
it("provides a Dashboard destination for unknown pages", () => {
  render(<NotFound />);
  expect(
    screen.getByRole("heading", { level: 1, name: "Page not found" }),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "Return to Dashboard" }),
  ).toHaveAttribute("href", "/");
});
