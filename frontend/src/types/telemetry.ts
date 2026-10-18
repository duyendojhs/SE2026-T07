export type RateLimitQuota = {
  remaining: number;
  limit: number;
  resetAt: string | null;
};
