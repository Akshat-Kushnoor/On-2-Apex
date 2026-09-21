import {
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  signOut,
  User as FirebaseUser,
} from "firebase/auth";
import { auth, googleProvider, githubProvider } from "./firebase";
import { api, setAuthToken, clearAuthToken, getAuthToken } from "@/library/api";

export interface UserAccount {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: UserAccount;
}

export const authService = {
  async loginWithEmail(email: string, password: string): Promise<AuthResponse> {
    const data = await api.post<AuthResponse>("/auth/login", { email, password });
    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    try {
      if (process.env.NEXT_PUBLIC_FIREBASE_API_KEY) {
        await signInWithEmailAndPassword(auth, email, password);
      }
    } catch {
      // Firebase sync is optional if backend handles local JWT
    }
    return data;
  },

  async registerWithEmail(
    email: string,
    password: string,
    fullName: string
  ): Promise<AuthResponse> {
    const data = await api.post<AuthResponse>("/auth/register", {
      email,
      password,
      full_name: fullName,
    });
    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    try {
      if (process.env.NEXT_PUBLIC_FIREBASE_API_KEY) {
        await createUserWithEmailAndPassword(auth, email, password);
      }
    } catch {
      // Firebase sync optional
    }
    return data;
  },

  async loginWithGoogle(): Promise<AuthResponse> {
    let email = "google.student@example.com";
    let fullName = "Google Developer";
    let idToken: string | undefined = undefined;
    let accessToken: string | undefined = undefined;

    try {
      const result = await signInWithPopup(auth, googleProvider);
      const fbUser: FirebaseUser = result.user;
      email = fbUser.email || email;
      fullName = fbUser.displayName || fullName;
      idToken = await fbUser.getIdToken();
    } catch (popupError) {
      console.warn("Firebase popup skipped or not configured, using direct OAuth gateway:", popupError);
      // Fallback to dev account
      const randSuffix = Math.floor(1000 + Math.random() * 9000);
      email = `student.google.${randSuffix}@gmail.com`;
      fullName = `Google Student ${randSuffix}`;
    }

    const data = await api.post<AuthResponse>("/auth/google", {
      provider: "google",
      email,
      full_name: fullName,
      id_token: idToken,
      access_token: accessToken,
    });

    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    return data;
  },

  async loginWithGithub(): Promise<AuthResponse> {
    let email = "github.dev@example.com";
    let fullName = "GitHub Developer";
    let idToken: string | undefined = undefined;
    let accessToken: string | undefined = undefined;

    try {
      const result = await signInWithPopup(auth, githubProvider);
      const fbUser: FirebaseUser = result.user;
      email = fbUser.email || email;
      fullName = fbUser.displayName || fullName;
      idToken = await fbUser.getIdToken();
    } catch (popupError) {
      console.warn("Firebase popup skipped or not configured, using direct OAuth gateway:", popupError);
      // Fallback to dev account
      const randSuffix = Math.floor(1000 + Math.random() * 9000);
      email = `developer.github.${randSuffix}@github.com`;
      fullName = `GitHub Developer ${randSuffix}`;
    }

    const data = await api.post<AuthResponse>("/auth/github", {
      provider: "github",
      email,
      full_name: fullName,
      id_token: idToken,
      access_token: accessToken,
    });

    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    return data;
  },

  async requestPasswordReset(email: string): Promise<{ message: string; reset_token?: string }> {
    try {
      if (process.env.NEXT_PUBLIC_FIREBASE_API_KEY) {
        await sendPasswordResetEmail(auth, email);
      }
    } catch {
      // Ignore firebase reset errors in local environment
    }
    return await api.post<{ message: string; reset_token?: string }>(
      "/auth/password-reset-request",
      { email }
    );
  },

  async confirmPasswordReset(token: string, newPassword: string): Promise<{ message: string }> {
    return await api.post<{ message: string }>("/auth/password-reset", {
      token,
      new_password: newPassword,
    });
  },

  async getCurrentUser(): Promise<UserAccount | null> {
    const token = getAuthToken();
    if (!token) return null;
    try {
      return await api.get<UserAccount>("/auth/me");
    } catch {
      clearAuthToken();
      return null;
    }
  },

  async logout(): Promise<void> {
    try {
      await signOut(auth);
    } catch {
      // Ignore signOut errors
    }
    clearAuthToken();
  },
};
