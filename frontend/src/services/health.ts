import { api } from "@/library/api";

export interface HealthResponse {
  status: string;
}

export interface ReadyResponse {
  status: string;
  database: string;
  checks?: {
    database?: string;
    local_db_directory?: string;
  };
}

export const healthService = {
  checkHealth: async (): Promise<boolean> => {
    try {
      const data = await api.get<HealthResponse>("/health");
      return data.status === "healthy" || data.status === "ok";
    } catch {
      return false;
    }
  },

  checkReady: async (): Promise<ReadyResponse> => {
    try {
      const res = await api.get<{
        status: string;
        database?: string;
        checks?: { database?: string; local_db_directory?: string };
      }>("/ready");
      return {
        status: res.status,
        database: res.database || res.checks?.database || "connected",
        checks: res.checks,
      };
    } catch {
      return { status: "unavailable", database: "disconnected" };
    }
  },
};
