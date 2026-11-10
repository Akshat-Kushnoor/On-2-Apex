"use client";

import React from "react";
import Link from "next/link";
import { LogOut, PanelLeft, PanelLeftClose, User as UserIcon } from "lucide-react";
import { Button } from "../ui/button";
import { useAuth } from "@/firebase/AuthContext";

interface TopbarProps {
  isLoggedIn?: boolean;
  isSidebarOpen?: boolean;
  onToggleSidebar?: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  isLoggedIn,
  isSidebarOpen = true,
  onToggleSidebar,
}) => {
  const { user, token, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    window.location.href = "/login";
  };

  return (
    <header className="h-[65px] border-b-2 border-black bg-white px-6 flex items-center justify-between sticky top-0 z-40 select-none">
      <div className="flex items-center gap-3">
        {isLoggedIn && onToggleSidebar && (
          <button
            type="button"
            onClick={onToggleSidebar}
            className="p-2 rounded-[5px] border-2 border-black bg-white hover:bg-neutral-100 shadow-[2px_2px_0px_#000] text-black transition-all flex items-center justify-center shrink-0"
            title={isSidebarOpen ? "Collapse Navigation" : "Expand Navigation"}
          >
            {isSidebarOpen ? (
              <PanelLeftClose className="w-4 h-4" />
            ) : (
              <PanelLeft className="w-4 h-4" />
            )}
          </button>
        )}
        <Link href="/" className="flex items-center gap-2.5">
          <div className="bg-black text-white px-2.5 py-1 text-xs font-black rounded-[4px] border-2 border-black tracking-widest uppercase shadow-[2px_2px_0px_#000]">
            ON2 APEX
          </div>
        </Link>
      </div>

      <div className="flex items-center gap-3">
        {token ? (
          <div className="flex items-center gap-2.5">
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold text-black bg-neutral-50 border-2 border-black rounded-[4px] shadow-[1px_1px_0px_#000]">
              <UserIcon className="w-3.5 h-3.5 text-neutral-600" />
              <span className="font-mono">{user?.full_name || user?.email || "Candidate"}</span>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleLogout}
              className="flex items-center gap-1.5 border-2 border-black shadow-[2px_2px_0px_#000] text-xs font-black uppercase"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Logout</span>
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link href="/login">
              <Button variant="secondary" size="sm" className="border-2 border-black shadow-[2px_2px_0px_#000] text-xs font-black uppercase">
                Login
              </Button>
            </Link>
            <Link href="/register">
              <Button variant="primary" size="sm" className="shadow-[2px_2px_0px_#000] text-xs font-black uppercase">
                Register
              </Button>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
