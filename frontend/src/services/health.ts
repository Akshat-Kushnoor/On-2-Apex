import { api } from "@/library/api";

export interface HealthResponse {
  status: string;
}

export interface ReadyResponse {
  status: string;
  database: string;
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
      return await api.get<ReadyResponse>("/ready");
    } catch {
      return { status: "unavailable", database: "disconnected" };
    }
  },
};
