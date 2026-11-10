import fixture from "../../../../backend/tests/mocks/dashboard.json";
import type { DashboardData } from "./types";

/**
 * Adapter module reading the offline fixture data.
 * Isolated here so UI components only consume strongly typed domain models.
 */
export const sampleDashboard: DashboardData = fixture;
