import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Demo — Pathfinding based on Classified Avalanche Terrain",
  description:
    "Find the path with the lowest risk for avalanches between two points in Switzerland.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
