import type { RateLimitQuota } from "@/types/telemetry";
import {
  getQuotaRatio,
  getQuotaLevel,
  formatQuotaReset,
} from "@/lib/rate-limit";
export function RateLimitGauge({
  quota,
}: {
  quota: RateLimitQuota | null;
}): React.JSX.Element {
  const ratio = getQuotaRatio(quota);
  const percentage = (ratio ?? 0) * 100;
  const reset = formatQuotaReset(quota?.resetAt ?? null);
  return (
    <div className="w-full sm:w-64">
      <div className="mb-2 flex items-center justify-between gap-3 text-xs">
        <span className="font-medium text-secondary">GitHub API quota</span>
      </div>
      {ratio !== null && quota ? (
        <>
          <div
            role="progressbar"
            aria-label="GitHub API quota remaining"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.round(percentage)}
            aria-valuetext={`${quota.remaining} of ${quota.limit} requests remaining`}
            className="h-1.5 overflow-hidden rounded-full bg-surface-subtle"
          >
            <div
              style={{ width: `${percentage}%` }}
              className={`h-full rounded-full ${getQuotaLevel(ratio) === "warning" ? "bg-warning" : "bg-success"}`}
            />
          </div>
          <p className="mt-1.5 text-xs text-secondary">
            {quota.remaining.toLocaleString("en-US")} /{" "}
            {quota.limit.toLocaleString("en-US")} remaining
            {reset && <span className="ml-2">· Resets {reset}</span>}
          </p>
        </>
      ) : (
        <p className="text-xs text-secondary">Quota unavailable</p>
      )}
    </div>
  );
}
