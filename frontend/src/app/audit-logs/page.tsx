import { AuditLogsView } from "@/features/audit-logs";

export const metadata = { title: "Audit Logs" };

export default function AuditPage(): React.JSX.Element {
  return <AuditLogsView />;
}
