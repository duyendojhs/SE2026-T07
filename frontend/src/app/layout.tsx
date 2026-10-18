import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "GitHub Project Coach",
  description: "Explainable insights from GitHub collaboration metadata.",
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>): React.JSX.Element {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
