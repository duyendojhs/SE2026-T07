import {
  Activity,
  LayoutDashboard,
  ScrollText,
  TriangleAlert,
} from "lucide-react";
export const navigation = [
  {
    href: "/",
    label: "Dashboard",
    group: "dashboard",
    icon: LayoutDashboard,
    description: "Your project at a glance",
  },
  {
    href: "/heatmap",
    label: "Collaboration Heatmap",
    group: "analytics",
    icon: Activity,
    description: "Explore collaboration patterns",
  },
  {
    href: "/stale-alerts",
    label: "Stale Alerts",
    group: "analytics",
    icon: TriangleAlert,
    description: "Spot work that needs attention",
  },
  {
    href: "/audit-logs",
    label: "Audit Logs",
    group: "system",
    icon: ScrollText,
    description: "Inspect metadata processing activity",
  },
] as const;
