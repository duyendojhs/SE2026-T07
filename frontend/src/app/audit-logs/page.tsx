import { ScrollText } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";
export const metadata = { title: "Audit Logs" };
export default function AuditPage(): React.JSX.Element {
  return (
    <EmptyState
      title="Audit Logs"
      description="Understand when metadata is accessed and processed."
      icon={ScrollText}
      detail="API access timestamps, target repositories, and quota costs will appear when the backend audit service is connected."
    />
  );
}
