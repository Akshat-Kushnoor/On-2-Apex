"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Briefcase,
  Compass,
  FileText,
  GraduationCap,
  Kanban,
  LayoutDashboard,
  Settings,
  User,
} from "lucide-react";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Profile", href: "/profile", icon: User },
  { label: "Job Search", href: "/jobs", icon: Briefcase },
  { label: "Learning Plan", href: "/learning", icon: GraduationCap },
  { label: "Resume Studio", href: "/resumes", icon: FileText },
  { label: "Workspace", href: "/workspace", icon: Kanban },
  { label: "Settings", href: "/settings", icon: Settings },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r-2 border-black bg-white flex flex-col justify-between h-[calc(100vh-65px)] sticky top-[65px]">
      <div className="p-4 space-y-2">
        <div className="text-[10px] font-black uppercase tracking-widest text-neutral-400 px-3 mb-2">
          Navigation
        </div>
        <nav className="space-y-1.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname?.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-[5px] text-xs font-black tracking-wide border-2 transition-all ${
                  isActive
                    ? "bg-black text-white border-black shadow-[3px_3px_0px_#000]"
                    : "bg-white text-black border-transparent hover:border-black hover:bg-neutral-50"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="p-4 border-t-2 border-black bg-neutral-50">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs font-black">AI PLACEMENT</div>
            <div className="text-[10px] font-bold text-neutral-500">v1.0 Local Edition</div>
          </div>
          <div className="w-3 h-3 rounded-full bg-black border-2 border-black" />
        </div>
      </div>
    </aside>
  );
};
