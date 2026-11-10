import { env } from "./env";

/**
 * Centralized API route definitions matching backend contracts.
 */
export const apiRoutes = {
  health: `${env.apiUrl}/health`,
  ready: `${env.apiUrl}/ready`,
  auth: {
    login: `${env.apiUrl}/api/v1/auth/github/login`,
    install: `${env.apiUrl}/api/v1/auth/github/install`,
    logout: `${env.apiUrl}/api/v1/auth/logout`,
    me: `${env.apiUrl}/api/v1/me`,
  },
  tenants: {
    repos: (slug: string) => `${env.apiUrl}/api/v1/tenants/${slug}/repos`,
    sync: (slug: string, repoId: string) =>
      `${env.apiUrl}/api/v1/tenants/${slug}/repos/${repoId}/sync`,
    audit: (slug: string) => `${env.apiUrl}/api/v1/tenants/${slug}/audit`,
    verifyAudit: (slug: string) =>
      `${env.apiUrl}/api/v1/tenants/${slug}/audit/verify`,
  },
} as const;
