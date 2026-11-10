import { expect, it } from "vitest";
import { cn } from "@/shared/lib/cn";

it("merges conditional classes and resolves Tailwind conflicts", () => {
  expect(
    cn("p-4 bg-surface", false && "hidden", { "text-primary": true }, "p-6"),
  ).toBe("bg-surface text-primary p-6");
});
