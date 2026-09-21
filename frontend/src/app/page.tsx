"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { healthService } from "@/services/health";
import {
  ArrowRight,
  Briefcase,
  CheckCircle2,
  FileText,
  GraduationCap,
  Kanban,
  Sparkles,
  TrendingUp,
} from "lucide-react";

export default function DashboardPage() {
  const [systemStats, setSystemStats] = useState({
    backendReady: false,
    dbReady: false,
  });

  useEffect(() => {
    healthService.checkReady().then((data) => {
      setSystemStats({
        backendReady: data.status === "ready",
        dbReady: data.database === "connected",
      });
    });
  }, []);

  return (
    <AppShell>
      <div className="space-y-8">
        <div className="border-2 border-black rounded-[5px] bg-black text-white p-6 shadow-[6px_6px_0px_#000] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className="bg-white text-black text-[10px]">
                LOCAL OPERATING SYSTEM
              </Badge>
              <Badge variant="dark" className="border-white text-[10px] text-white">
                DETERMINISTIC + AI
              </Badge>
            </div>
            <h1 className="text-3xl font-black tracking-tight uppercase">
              Placement Command Center
            </h1>
            <p className="text-neutral-300 text-sm mt-1 max-w-xl">
              Deterministic skill-gap analysis, time-budgeted preparation plans, and job-tailored resumes for engineering students.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link href="/jobs">
              <Button variant="secondary" size="md" className="flex items-center gap-2">
                <Briefcase className="w-4 h-4" />
                <span>Find Jobs</span>
              </Button>
            </Link>
            <Link href="/workspace">
              <Button variant="primary" size="md" className="bg-white text-black border-white hover:bg-neutral-200 flex items-center gap-2">
                <Kanban className="w-4 h-4" />
                <span>Workspace</span>
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <Card className="flex flex-col justify-between">
            <CardHeader>
              <div className="flex items-center justify-between">
                <Badge variant="dark">STAGE 1</Badge>
                <TrendingUp className="w-5 h-5 text-black" />
              </div>
              <CardTitle className="mt-3">Profile Alignment</CardTitle>
              <CardDescription>Verified candidate skills & projects</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black">Ready</div>
              <p className="text-xs text-neutral-600 mt-1">
                Structured profile loaded from persistent SQLite.
              </p>
            </CardContent>
            <CardFooter>
              <Link href="/profile" className="w-full">
                <Button variant="secondary" size="sm" className="w-full flex items-center justify-center gap-1.5">
                  <span>Manage Profile</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </CardFooter>
          </Card>

          <Card className="flex flex-col justify-between">
            <CardHeader>
              <div className="flex items-center justify-between">
                <Badge variant="default">STAGE 2</Badge>
                <Briefcase className="w-5 h-5 text-black" />
              </div>
              <CardTitle className="mt-3">Job Intelligence</CardTitle>
              <CardDescription>Targeted market opportunities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black">Live Search</div>
              <p className="text-xs text-neutral-600 mt-1">
                Normalized deduplication via JobSpy integration.
              </p>
            </CardContent>
            <CardFooter>
              <Link href="/jobs" className="w-full">
                <Button variant="secondary" size="sm" className="w-full flex items-center justify-center gap-1.5">
                  <span>Browse Openings</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </CardFooter>
          </Card>

          <Card className="flex flex-col justify-between">
            <CardHeader>
              <div className="flex items-center justify-between">
                <Badge variant="highlight">STAGE 3</Badge>
                <GraduationCap className="w-5 h-5 text-black" />
              </div>
              <CardTitle className="mt-3">Learning Roadmap</CardTitle>
              <CardDescription>Weekly time-budgeted study</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black">Active Plan</div>
              <div className="mt-2">
                <Progress value={50} showLabel={true} />
              </div>
            </CardContent>
            <CardFooter>
              <Link href="/learning" className="w-full">
                <Button variant="secondary" size="sm" className="w-full flex items-center justify-center gap-1.5">
                  <span>View Tasks</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </CardFooter>
          </Card>

          <Card className="flex flex-col justify-between">
            <CardHeader>
              <div className="flex items-center justify-between">
                <Badge variant="dark">STAGE 4</Badge>
                <FileText className="w-5 h-5 text-black" />
              </div>
              <CardTitle className="mt-3">Resume Studio</CardTitle>
              <CardDescription>Tailored XYZ bullet points</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black">ATS & LaTeX</div>
              <p className="text-xs text-neutral-600 mt-1">
                Zero hallucinations, verified diff tracking.
              </p>
            </CardContent>
            <CardFooter>
              <Link href="/resumes" className="w-full">
                <Button variant="secondary" size="sm" className="w-full flex items-center justify-center gap-1.5">
                  <span>Open Studio</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </CardFooter>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Core System Verification</CardTitle>
            <CardDescription>Real-time local backend health and service connectivity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border-2 border-black rounded-[5px] p-4 bg-white shadow-[3px_3px_0px_#000] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold uppercase text-neutral-500">FastAPI Backend</div>
                  <div className="text-sm font-black text-black">http://localhost:8000</div>
                </div>
                <Badge variant={systemStats.backendReady ? "highlight" : "outline"}>
                  {systemStats.backendReady ? "ONLINE" : "CHECKING"}
                </Badge>
              </div>

              <div className="border-2 border-black rounded-[5px] p-4 bg-white shadow-[3px_3px_0px_#000] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold uppercase text-neutral-500">Local Database</div>
                  <div className="text-sm font-black text-black">SQLite WAL Mode</div>
                </div>
                <Badge variant={systemStats.dbReady ? "highlight" : "outline"}>
                  {systemStats.dbReady ? "CONNECTED" : "CHECKING"}
                </Badge>
              </div>

              <div className="border-2 border-black rounded-[5px] p-4 bg-white shadow-[3px_3px_0px_#000] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold uppercase text-neutral-500">BYOK LLM Gateway</div>
                  <div className="text-sm font-black text-black">Unified Failover</div>
                </div>
                <Badge variant="highlight">ACTIVE</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
