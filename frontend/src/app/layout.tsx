import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Niryat AI - Export Intelligence Platform",
  description: "AI-Guided Export Readiness and Intelligence Platform for Indian MSMEs",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
