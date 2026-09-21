"use client";

import { healthService } from "@/services/health";
import { LogOut, User as UserIcon } from "lucide-react";
import Link from "next/link";
import React, { useEffect, useState } from "react";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { useAuth } from "@/firebase/AuthContext";

export const Topbar: React.FC = () => {
  const { user, token, logout } = useAuth();
  const [isReady, setIsReady] = useState<boolean>(true);

  useEffect(() => {
    healthService.checkHealth().then((healthy) => setIsReady(healthy));
  }, []);

  const handleLogout = async () => {
    await logout();
    window.location.href = "/login";
  };

  return (
    <header className="h-[65px] border-b-2 border-black bg-white px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-black text-white px-2.5 py-1 text-base font-black rounded-[5px] border-2 border-black tracking-wider">
            ON2
          </div>
          <span className="text-base font-black tracking-tight text-black">APEX</span>
        </Link>
        <Badge variant={isReady ? "highlight" : "outline"} className="text-[10px]">
          {isReady ? "LIVE CORE" : "OFFLINE"}
        </Badge>
      </div>

      <div className="flex items-center gap-3">
        {token ? (
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-1.5 text-xs font-bold text-neutral-700">
              <UserIcon className="w-3.5 h-3.5" />
              <span>{user?.full_name || user?.email || "Student"}</span>
            </div>
            <Badge variant="default" className="text-xs">
              ACTIVE SESSION
            </Badge>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleLogout}
              className="flex items-center gap-1.5 border-2 border-black shadow-[2px_2px_0px_#000]"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Logout</span>
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link href="/login">
              <Button variant="secondary" size="sm" className="border-2 border-black shadow-[2px_2px_0px_#000]">
                Login
              </Button>
            </Link>
            <Link href="/register">
              <Button variant="primary" size="sm" className="shadow-[2px_2px_0px_#000]">
                Register
              </Button>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
