import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import TopNav from "@/components/TopNav";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Jarvis | Advanced Analytics",
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
        <main className="flex-1 overflow-y-auto px-8 lg:px-12 pb-12">
          <TopNav />
          {children}
        </main>
      </body>
    </html>
  );
}
