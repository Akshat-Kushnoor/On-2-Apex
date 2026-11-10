"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/firebase/AuthContext";
import { profileService } from "@/services/profile";
import { resumeService } from "@/services/resumes";
import { interviewService } from "@/services/interviews";
import {
  Briefcase,
  Compass,
  FileText,
  GraduationCap,
  Kanban,
  LayoutDashboard,
  Mic,
  Settings,
  User,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const PIPELINE_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Profile & Skills", href: "/profile", icon: User },
  { label: "Job Intelligence", href: "/jobs", icon: Briefcase },
  { label: "Learning Roadmap", href: "/learning", icon: GraduationCap },
  { label: "Resume Studio", href: "/resumes", icon: FileText },
  { label: "Mock Interview", href: "/interview", icon: Mic },
];

const OPERATIONS_ITEMS: NavItem[] = [
  { label: "Placement Workspace", href: "/workspace", icon: Kanban },
  { label: "Applications Tracker", href: "/workspace?tab=kanban", icon: Compass },
];

const SYSTEM_ITEMS: NavItem[] = [
  { label: "AI Gateway & Settings", href: "/settings", icon: Settings },
];

interface SidebarProps {
  isOpen?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true }) => {
  const pathname = usePathname();
  const { user } = useAuth();
  const [readiness, setReadiness] = useState<number>(0);

  useEffect(() => {
    Promise.all([
      profileService.getSkills().catch(() => []),
      resumeService.listResumes().catch(() => []),
      interviewService.getLatestInterview().catch(() => null),
    ]).then(([skills, resumes, latestInterview]) => {
      let score = 0;
      if (skills && skills.length > 0) score += Math.min(skills.length * 5, 25);
      if (resumes && resumes.length > 0) score += 20;
      if (latestInterview && latestInterview.overall_score > 0) {
        score += Math.round(latestInterview.overall_score * 0.2);
      }
      setReadiness(Math.min(score, 100));
    });
  }, []);

  const getInitials = (name?: string | null): string => {
    if (!name) return "AP";
    const parts = name.trim().split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  const filledBars = Math.min(Math.floor(readiness / 20), 5);

  const renderNavList = (items: NavItem[]) => (
    <nav className="space-y-1">
      {items.map((item) => {
        const Icon = item.icon;
        const isActive =
          item.href === "/"
            ? pathname === "/"
            : pathname?.startsWith(item.href);

        return (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-2.5 px-3 py-2 rounded-[5px] text-xs font-black tracking-wide border-2 transition-all ${
              isActive
                ? "bg-black text-white border-black shadow-[3px_3px_0px_#000]"
                : "bg-white text-black border-transparent hover:border-black hover:bg-neutral-50"
            }`}
          >
            <Icon className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );

  return (
    <aside
      className={`transition-all duration-300 ease-in-out bg-white flex flex-col justify-between h-[calc(100vh-65px)] sticky top-[65px] z-30 shrink-0 select-none ${
        isOpen
          ? "w-64 border-r-2 border-black opacity-100 translate-x-0"
          : "w-0 border-r-0 opacity-0 -translate-x-full overflow-hidden pointer-events-none"
      }`}
    >
      <div className="w-64 h-full flex flex-col justify-between overflow-y-auto">
        <div className="p-4 space-y-4">
          <div className="border-2 border-black rounded-[5px] p-3 bg-neutral-50 shadow-[2px_2px_0px_#000]">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 bg-black text-white flex items-center justify-center font-black text-xs rounded-[4px] border-2 border-black shrink-0 shadow-[1px_1px_0px_#000]">
                {getInitials(user?.full_name)}
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-black truncate text-black">
                  {user?.full_name || "Candidate"}
                </div>
                <div className="text-[10px] font-mono font-bold text-neutral-500 uppercase tracking-tight truncate">
                  Engineering Tier-1
                </div>
              </div>
            </div>
            <div className="mt-2.5 pt-2 border-t border-neutral-300 flex items-center justify-between">
              <span className="text-[9px] font-mono font-bold text-neutral-600 uppercase">
                Status
              </span>
              <span className="inline-flex items-center gap-1 text-[9px] font-mono font-black uppercase bg-black text-white px-1.5 py-0.5 rounded-[3px]">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                Active Hunt
              </span>
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-[10px] font-mono font-black uppercase tracking-widest text-neutral-500 px-1">
              Core Pipeline
            </div>
            {renderNavList(PIPELINE_ITEMS)}
          </div>

          <div className="space-y-1">
            <div className="text-[10px] font-mono font-black uppercase tracking-widest text-neutral-500 px-1">
              Operations & Tracking
            </div>
            {renderNavList(OPERATIONS_ITEMS)}
          </div>

          <div className="space-y-1">
            <div className="text-[10px] font-mono font-black uppercase tracking-widest text-neutral-500 px-1">
              Configuration
            </div>
            {renderNavList(SYSTEM_ITEMS)}
          </div>
        </div>

        <div className="p-4 space-y-3 border-t-2 border-black bg-white">
          <div className="border-2 border-black rounded-[5px] p-2.5 bg-neutral-50 shadow-[2px_2px_0px_#000]">
            <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-wider mb-1">
              <span>Readiness Index</span>
              <span className="font-mono text-xs">{readiness}%</span>
            </div>
            <div className="grid grid-cols-5 gap-1 my-1.5">
              {[0, 1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className={`h-1.5 rounded-[2px] ${
                    i < filledBars
                      ? "bg-black"
                      : "bg-neutral-200 border border-black"
                  }`}
                />
              ))}
            </div>
            <div className="text-[9px] font-mono font-bold text-neutral-500 uppercase tracking-tight">
              {readiness > 0 ? "Target: FAANG / Tier-1 Tech" : "0% • Pipeline Unconfigured"}
            </div>
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono font-black text-neutral-700 pt-1">
            <div>
              <div>ON2 APEX OS</div>
              <div className="text-[9px] text-neutral-500 font-bold">SQLite WAL • v1.0.4</div>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-black animate-pulse" />
              <span className="text-[9px]">LOCAL</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
