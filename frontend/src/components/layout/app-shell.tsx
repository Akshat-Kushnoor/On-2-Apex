"use client";

import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { Topbar } from "./topbar";
import { Sidebar } from "./sidebar";
import { useAuth } from "@/firebase/AuthContext";

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const { token, loading } = useAuth();
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [hasStoredToken, setHasStoredToken] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("token");
      setHasStoredToken(!!stored);
    }
  }, [token]);

  const isAuthPage =
    pathname === "/login" ||
    pathname === "/register" ||
    pathname === "/reset-password";

  const isLoggedIn = (!!token || hasStoredToken) && !isAuthPage;

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col">
      <Topbar
        isLoggedIn={isLoggedIn}
        isSidebarOpen={isSidebarOpen}
        onToggleSidebar={toggleSidebar}
      />
      <div className="flex flex-1 relative overflow-x-hidden">
        {isLoggedIn && <Sidebar isOpen={isSidebarOpen} />}
        <main className="flex-1 p-8 max-w-7xl mx-auto w-full transition-all duration-300 ease-in-out">
          {children}
        </main>
      </div>
    </div>
  );
};
