import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EPA rules tracker",
  description: "Recent EPA final rules from the Federal Register",
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
