import Link from "next/link";
import { PageHeader } from "@/components/layout/PageHeader";

export default function NotFound(): React.JSX.Element {
  return (
    <section className="space-y-5 rounded-lg border border-line bg-surface p-6">
      <PageHeader
        title="Page not found"
        meta="The requested page does not exist."
      />
      <Link
        href="/"
        className="inline-block text-sm text-primary hover:underline"
      >
        Return to Dashboard
      </Link>
    </section>
  );
}
