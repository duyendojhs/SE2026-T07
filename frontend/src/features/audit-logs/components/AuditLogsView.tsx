import { ScrollText } from "lucide-react";
import { EmptyState } from "@/shared/components/ui/EmptyState";

export function AuditLogsView(): React.JSX.Element {
  return (
    <EmptyState
      title="Audit Logs"
      description="Understand when metadata is accessed and processed."
      icon={ScrollText}
      detail="API access timestamps, target repositories, and quota costs will appear when the backend audit service is connected."
    />
  );
}
