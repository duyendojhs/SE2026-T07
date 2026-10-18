import fixture from "../../../backend/tests/mocks/dashboard.json";
import type { DashboardData } from "@/types/dashboard";

// The adapter is the only dashboard module aware of the offline fixture location.
export const sampleDashboard: DashboardData = fixture;
