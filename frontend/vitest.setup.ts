import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";
afterEach(cleanup);
Object.defineProperty(window, "matchMedia", {
  value: vi.fn(() => ({
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  })),
});
HTMLDialogElement.prototype.showModal = function (): void {
  this.setAttribute("open", "");
};
HTMLDialogElement.prototype.close = function (): void {
  this.removeAttribute("open");
};
