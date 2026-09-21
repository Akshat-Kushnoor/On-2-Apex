"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
  authService,
  AuthResponse,
  UserAccount,
} from "./authService";
import { getAuthToken } from "@/library/api";

interface AuthContextType {
  user: UserAccount | null;
  token: string | null;
  loading: boolean;
  loginWithEmail: (email: string, password: string) => Promise<AuthResponse>;
  registerWithEmail: (
    email: string,
    password: string,
    fullName: string
  ) => Promise<AuthResponse>;
  loginWithGoogle: () => Promise<AuthResponse>;
  loginWithGithub: () => Promise<AuthResponse>;
  requestPasswordReset: (email: string) => Promise<{ message: string; reset_token?: string }>;
  confirmPasswordReset: (token: string, newPassword: string) => Promise<{ message: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<UserAccount | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    const currentToken = getAuthToken();
    setToken(currentToken);
    if (currentToken) {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } else {
      setUser(null);
    }
  };

  useEffect(() => {
    refreshUser().finally(() => setLoading(false));
  }, []);

  const loginWithEmail = async (email: string, password: string) => {
    const res = await authService.loginWithEmail(email, password);
    setToken(res.access_token);
    if (res.user) setUser(res.user);
    else await refreshUser();
    return res;
  };

  const registerWithEmail = async (
    email: string,
    password: string,
    fullName: string
  ) => {
    const res = await authService.registerWithEmail(email, password, fullName);
    setToken(res.access_token);
    if (res.user) setUser(res.user);
    else await refreshUser();
    return res;
  };

  const loginWithGoogle = async () => {
    const res = await authService.loginWithGoogle();
    setToken(res.access_token);
    if (res.user) setUser(res.user);
    else await refreshUser();
    return res;
  };

  const loginWithGithub = async () => {
    const res = await authService.loginWithGithub();
    setToken(res.access_token);
    if (res.user) setUser(res.user);
    else await refreshUser();
    return res;
  };

  const requestPasswordReset = async (email: string) => {
    return await authService.requestPasswordReset(email);
  };

  const confirmPasswordReset = async (token: string, newPassword: string) => {
    return await authService.confirmPasswordReset(token, newPassword);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        loginWithEmail,
        registerWithEmail,
        loginWithGoogle,
        loginWithGithub,
        requestPasswordReset,
        confirmPasswordReset,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
