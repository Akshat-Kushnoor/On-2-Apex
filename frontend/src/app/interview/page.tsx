"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  interviewService,
  InterviewQuestionItem,
  InterviewAnswerItem,
  InterviewScorecardOut,
} from "@/services/interviews";
import {
  Mic,
  MicOff,
  Video,
  VideoOff,
  Volume2,
  Sparkles,
  ArrowRight,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Brain,
  Award,
  TrendingUp,
  Target,
  Lightbulb,
  MessageSquare,
  ShieldCheck,
  ChevronRight,
  Briefcase,
  Play,
  Clock,
  Terminal,
} from "lucide-react";

const ROLE_PRESETS = [
  "Senior Backend Engineer",
  "Frontend Specialist",
  "AI/ML Engineer",
  "Full Stack Developer",
  "Cloud & DevOps Architect",
  "Data Engineer",
];

export default function MockInterviewPage() {
  const [phase, setPhase] = useState<"lobby" | "interview" | "evaluating" | "scorecard">("lobby");
  const [selectedRole, setSelectedRole] = useState<string>("Senior Backend Engineer");
  const [customRole, setCustomRole] = useState<string>("");

  const [questions, setQuestions] = useState<InterviewQuestionItem[]>([]);
  const [currentIdx, setCurrentIdx] = useState<number>(0);
  const [recordedAnswers, setRecordedAnswers] = useState<InterviewAnswerItem[]>([]);
  const [currentAnswerText, setCurrentAnswerText] = useState<string>("");

  const [isMicActive, setIsMicActive] = useState<boolean>(true);
  const [isVideoActive, setIsVideoActive] = useState<boolean>(true);
  const [isSpeakingAI, setIsSpeakingAI] = useState<boolean>(false);
  const [isListeningUser, setIsListeningUser] = useState<boolean>(false);

  const [scorecard, setScorecard] = useState<InterviewScorecardOut | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<any>(null);

  const startMediaPreview = useCallback(async () => {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      }
    } catch {
      setIsVideoActive(false);
    }
  }, []);

  const stopMediaPreview = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
    }
  }, []);

  useEffect(() => {
    startMediaPreview();
    return () => {
      stopMediaPreview();
    };
  }, [startMediaPreview, stopMediaPreview]);

  const speakText = useCallback((text: string, onDone?: () => void) => {
    if (typeof window === "undefined" || !window.speechSynthesis) {
      if (onDone) onDone();
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.98;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(
      (v) => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Samantha"))
    );
    if (naturalVoice) {
      utterance.voice = naturalVoice;
    }

    utterance.onstart = () => setIsSpeakingAI(true);
    utterance.onend = () => {
      setIsSpeakingAI(false);
      if (onDone) onDone();
    };
    utterance.onerror = () => {
      setIsSpeakingAI(false);
      if (onDone) onDone();
    };

    window.speechSynthesis.speak(utterance);
  }, []);

  const startSpeechRecognition = useCallback(() => {
    if (typeof window === "undefined") return;
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    try {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onstart = () => setIsListeningUser(true);
      recognition.onend = () => setIsListeningUser(false);
      recognition.onerror = () => setIsListeningUser(false);

      recognition.onresult = (event: any) => {
        let transcript = "";
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript + " ";
        }
        setCurrentAnswerText(transcript.trim());
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch {}
  }, []);

  const stopSpeechRecognition = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
      setIsListeningUser(false);
    }
  }, []);

  const handleStartInterview = async () => {
    setErrorMessage("");
    const roleToUse = customRole.trim() || selectedRole;
    try {
      const res = await interviewService.startInterview(roleToUse);
      setQuestions(res.questions);
      setCurrentIdx(0);
      setRecordedAnswers([]);
      setCurrentAnswerText("");
      setPhase("interview");

      setTimeout(() => {
        if (res.questions.length > 0) {
          const intro = `Welcome to your mock interview for ${roleToUse}. Let's begin with your first question. ${res.questions[0].question}`;
          speakText(intro, () => {
            if (isMicActive) {
              startSpeechRecognition();
            }
          });
        }
      }, 500);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to initiate mock interview session.");
    }
  };

  const handleRepeatQuestion = () => {
    const q = questions[currentIdx];
    if (!q) return;
    stopSpeechRecognition();
    speakText(q.question, () => {
      if (isMicActive) {
        startSpeechRecognition();
      }
    });
  };

  const handleNextOrFinish = async () => {
    stopSpeechRecognition();
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setIsSpeakingAI(false);

    const currentQ = questions[currentIdx];
    const currentAnswerItem: InterviewAnswerItem = {
      question_id: currentQ.id,
      category: currentQ.category,
      question: currentQ.question,
      answer: currentAnswerText.trim() || "[No verbal response recorded]",
    };

    const updatedAnswers = [...recordedAnswers, currentAnswerItem];
    setRecordedAnswers(updatedAnswers);
    setCurrentAnswerText("");

    if (currentIdx + 1 < questions.length) {
      const nextIndex = currentIdx + 1;
      setCurrentIdx(nextIndex);
      const nextQ = questions[nextIndex];
      const promptText = `Next question. In the category of ${nextQ.category.replace("_", " ")}: ${nextQ.question}`;
      speakText(promptText, () => {
        if (isMicActive) {
          startSpeechRecognition();
        }
      });
    } else {
      setPhase("evaluating");
      try {
        const roleToUse = customRole.trim() || selectedRole;
        const result = await interviewService.evaluateInterview({
          position: roleToUse,
          answers: updatedAnswers,
        });
        setScorecard(result);
        setPhase("scorecard");
      } catch (err: unknown) {
        setErrorMessage(err instanceof Error ? err.message : "Error evaluating interview session.");
        setPhase("scorecard");
      }
    }
  };

  const activeQuestion = questions[currentIdx];
  const roleName = customRole.trim() || selectedRole;

  return (
    <AppShell>
      <div className="space-y-6 pb-20 animate-pop-in">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b-2 border-black pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 bg-black text-white rounded-[5px] shadow-[2px_2px_0px_#000]">
                <Mic className="w-5 h-5" />
              </span>
              <h1 className="text-2xl font-black uppercase tracking-tight">
                Autonomous Auto Mock Interview
              </h1>
            </div>
            <p className="text-xs text-neutral-600 font-medium">
              Real-time voice interview stage powered by browser speech synthesis & native BYOK evaluation. Graded across 5 dimensions out of 100.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="dark" className="text-xs font-mono font-bold">
              3-Round Auto Evaluation
            </Badge>
          </div>
        </div>

        {errorMessage && (
          <div className="bg-red-50 border-2 border-black p-3 rounded-[5px] text-xs font-bold text-red-700 flex items-center gap-2 shadow-[2px_2px_0px_#000]">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {phase === "lobby" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-7 space-y-6">
              <Card className="border-2 border-black shadow-[4px_4px_0px_#000] bg-white">
                <CardHeader>
                  <CardTitle className="text-base uppercase flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-black" />
                    <span>Select Target Interview Position</span>
                  </CardTitle>
                  <CardDescription>
                    The AI automatically tailors 3 specialized questions: 1 Technical Architecture, 1 Problem Solving, and 1 STAR Behavioural.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {ROLE_PRESETS.map((role) => (
                      <button
                        key={role}
                        type="button"
                        onClick={() => {
                          setSelectedRole(role);
                          setCustomRole("");
                        }}
                        className={`p-3 text-xs font-black uppercase rounded-[5px] border-2 border-black text-left transition-all ${
                          selectedRole === role && !customRole
                            ? "bg-black text-white shadow-[2px_2px_0px_#000]"
                            : "bg-white text-black hover:bg-neutral-100"
                        }`}
                      >
                        {role}
                      </button>
                    ))}
                  </div>

                  <div className="space-y-1.5 pt-2">
                    <label className="text-xs font-black uppercase tracking-wider text-neutral-600">
                      Or Specify Custom Role Title
                    </label>
                    <Input
                      type="text"
                      placeholder="e.g. Distributed Systems Engineer, Platform Lead..."
                      value={customRole}
                      onChange={(e) => setCustomRole(e.target.value)}
                      className="border-2 border-black text-xs font-bold"
                    />
                  </div>

                  <div className="p-3.5 bg-neutral-50 border-2 border-black rounded-[5px] space-y-2">
                    <div className="text-[10px] font-black uppercase text-neutral-600 flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>Interview Round Composition</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center text-xs font-black">
                      <div className="bg-white border border-black p-2 rounded-[4px] shadow-[1px_1px_0px_#000]">
                        <span className="text-[9px] text-neutral-500 block uppercase">Round 1</span>
                        Technical Core
                      </div>
                      <div className="bg-white border border-black p-2 rounded-[4px] shadow-[1px_1px_0px_#000]">
                        <span className="text-[9px] text-neutral-500 block uppercase">Round 2</span>
                        Problem Solving
                      </div>
                      <div className="bg-white border border-black p-2 rounded-[4px] shadow-[1px_1px_0px_#000]">
                        <span className="text-[9px] text-neutral-500 block uppercase">Round 3</span>
                        STAR Behavioural
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Button
                variant="primary"
                size="lg"
                onClick={handleStartInterview}
                className="w-full text-sm font-black uppercase tracking-wider py-4 shadow-[4px_4px_0px_#000] flex items-center justify-center gap-2"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>Launch Autonomous Interview Stage</span>
              </Button>
            </div>

            <div className="lg:col-span-5 space-y-4">
              <Card className="border-2 border-black shadow-[4px_4px_0px_#000] bg-white overflow-hidden">
                <div className="p-3 border-b-2 border-black bg-neutral-50 flex items-center justify-between">
                  <span className="text-xs font-black uppercase flex items-center gap-1.5">
                    <Video className="w-3.5 h-3.5" />
                    <span>Candidate Camera & Audio Check</span>
                  </span>
                  <Badge variant={isVideoActive ? "highlight" : "outline"} className="text-[9px]">
                    {isVideoActive ? "CAM READY" : "AUDIO ONLY"}
                  </Badge>
                </div>

                <div className="p-4 space-y-3">
                  <div className="relative aspect-video bg-neutral-950 rounded-[5px] border-2 border-black overflow-hidden flex items-center justify-center">
                    {isVideoActive ? (
                      <video
                        ref={videoRef}
                        autoPlay
                        muted
                        playsInline
                        className="w-full h-full object-cover scale-x-[-1]"
                      />
                    ) : (
                      <div className="text-center text-white space-y-1">
                        <VideoOff className="w-8 h-8 mx-auto text-neutral-500" />
                        <p className="text-xs font-mono font-bold text-neutral-400">Camera Feed Inactive</p>
                      </div>
                    )}
                    <div className="absolute bottom-2 left-2 flex items-center gap-1.5 bg-black/80 px-2 py-1 rounded-[3px] text-[10px] font-mono font-bold text-white border border-neutral-700">
                      <span className="w-2 h-2 rounded-full bg-lime-400 animate-pulse" />
                      <span>{isMicActive ? "Mic Active" : "Mic Muted"}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-2">
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => setIsMicActive(!isMicActive)}
                      className="text-xs border-2 border-black flex-1 flex items-center justify-center gap-1"
                    >
                      {isMicActive ? <Mic className="w-3.5 h-3.5" /> : <MicOff className="w-3.5 h-3.5 text-red-600" />}
                      <span>{isMicActive ? "Mute Mic" : "Unmute Mic"}</span>
                    </Button>

                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => setIsVideoActive(!isVideoActive)}
                      className="text-xs border-2 border-black flex-1 flex items-center justify-center gap-1"
                    >
                      {isVideoActive ? <Video className="w-3.5 h-3.5" /> : <VideoOff className="w-3.5 h-3.5 text-red-600" />}
                      <span>{isVideoActive ? "Disable Cam" : "Enable Cam"}</span>
                    </Button>
                  </div>
                </div>
              </Card>

              <div className="p-4 border-2 border-black rounded-[5px] bg-neutral-100 shadow-[3px_3px_0px_#000] space-y-1.5">
                <div className="text-xs font-black uppercase text-black flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Autonomous AI Coach Rules</span>
                </div>
                <p className="text-xs text-neutral-700 font-medium leading-relaxed">
                  The AI interviewer speaks each question out loud. Speak naturally into your microphone. Your spoken responses are transcribed in real-time and evaluated by your BYOK LLM.
                </p>
              </div>
            </div>
          </div>
        )}

        {phase === "interview" && activeQuestion && (
          <div className="space-y-6">
            <div className="flex items-center justify-between border-2 border-black rounded-[5px] p-3 bg-white shadow-[3px_3px_0px_#000]">
              <div className="flex items-center gap-3">
                <Badge variant="dark" className="text-xs font-black">
                  QUESTION {currentIdx + 1} OF {questions.length}
                </Badge>
                <span className="text-xs font-black uppercase text-neutral-600">
                  Target: <strong className="text-black">{roleName}</strong>
                </span>
                <span className="px-2 py-0.5 text-[10px] font-black uppercase bg-neutral-100 border border-black rounded-[4px]">
                  {activeQuestion.category.replace("_", " ")}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleRepeatQuestion}
                  className="text-xs border-2 border-black shadow-[1px_1px_0px_#000] flex items-center gap-1.5"
                >
                  <Volume2 className="w-3.5 h-3.5" />
                  <span>Repeat Question</span>
                </Button>

                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleNextOrFinish}
                  className="text-xs shadow-[2px_2px_0px_#000] flex items-center gap-1.5"
                >
                  <span>{currentIdx + 1 < questions.length ? "Next Question" : "Finish & Analyze"}</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-2 border-black shadow-[4px_4px_0px_#000] bg-white flex flex-col justify-between">
                <div className="p-4 border-b-2 border-black bg-neutral-50 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-black" />
                    <span className="text-xs font-black uppercase">AI Technical Interviewer</span>
                  </div>
                  <Badge variant={isSpeakingAI ? "highlight" : "outline"} className="text-[10px]">
                    {isSpeakingAI ? "SPEAKING ALOUD" : "WAITING FOR ANSWER"}
                  </Badge>
                </div>

                <div className="p-6 space-y-6 flex-1 flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="text-[10px] font-black uppercase text-neutral-500 tracking-wider">
                      {activeQuestion.title}
                    </div>
                    <p className="text-lg font-black text-black leading-relaxed">
                      "{activeQuestion.question}"
                    </p>
                    {activeQuestion.hint && (
                      <p className="text-xs text-neutral-500 italic bg-neutral-50 border border-neutral-200 p-2.5 rounded-[4px]">
                        Expected Areas: {activeQuestion.hint}
                      </p>
                    )}
                  </div>

                  <div className="border-2 border-black rounded-[5px] p-4 bg-neutral-900 text-white flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Volume2 className={`w-4 h-4 ${isSpeakingAI ? "text-lime-400 animate-pulse" : "text-neutral-500"}`} />
                      <span className="text-xs font-mono font-bold">
                        {isSpeakingAI ? "Audio Synthesizer Active" : "Waiting for candidate voice input..."}
                      </span>
                    </div>

                    <div className="flex items-end gap-1 h-6">
                      {[18, 28, 14, 32, 22, 10, 26, 16].map((h, i) => (
                        <span
                          key={i}
                          className={`w-1 rounded-full transition-all duration-150 ${
                            isSpeakingAI ? "bg-lime-400" : "bg-neutral-700"
                          }`}
                          style={{
                            height: isSpeakingAI ? `${(h * ((i % 3) + 1)) % 24 + 6}px` : "4px",
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </Card>

              <Card className="border-2 border-black shadow-[4px_4px_0px_#000] bg-white flex flex-col justify-between">
                <div className="p-4 border-b-2 border-black bg-neutral-50 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${isListeningUser ? "bg-red-600 animate-pulse" : "bg-neutral-400"}`} />
                    <span className="text-xs font-black uppercase">Candidate Live Voice Transcript</span>
                  </div>
                  <Badge variant={isListeningUser ? "highlight" : "outline"} className="text-[10px]">
                    {isListeningUser ? "LISTENING" : "MIC PAUSED"}
                  </Badge>
                </div>

                <div className="p-6 space-y-4 flex-1 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-[10px] font-black uppercase text-neutral-500 tracking-wider">
                      <span>Real-Time Speech Subtitles</span>
                      <button
                        type="button"
                        onClick={() => setCurrentAnswerText("")}
                        className="text-neutral-400 hover:text-black underline"
                      >
                        Clear
                      </button>
                    </div>

                    <Textarea
                      value={currentAnswerText}
                      onChange={(e) => setCurrentAnswerText(e.target.value)}
                      placeholder="Start speaking into your microphone. Words will transcribe live here... (Or type manually if preferred)"
                      rows={8}
                      className="border-2 border-black text-xs font-bold leading-relaxed resize-none p-3"
                    />
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <div className="text-[10px] font-mono text-neutral-500">
                      Words: {currentAnswerText.trim() ? currentAnswerText.trim().split(/\s+/).length : 0}
                    </div>

                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleNextOrFinish}
                      className="text-xs shadow-[2px_2px_0px_#000] flex items-center gap-1.5"
                    >
                      <span>{currentIdx + 1 < questions.length ? "Submit Answer & Next" : "Submit & Evaluate"}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        )}

        {phase === "evaluating" && (
          <div className="py-24 text-center space-y-4 max-w-md mx-auto border-2 border-black rounded-[5px] bg-white shadow-[6px_6px_0px_#000] p-8">
            <div className="w-12 h-12 border-4 border-black border-t-transparent animate-spin mx-auto rounded-full" />
            <div className="space-y-1">
              <h2 className="text-xl font-black uppercase tracking-tight">
                Evaluating Candidate Performance
              </h2>
              <p className="text-xs text-neutral-600 font-medium leading-relaxed">
                Analyzing Technical Architecture, Problem Solving, and STAR Structure using your configured BYOK LLM gateway...
              </p>
            </div>
          </div>
        )}

        {phase === "scorecard" && scorecard && (
          <div className="space-y-6">
            <div className="border-2 border-black rounded-[5px] p-6 bg-white shadow-[6px_6px_0px_#000] flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-6">
                <div className="relative w-28 h-28 shrink-0">
                  <svg viewBox="0 0 36 36" className="w-28 h-28 -rotate-90">
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e5e5e5" strokeWidth="3" />
                    <circle
                      cx="18"
                      cy="18"
                      r="15.9"
                      fill="none"
                      stroke="#000"
                      strokeWidth="3"
                      strokeDasharray={`${scorecard.overall_score} 100`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-black text-black">{scorecard.overall_score}</span>
                    <span className="text-[9px] font-black uppercase text-neutral-500">/100</span>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-black uppercase text-neutral-500">Hiring Committee Verdict:</span>
                    <span className="px-3 py-0.5 text-xs font-black uppercase bg-black text-white rounded-[4px] shadow-[2px_2px_0px_#000]">
                      {scorecard.verdict}
                    </span>
                  </div>
                  <h2 className="text-xl font-black uppercase tracking-tight text-black">
                    {scorecard.position} Mock Evaluation
                  </h2>
                  <p className="text-xs text-neutral-600 font-medium">
                    Evaluated natively via BYOK Gateway. Scores are recorded in your persistent placement history.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    setPhase("lobby");
                    setScorecard(null);
                  }}
                  className="text-xs border-2 border-black shadow-[2px_2px_0px_#000] flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Retake Interview</span>
                </Button>

                <Link href="/">
                  <Button
                    variant="primary"
                    size="sm"
                    className="text-xs shadow-[2px_2px_0px_#000] flex items-center gap-1.5"
                  >
                    <span>Back to Dashboard</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </Link>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Technical Core", value: scorecard.param_scores.technical, icon: <TrendingUp className="w-4 h-4" /> },
                { label: "Problem Solving", value: scorecard.param_scores.problem_solving, icon: <Target className="w-4 h-4" /> },
                { label: "STAR Behavioural", value: scorecard.param_scores.behavioural, icon: <Award className="w-4 h-4" /> },
                { label: "Communication & Clarity", value: scorecard.param_scores.clarity, icon: <MessageSquare className="w-4 h-4" /> },
              ].map(({ label, value, icon }) => (
                <div key={label} className="border-2 border-black rounded-[5px] p-4 bg-white shadow-[3px_3px_0px_#000] space-y-2 text-center">
                  <div className="flex items-center justify-center gap-1.5 text-neutral-600">
                    {icon}
                    <span className="text-[10px] font-black uppercase">{label}</span>
                  </div>
                  <div className="text-2xl font-black text-black">
                    {value}<span className="text-xs text-neutral-400 font-bold">/100</span>
                  </div>
                  <div className="w-full bg-neutral-200 rounded-full h-2 border border-black overflow-hidden">
                    <div className="bg-black h-2 rounded-full" style={{ width: `${value}%` }} />
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {scorecard.strengths && scorecard.strengths.length > 0 && (
                <div className="border-2 border-black rounded-[5px] p-5 bg-white shadow-[4px_4px_0px_#000] space-y-3">
                  <div className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5 text-black">
                    <CheckCircle2 className="w-4 h-4 text-black" />
                    <span>Key Performance Strengths</span>
                  </div>
                  <ul className="space-y-2">
                    {scorecard.strengths.map((s, i) => (
                      <li key={i} className="text-xs font-medium text-neutral-800 flex items-start gap-2">
                        <span className="font-black text-black shrink-0">+</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {scorecard.improvements && scorecard.improvements.length > 0 && (
                <div className="border-2 border-black rounded-[5px] p-5 bg-neutral-50 border-2 border-black shadow-[4px_4px_0px_#000] space-y-3">
                  <div className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5 text-black">
                    <Lightbulb className="w-4 h-4 text-black" />
                    <span>Targeted Improvement Areas</span>
                  </div>
                  <ul className="space-y-2">
                    {scorecard.improvements.map((imp, i) => (
                      <li key={i} className="text-xs font-medium text-neutral-800 flex items-start gap-2">
                        <span className="font-black text-neutral-500 shrink-0">→</span>
                        <span>{imp}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="border-2 border-black rounded-[5px] bg-white shadow-[4px_4px_0px_#000] p-6 space-y-4">
              <div className="text-xs font-black uppercase tracking-wider flex items-center gap-2 border-b-2 border-black pb-3">
                <Terminal className="w-4 h-4 text-black" />
                <span>Question-by-Question Transcript & Candidate Response Audit</span>
              </div>

              <div className="space-y-4">
                {scorecard.questions_and_answers.map((qa, idx) => (
                  <div key={idx} className="p-4 border-2 border-black rounded-[5px] bg-neutral-50 space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-black uppercase bg-black text-white px-2 py-0.5 rounded-[3px]">
                        Round {idx + 1}: {qa.category.replace("_", " ")}
                      </span>
                    </div>
                    <div className="text-xs font-black text-black">
                      Q: {qa.question}
                    </div>
                    <div className="text-xs text-neutral-700 font-medium bg-white border border-neutral-300 p-2.5 rounded-[4px]">
                      A: {qa.answer}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
