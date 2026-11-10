import { api } from "@/library/api";

export interface InterviewQuestionItem {
  id: number;
  category: "technical" | "problem_solving" | "behavioural" | string;
  title: string;
  question: string;
  hint?: string | null;
}

export interface InterviewStartResponse {
  position: string;
  questions: InterviewQuestionItem[];
}

export interface InterviewAnswerItem {
  question_id: number;
  category: string;
  question: string;
  answer: string;
}

export interface InterviewEvaluateRequest {
  position: string;
  answers: InterviewAnswerItem[];
}

export interface InterviewScorecardOut {
  id: string;
  position: string;
  overall_score: number;
  verdict: "STRONG HIRE" | "HIRE" | "NEEDS WORK" | string;
  param_scores: {
    technical: number;
    problem_solving: number;
    behavioural: number;
    clarity: number;
    overall: number;
    [key: string]: number;
  };
  questions_and_answers: {
    question_id: number;
    category: string;
    question: string;
    answer: string;
  }[];
  strengths: string[];
  improvements: string[];
  created_at: string;
}

export interface InterviewSessionBrief {
  id: string;
  position: string;
  overall_score: number;
  verdict: string;
  param_scores: Record<string, number>;
  created_at: string;
}

export const interviewService = {
  async startInterview(position: string): Promise<InterviewStartResponse> {
    return await api.post<InterviewStartResponse>("/interviews/start", { position });
  },

  async evaluateInterview(payload: InterviewEvaluateRequest): Promise<InterviewScorecardOut> {
    return await api.post<InterviewScorecardOut>("/interviews/evaluate", payload);
  },

  async getLatestInterview(): Promise<InterviewScorecardOut | null> {
    try {
      return await api.get<InterviewScorecardOut | null>("/interviews/latest");
    } catch {
      return null;
    }
  },

  async getInterviewHistory(): Promise<InterviewSessionBrief[]> {
    try {
      return await api.get<InterviewSessionBrief[]>("/interviews/history");
    } catch {
      return [];
    }
  },
};
