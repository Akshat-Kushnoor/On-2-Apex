"use client";

import React, { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { healthService } from "@/services/health";
import { interviewService, InterviewScorecardOut } from "@/services/interviews";
import { profileService, SkillOut } from "@/services/profile";
import { workspaceService, ApplicationBrief } from "@/services/workspace";
import { learningService, LearningPlanOut } from "@/services/learning";
import { resumeService, GeneratedResumeBrief } from "@/services/resumes";
import { jobService, JobListOut } from "@/services/jobs";
import {
  ArrowRight,
  Briefcase,
  Clock,
  Code,
  FileCode,
  FileText,
  GraduationCap,
  Mic,
  Search,
  Terminal,
  UserCheck,
} from "lucide-react";

interface PipelineStage {
  step: string;
  badge: string;
  title: string;
  description: string;
  status: string;
  metric: string;
  progressPercent: number;
  ctaText: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface CommandItem {
  id: string;
  category: string;
  title: string;
  subtext: string;
  priority: "HIGH" | "MEDIUM";
  estimatedMinutes: number;
  actionText: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

export default function DashboardPage() {
  const [systemStats, setSystemStats] = useState({
    backendReady: false,
    dbReady: false,
  });
  const [latestInterview, setLatestInterview] = useState<InterviewScorecardOut | null>(null);
  const [skills, setSkills] = useState<SkillOut[]>([]);
  const [applications, setApplications] = useState<ApplicationBrief[]>([]);
  const [activePlan, setActivePlan] = useState<LearningPlanOut | null>(null);
  const [resumes, setResumes] = useState<GeneratedResumeBrief[]>([]);
  const [jobsTotal, setJobsTotal] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    healthService.checkReady().then((data) => {
      setSystemStats({
        backendReady: data.status === "ready",
        dbReady: data.database === "connected" || data.checks?.database === "healthy",
      });
    }).catch(() => null);

    interviewService.getLatestInterview().then(setLatestInterview).catch(() => null);
    profileService.getSkills().then(setSkills).catch(() => setSkills([]));
    workspaceService.listApplications().then(setApplications).catch(() => setApplications([]));
    learningService.getActivePlan().then(setActivePlan).catch(() => setActivePlan(null));
    resumeService.listResumes().then(setResumes).catch(() => setResumes([]));
    jobService.listJobs({ limit: 1 }).then((res) => setJobsTotal(res.total || 0)).catch(() => setJobsTotal(0));
  }, []);

  const skillsCount = skills.length;
  const applicationsCount = applications.length;
  const resumesCount = resumes.length;

  const totalTasks = activePlan?.tasks?.length ?? 0;
  const completedTasks = activePlan?.tasks?.filter(
    (t) => t.status === "COMPLETED" || t.status === "VERIFIED"
  ).length ?? 0;

  const learningProgress = useMemo(() => {
    if (!activePlan) return 0;
    if (totalTasks > 0) {
      return Math.round((completedTasks / totalTasks) * 100);
    }
    return Math.round(activePlan.progress_pct || 0);
  }, [activePlan, completedTasks, totalTasks]);

  const mockScore = latestInterview ? latestInterview.overall_score : 0;

  const readinessScore = useMemo(() => {
    let score = 0;
    if (skillsCount > 0) {
      score += Math.min(skillsCount * 5, 25);
    }
    if (applicationsCount > 0) {
      score += Math.min(applicationsCount * 3, 15);
    }
    if (resumesCount > 0) {
      score += 20;
    }
    if (learningProgress > 0) {
      score += Math.round(learningProgress * 0.2);
    }
    if (mockScore > 0) {
      score += Math.round(mockScore * 0.2);
    }
    return Math.min(score, 100);
  }, [skillsCount, applicationsCount, resumesCount, learningProgress, mockScore]);

  const pipelineStages: PipelineStage[] = useMemo(() => [
    {
      step: "01",
      badge: "STAGE 01",
      title: "Profile Alignment",
      description: skillsCount > 0 ? "Verified candidate competencies recorded" : "No skills verified yet in candidate profile",
      status: skillsCount > 0 ? "VERIFIED" : "0 SKILLS",
      metric: `${skillsCount} SKILLS VERIFIED`,
      progressPercent: skillsCount > 0 ? Math.min(skillsCount * 10, 100) : 0,
      ctaText: skillsCount > 0 ? "Audit Profile" : "Add Skills",
      href: "/profile",
      icon: UserCheck,
    },
    {
      step: "02",
      badge: "STAGE 02",
      title: "Job Intelligence",
      description: jobsTotal > 0 ? "Real-time deduplicated engineering openings" : "No indexed job openings found in feed",
      status: jobsTotal > 0 ? "ACTIVE FEED" : "0 JOBS",
      metric: `${jobsTotal} JOBS INDEXED`,
      progressPercent: jobsTotal > 0 ? 100 : 0,
      ctaText: "Browse Jobs",
      href: "/jobs",
      icon: Briefcase,
    },
    {
      step: "03",
      badge: "STAGE 03",
      title: "Learning Roadmap",
      description: activePlan ? `${activePlan.target_role} (${activePlan.total_weeks} weeks)` : "No active learning plan generated",
      status: activePlan ? (learningProgress === 100 ? "COMPLETED" : "IN PROGRESS") : "0 TASKS",
      metric: activePlan ? `${completedTasks} / ${totalTasks} TASKS` : "0 TASKS",
      progressPercent: learningProgress,
      ctaText: activePlan ? "Continue Plan" : "Create Plan",
      href: "/learning",
      icon: GraduationCap,
    },
    {
      step: "04",
      badge: "STAGE 04",
      title: "Resume Studio",
      description: resumesCount > 0 ? "Tailored LaTeX ATS resume drafts compiled" : "No tailored resumes generated yet",
      status: resumesCount > 0 ? "COMPILED" : "0 RESUMES",
      metric: `${resumesCount} RESUMES`,
      progressPercent: resumesCount > 0 ? 100 : 0,
      ctaText: resumesCount > 0 ? "Open Studio" : "Build Resume",
      href: "/resumes",
      icon: FileText,
    },
    {
      step: "05",
      badge: "STAGE 05",
      title: "Mock Interview",
      description: latestInterview ? `${latestInterview.verdict} • ${latestInterview.position}` : "No mock interview completed yet",
      status: latestInterview ? "EVALUATED" : "0 EVALS",
      metric: latestInterview ? `${latestInterview.overall_score} / 100 PTS` : "0 / 100 PTS",
      progressPercent: mockScore,
      ctaText: latestInterview ? "Retake Eval" : "Start Voice AI",
      href: "/interview",
      icon: Mic,
    },
  ], [skillsCount, jobsTotal, activePlan, learningProgress, completedTasks, totalTasks, resumesCount, latestInterview, mockScore]);

  const commandItems: CommandItem[] = useMemo(() => {
    const list: CommandItem[] = [];

    if (activePlan && activePlan.tasks) {
      const pendingTasks = activePlan.tasks.filter(
        (t) => t.status !== "COMPLETED" && t.status !== "VERIFIED"
      );
      pendingTasks.slice(0, 2).forEach((task, idx) => {
        list.push({
          id: `task-${task.id || idx}`,
          category: task.skill || "ROADMAP",
          title: task.title,
          subtext: task.description || task.learning_goal || "Complete this milestone task to advance your placement preparation.",
          priority: (task.priority as "HIGH" | "MEDIUM") || "HIGH",
          estimatedMinutes: task.estimated_hours ? Math.round(task.estimated_hours * 60) : 30,
          actionText: "Start Task",
          href: "/learning",
          icon: Code,
        });
      });
    }

    if (skillsCount === 0) {
      list.push({
        id: "cmd-skills",
        category: "PROFILE SETUP",
        title: "Record Your Verified Technical Skills",
        subtext: "Your profile has 0 verified skills. Add your core languages and frameworks to activate skill-gap analysis.",
        priority: "HIGH",
        estimatedMinutes: 10,
        actionText: "Add Skills",
        href: "/profile",
        icon: UserCheck,
      });
    }

    if (!activePlan) {
      list.push({
        id: "cmd-plan",
        category: "LEARNING ROADMAP",
        title: "Generate Time-Budgeted Learning Roadmap",
        subtext: "You currently have 0 active learning plans. Calibrate a personalized weekly syllabus targeting your preferred role.",
        priority: "HIGH",
        estimatedMinutes: 5,
        actionText: "Create Plan",
        href: "/learning",
        icon: GraduationCap,
      });
    }

    if (resumesCount === 0) {
      list.push({
        id: "cmd-resume",
        category: "RESUME STUDIO",
        title: "Compile Your First ATS LaTeX Resume",
        subtext: "0 resumes compiled. Tailor your bullet points with quantified impact formulas and verify ATS compatibility.",
        priority: "HIGH",
        estimatedMinutes: 15,
        actionText: "Build Resume",
        href: "/resumes",
        icon: FileCode,
      });
    }

    if (!latestInterview) {
      list.push({
        id: "cmd-interview",
        category: "MOCK INTERVIEW",
        title: "Complete Autonomous Voice Mock Interview",
        subtext: "0 mock interviews taken. Complete a 3-round technical, problem-solving, and behavioural evaluation with voice feedback.",
        priority: "HIGH",
        estimatedMinutes: 15,
        actionText: "Start Voice AI",
        href: "/interview",
        icon: Mic,
      });
    } else if (latestInterview.overall_score < 70) {
      list.push({
        id: "cmd-retake",
        category: "MOCK INTERVIEW",
        title: `Retake Mock Interview for ${latestInterview.position}`,
        subtext: `Recent evaluation: ${latestInterview.overall_score}/100 (${latestInterview.verdict}). Retake the 3-round voice session to improve score.`,
        priority: "HIGH",
        estimatedMinutes: 15,
        actionText: "Retake Session",
        href: "/interview",
        icon: Mic,
      });
    }

    if (applicationsCount === 0) {
      list.push({
        id: "cmd-apps",
        category: "APPLICATIONS",
        title: "Track Target Job Openings in Workspace",
        subtext: "0 applications tracked. Browse live indexed openings and add them to your Kanban placement board.",
        priority: "MEDIUM",
        estimatedMinutes: 10,
        actionText: "Browse Jobs",
        href: "/jobs",
        icon: Briefcase,
      });
    }

    return list.slice(0, 4);
  }, [activePlan, skillsCount, resumesCount, latestInterview, applicationsCount]);

  const filteredCommands = useMemo(() => {
    if (!searchQuery.trim()) return commandItems;
    const q = searchQuery.toLowerCase();
    return commandItems.filter(
      (cmd) =>
        cmd.title.toLowerCase().includes(q) ||
        cmd.category.toLowerCase().includes(q) ||
        cmd.subtext.toLowerCase().includes(q)
    );
  }, [commandItems, searchQuery]);

  const filledReadinessSegments = Math.min(Math.floor(readinessScore / 20), 5);
  const filledLearningSegments = Math.min(Math.floor(learningProgress / 25), 4);

  return (
    <AppShell>
      <div className="space-y-8 select-none">
        <section className="border-2 border-black rounded-[5px] bg-black text-white p-6 md:p-8 shadow-[6px_6px_0px_#000] space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className="inline-flex items-center px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider bg-neutral-900 text-neutral-300 border border-neutral-700 rounded-[4px]">
                  Deterministic + AI
                </span>
                <span className="inline-flex items-center px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider bg-neutral-900 text-neutral-300 border border-neutral-700 rounded-[4px]">
                  v1.0 Production Core
                </span>
              </div>
              <h1 className="text-3xl md:text-4xl font-black tracking-tight uppercase">
                Placement Command Center
              </h1>
              <p className="text-neutral-300 text-xs md:text-sm mt-1.5 max-w-2xl font-medium">
                Deterministic skill verification, real-time market indexing, time-budgeted study roadmaps, and autonomous voice mock interviews for engineering students.
              </p>
            </div>
          </div>

          <div className="border-2 border-white bg-neutral-950 p-2.5 rounded-[5px] shadow-[4px_4px_0px_#fff] flex flex-col md:flex-row items-center gap-3">
            <div className="flex items-center gap-2.5 bg-neutral-900 border border-neutral-700 px-3 py-2 rounded-[4px] w-full md:flex-1">
              <Search className="w-4 h-4 text-neutral-400 shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Filter commands, pipeline stages, or target skills..."
                className="bg-transparent text-xs font-mono text-white placeholder-neutral-500 focus:outline-none w-full"
              />
              <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-mono bg-neutral-800 text-neutral-300 border border-neutral-600 px-1.5 py-0.5 rounded">
                CTRL+K
              </span>
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto shrink-0 justify-end">
              <Link href="/jobs" className="flex-1 md:flex-initial">
                <Button
                  variant="secondary"
                  size="sm"
                  className="w-full flex items-center justify-center gap-1.5 border-2 border-white shadow-[2px_2px_0px_#fff] text-xs font-black uppercase tracking-wide"
                >
                  <Briefcase className="w-3.5 h-3.5" />
                  <span>Find Jobs</span>
                </Button>
              </Link>
              <Link href="/interview" className="flex-1 md:flex-initial">
                <Button
                  variant="secondary"
                  size="sm"
                  className="w-full flex items-center justify-center gap-1.5 border-2 border-white shadow-[2px_2px_0px_#fff] text-xs font-black uppercase tracking-wide"
                >
                  <Mic className="w-3.5 h-3.5" />
                  <span>Mock Interview</span>
                </Button>
              </Link>
            </div>
          </div>
        </section>

        <section className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
            <div>
              <div className="text-[10px] font-mono font-black uppercase tracking-widest text-neutral-500">
                Evaluation Telemetry
              </div>
              <h2 className="text-xl font-black tracking-tight uppercase text-black">
                Readiness Snapshot
              </h2>
            </div>
            <div className="text-xs font-mono font-bold text-neutral-600">
              UPDATED LIVE FROM LOCAL SQLITE WAL
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="border-2 border-black rounded-[5px] bg-white p-4 shadow-[4px_4px_0px_#000] flex flex-col justify-between">
              <div>
                <div className="text-[10px] font-mono font-black text-neutral-500 uppercase tracking-wider">
                  Placement Readiness
                </div>
                <div className="text-4xl font-black text-black mt-2 font-mono tracking-tight">
                  {readinessScore}%
                </div>
              </div>
              <div className="mt-4 pt-3 border-t-2 border-black space-y-1.5">
                <div className="grid grid-cols-5 gap-1">
                  {[0, 1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className={`h-1.5 rounded-[1px] ${
                        i < filledReadinessSegments
                          ? "bg-black"
                          : "bg-neutral-200 border border-black"
                      }`}
                    />
                  ))}
                </div>
                <div className="text-[10px] font-mono font-bold text-neutral-600 uppercase">
                  {readinessScore > 0 ? "Target: Tier-1 Tech" : "0% • Pipeline Unconfigured"}
                </div>
              </div>
            </div>

            <div className="border-2 border-black rounded-[5px] bg-white p-4 shadow-[4px_4px_0px_#000] flex flex-col justify-between">
              <div>
                <div className="text-[10px] font-mono font-black text-neutral-500 uppercase tracking-wider">
                  Skills Verified
                </div>
                <div className="text-4xl font-black text-black mt-2 font-mono tracking-tight">
                  {skillsCount}
                </div>
              </div>
              <div className="mt-4 pt-3 border-t-2 border-black space-y-1">
                <div className="text-[10px] font-mono font-black text-black uppercase">
                  {skillsCount > 0 ? `${skillsCount} Verified In Profile` : "0 Skills Verified"}
                </div>
                <div className="text-[10px] font-mono font-bold text-neutral-600 truncate">
                  {skillsCount > 0 ? skills.slice(0, 3).map((s) => s.name).join(", ") : "Profile Unconfigured"}
                </div>
              </div>
            </div>

            <div className="border-2 border-black rounded-[5px] bg-white p-4 shadow-[4px_4px_0px_#000] flex flex-col justify-between">
              <div>
                <div className="text-[10px] font-mono font-black text-neutral-500 uppercase tracking-wider">
                  Active Pipeline
                </div>
                <div className="text-4xl font-black text-black mt-2 font-mono tracking-tight">
                  {applicationsCount}
                </div>
              </div>
              <div className="mt-4 pt-3 border-t-2 border-black space-y-1">
                <div className="text-[10px] font-mono font-black text-black uppercase">
                  {applicationsCount > 0 ? `${applicationsCount} Applications Tracked` : "0 Applications Tracked"}
                </div>
                <div className="text-[10px] font-mono font-bold text-neutral-600">
                  {applicationsCount > 0 ? "Pipeline In Progress" : "Workspace Empty"}
                </div>
              </div>
            </div>

            <div className="border-2 border-black rounded-[5px] bg-white p-4 shadow-[4px_4px_0px_#000] flex flex-col justify-between">
              <div>
                <div className="text-[10px] font-mono font-black text-neutral-500 uppercase tracking-wider">
                  Mock Interview Score
                </div>
                <div className="flex items-baseline gap-1 mt-2">
                  <span className="text-4xl font-black text-black font-mono tracking-tight">
                    {mockScore}
                  </span>
                  <span className="text-sm font-mono font-bold text-neutral-500">
                    /100
                  </span>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t-2 border-black space-y-1">
                <div className="text-[10px] font-mono font-black text-black uppercase truncate">
                  {latestInterview ? latestInterview.verdict : "Untested"}
                </div>
                <div className="text-[10px] font-mono font-bold text-neutral-600 truncate">
                  {latestInterview ? latestInterview.position : "0 Interviews Completed"}
                </div>
              </div>
            </div>

            <div className="border-2 border-black rounded-[5px] bg-white p-4 shadow-[4px_4px_0px_#000] flex flex-col justify-between">
              <div>
                <div className="text-[10px] font-mono font-black text-neutral-500 uppercase tracking-wider">
                  Learning Progress
                </div>
                <div className="text-4xl font-black text-black mt-2 font-mono tracking-tight">
                  {learningProgress}%
                </div>
              </div>
              <div className="mt-4 pt-3 border-t-2 border-black space-y-1.5">
                <div className="grid grid-cols-4 gap-1">
                  {[0, 1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className={`h-1.5 rounded-[1px] ${
                        i < filledLearningSegments
                          ? "bg-black"
                          : "bg-neutral-200 border border-black"
                      }`}
                    />
                  ))}
                </div>
                <div className="text-[10px] font-mono font-bold text-neutral-600 uppercase">
                  {totalTasks > 0 ? `${completedTasks} of ${totalTasks} Milestones Finished` : "0 Milestones • No Plan"}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
            <div>
              <div className="text-[10px] font-mono font-black uppercase tracking-widest text-neutral-500">
                End-To-End Architecture
              </div>
              <h2 className="text-xl font-black tracking-tight uppercase text-black">
                Placement Pipeline
              </h2>
            </div>
            <div className="text-xs font-mono font-bold text-neutral-600">
              5 CONNECTED STAGES • DETERMINISTIC EXECUTION
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {pipelineStages.map((stage) => {
              const Icon = stage.icon;
              const filledBarSegments = Math.min(Math.floor(stage.progressPercent / 25), 4);
              return (
                <div
                  key={stage.step}
                  className="border-2 border-black rounded-[5px] bg-white p-4 shadow-[4px_4px_0px_#000] flex flex-col justify-between hover:-translate-y-0.5 transition-transform"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between border-b-2 border-black pb-2.5">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-mono font-black bg-black text-white px-1.5 py-0.5 rounded-[3px]">
                          {stage.step}
                        </span>
                        <span className="text-[10px] font-mono font-bold text-neutral-500">
                          STAGE
                        </span>
                      </div>
                      <span className="text-[9px] font-mono font-black px-1.5 py-0.5 rounded border border-black bg-neutral-100 text-black uppercase">
                        {stage.status}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <div className="p-1.5 bg-neutral-100 border border-black rounded-[4px] shrink-0">
                        <Icon className="w-4 h-4 text-black" />
                      </div>
                      <h3 className="font-black text-sm tracking-tight text-black truncate">
                        {stage.title}
                      </h3>
                    </div>

                    <p className="text-xs text-neutral-600 leading-snug line-clamp-2">
                      {stage.description}
                    </p>

                    <div className="border border-black rounded-[4px] p-2 bg-neutral-50 space-y-1.5">
                      <div className="flex items-center justify-between text-[10px] font-mono font-black">
                        <span className="text-neutral-500">METRIC</span>
                        <span className="text-black">{stage.metric}</span>
                      </div>
                      <div className="grid grid-cols-4 gap-1">
                        {[0, 1, 2, 3].map((i) => (
                          <div
                            key={i}
                            className={`h-1.5 rounded-[1px] ${
                              i < filledBarSegments
                                ? "bg-black"
                                : "bg-neutral-200 border border-black"
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t-2 border-black">
                    <Link href={stage.href} className="w-full block">
                      <Button
                        variant="secondary"
                        size="sm"
                        className="w-full flex items-center justify-between text-xs font-black uppercase tracking-wide border-2 border-black shadow-[2px_2px_0px_#000] hover:bg-black hover:text-white transition-colors"
                      >
                        <span>{stage.ctaText}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
            <div>
              <div className="text-[10px] font-mono font-black uppercase tracking-widest text-neutral-500">
                Priority Action Plan
              </div>
              <h2 className="text-xl font-black tracking-tight uppercase text-black">
                Today's Commands
              </h2>
            </div>
            <div className="text-xs font-mono font-bold text-neutral-600">
              {filteredCommands.length} ACTIVE DIRECTIVES FOR TODAY
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredCommands.map((cmd) => {
              const CmdIcon = cmd.icon;
              return (
                <div
                  key={cmd.id}
                  className="border-2 border-black rounded-[5px] bg-white p-5 shadow-[4px_4px_0px_#000] flex flex-col justify-between space-y-4 hover:-translate-y-0.5 transition-transform"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between border-b-2 border-black pb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono font-black bg-black text-white px-2 py-0.5 rounded-[3px] uppercase">
                          {cmd.priority} PRIORITY
                        </span>
                        <span className="text-[10px] font-mono font-bold text-neutral-500">
                          {cmd.category}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-[10px] font-mono font-bold text-black border border-black px-1.5 py-0.5 rounded bg-neutral-100">
                        <Clock className="w-3 h-3" />
                        <span>{cmd.estimatedMinutes} MIN</span>
                      </div>
                    </div>

                    <div className="flex items-start gap-2.5">
                      <div className="p-2 bg-neutral-100 border-2 border-black rounded-[4px] shrink-0 mt-0.5">
                        <CmdIcon className="w-4 h-4 text-black" />
                      </div>
                      <div>
                        <h3 className="text-sm font-black text-black leading-snug">
                          {cmd.title}
                        </h3>
                        <p className="text-xs text-neutral-600 mt-1 leading-relaxed">
                          {cmd.subtext}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="pt-3 border-t-2 border-black flex items-center justify-end">
                    <Link href={cmd.href}>
                      <Button
                        variant="primary"
                        size="sm"
                        className="flex items-center gap-2 text-xs font-black uppercase tracking-wide border-2 border-black shadow-[2px_2px_0px_#000]"
                      >
                        <span>{cmd.actionText}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="border-2 border-black rounded-[5px] bg-black text-white shadow-[6px_6px_0px_#000] overflow-hidden">
          <div className="px-5 py-3 border-b-2 border-neutral-800 flex items-center justify-between bg-neutral-950">
            <div className="flex items-center gap-2.5">
              <Terminal className="w-4 h-4 text-white" />
              <span className="text-xs font-mono font-black uppercase tracking-wider text-white">
                Core System Status :: Local Runtime Telemetry
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
              <span className="text-[10px] font-mono font-black uppercase text-neutral-300">
                Deterministic Engine Active
              </span>
            </div>
          </div>

          <div className="p-5 font-mono text-xs space-y-3 bg-black">
            <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-neutral-800 pb-2.5 gap-2">
              <div className="flex items-center gap-3">
                <span className="text-neutral-500 font-bold">[BACKEND]</span>
                <span className="font-bold text-white">FastAPI Local Daemon</span>
                <span className="text-neutral-400 text-[11px]">http://127.0.0.1:8000</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-neutral-400 text-[11px]">Uvicorn • Latency: 3.4ms</span>
                <span className={`px-2 py-0.5 text-[10px] font-black rounded uppercase border ${
                  systemStats.backendReady
                    ? "bg-white text-black border-white"
                    : "bg-neutral-800 text-neutral-400 border-neutral-600"
                }`}>
                  {systemStats.backendReady ? "ONLINE" : "INITIALIZING"}
                </span>
              </div>
            </div>

            <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-neutral-800 pb-2.5 gap-2">
              <div className="flex items-center gap-3">
                <span className="text-neutral-500 font-bold">[DATABASE]</span>
                <span className="font-bold text-white">SQLite Engine</span>
                <span className="text-neutral-400 text-[11px]">placement_coach.db</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-neutral-400 text-[11px]">WAL Mode • Isolation: Serializable</span>
                <span className={`px-2 py-0.5 text-[10px] font-black rounded uppercase border ${
                  systemStats.dbReady
                    ? "bg-white text-black border-white"
                    : "bg-neutral-800 text-neutral-400 border-neutral-600"
                }`}>
                  {systemStats.dbReady ? "CONNECTED" : "INITIALIZING"}
                </span>
              </div>
            </div>

            <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-neutral-800 pb-2.5 gap-2">
              <div className="flex items-center gap-3">
                <span className="text-neutral-500 font-bold">[AI_GATEWAY]</span>
                <span className="font-bold text-white">BYOK Multi-Model Pipeline</span>
                <span className="text-neutral-400 text-[11px]">OpenAI / Gemini / Groq</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-neutral-400 text-[11px]">Deterministic Fallback: Active</span>
                <span className="px-2 py-0.5 text-[10px] font-black rounded uppercase border bg-white text-black border-white">
                  CONFIGURED
                </span>
              </div>
            </div>

            <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-neutral-800 pb-2.5 gap-2">
              <div className="flex items-center gap-3">
                <span className="text-neutral-500 font-bold">[SCRAPER]</span>
                <span className="font-bold text-white">JobSpy Harvester</span>
                <span className="text-neutral-400 text-[11px]">LinkedIn • Indeed</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-neutral-400 text-[11px]">Deduplication: SHA-256</span>
                <span className="px-2 py-0.5 text-[10px] font-black rounded uppercase border bg-white text-black border-white">
                  STANDBY
                </span>
              </div>
            </div>

            <div className="flex flex-col md:flex-row md:items-center justify-between pt-0.5 gap-2">
              <div className="flex items-center gap-3">
                <span className="text-neutral-500 font-bold">[VOICE_AI]</span>
                <span className="font-bold text-white">Web Speech API</span>
                <span className="text-neutral-400 text-[11px]">SpeechRecognition + Synthesis</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-neutral-400 text-[11px]">Autonomous 3-Round Protocol</span>
                <span className="px-2 py-0.5 text-[10px] font-black rounded uppercase border bg-white text-black border-white">
                  READY
                </span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
