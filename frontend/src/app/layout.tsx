import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";
import { sampleQuota } from "@/mocks/rate-limit";
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
        <AppShell quota={sampleQuota}>{children}</AppShell>
      </body>
    </html>
  );
}
