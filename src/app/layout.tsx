import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Off-Grid: Safe Ski Tour Planning",
  description:
    "Explore Switzerland safely with Off-Grid's intelligent pathfinding tool, optimized for low-risk routes in classified avalanche terrain.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
        {children}
      </body>
    </html>
  );
}
