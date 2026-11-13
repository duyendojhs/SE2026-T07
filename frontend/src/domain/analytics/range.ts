import type { DashboardRange } from "./types";

/** Normalizes a URL range value to a supported analytics period. */
export function parseDashboardRange(value?: string | string[]): DashboardRange {
  return value === "3d" ? "3d" : "7d";
}
