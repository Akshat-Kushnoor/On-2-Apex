import type { Metadata } from "next";
import React from "react";
import "./globals.css";
import { AuthProvider } from "@/firebase/AuthContext";

export const metadata: Metadata = {
  title: "ON-2-APEX — AI Placement Coach",
  description: "Personal local-first placement operating system for engineering students.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-neutral-50 text-black flex flex-col font-sans">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
