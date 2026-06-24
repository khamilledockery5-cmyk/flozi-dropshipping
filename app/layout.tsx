import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trade AI",
  description: "An AI-powered trading assistant.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
