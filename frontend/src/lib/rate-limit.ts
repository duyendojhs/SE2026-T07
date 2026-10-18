import type { RateLimitQuota } from "@/types/telemetry";

export function getQuotaRatio(quota: RateLimitQuota | null): number | null {
  if (
    !quota ||
    !Number.isFinite(quota.limit) ||
    quota.limit <= 0 ||
    !Number.isFinite(quota.remaining) ||
    quota.remaining < 0 ||
    quota.remaining > quota.limit
  )
    return null;
  return quota.remaining / quota.limit;
}

export function getQuotaLevel(
  ratio: number | null,
): "unknown" | "warning" | "healthy" {
  return ratio === null ? "unknown" : ratio <= 0.2 ? "warning" : "healthy";
}

export function formatQuotaReset(resetAt: string | null): string | null {
  if (!resetAt) return null;
  const reset = new Date(resetAt);
  if (Number.isNaN(reset.getTime())) return null;
  return `${reset.toISOString().slice(11, 16)} UTC`;
}
