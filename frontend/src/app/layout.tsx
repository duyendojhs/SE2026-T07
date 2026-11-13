import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/shared/components/layout";
import { RateLimitGauge, sampleQuota } from "@/features/telemetry";

export const metadata: Metadata = {
  title: {
    default: "GitHub Project Coach",
    template: "%s | GitHub Project Coach",
  },
  description: "Explainable insights from GitHub collaboration metadata.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>): React.JSX.Element {
  return (
    <html lang="en">
      <body>
        <AppShell quotaSlot={<RateLimitGauge quota={sampleQuota} />}>
          {children}
        </AppShell>
      </body>
    </html>
  );
}
