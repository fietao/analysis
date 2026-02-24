import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Fiscal AI 2.0 | Advanced Analytics",
  description: "Elite Financial Analysis Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen flex bg-background`}>
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-8 lg:p-12">
          {children}
        </main>
      </body>
    </html>
  );
}
