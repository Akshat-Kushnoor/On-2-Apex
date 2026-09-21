"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/firebase/AuthContext";
import { Lock, Mail, ArrowRight, ShieldCheck, KeyRound } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [socialLoading, setSocialLoading] = useState<string | null>(null);

  const { loginWithEmail, loginWithGoogle, loginWithGithub } = useAuth();
  const router = useRouter();

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await loginWithEmail(email, password);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to sign in with email and password.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSocialLogin = async (provider: "google" | "github") => {
    setError("");
    setSocialLoading(provider);

    try {
      if (provider === "google") {
        await loginWithGoogle();
      } else {
        await loginWithGithub();
      }
      router.push("/");
    } catch (err: any) {
      setError(err.message || `Failed to sign in with ${provider}.`);
    } finally {
      setSocialLoading(null);
    }
  };

  return (
    <AppShell>
      <div className="flex items-center justify-center min-h-[calc(100vh-140px)] py-8">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-[5px] bg-black text-white text-xs font-bold uppercase tracking-wider">
              <ShieldCheck className="w-3.5 h-3.5 text-lime-400" />
              <span>Authentication Gate</span>
            </div>
            <h1 className="text-3xl font-black tracking-tight uppercase">
              Welcome Back
            </h1>
            <p className="text-sm text-neutral-600">
              Access your personalized placement command center and ATS workflows.
            </p>
          </div>

          <Card className="border-2 border-black bg-white shadow-[6px_6px_0px_#000]">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl font-black uppercase">
                Sign In
              </CardTitle>
              <CardDescription>
                Choose your preferred sign-in method to continue.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {error && (
                <div className="bg-red-50 border-2 border-red-500 text-red-700 px-4 py-2.5 rounded-[5px] text-xs font-bold flex items-start gap-2">
                  <span className="font-black uppercase tracking-wider">[ERROR]</span>
                  <span>{error}</span>
                </div>
              )}

              {/* Social Login Buttons */}
              <div className="grid grid-cols-2 gap-3">
                <Button
                  type="button"
                  variant="secondary"
                  size="md"
                  onClick={() => handleSocialLogin("google")}
                  disabled={socialLoading !== null || isSubmitting}
                  className="w-full flex items-center justify-center gap-2 border-2 border-black bg-white text-black hover:bg-neutral-100 shadow-[3px_3px_0px_#000]"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                    />
                  </svg>
                  <span>{socialLoading === "google" ? "Connecting..." : "Google"}</span>
                </Button>

                <Button
                  type="button"
                  variant="secondary"
                  size="md"
                  onClick={() => handleSocialLogin("github")}
                  disabled={socialLoading !== null || isSubmitting}
                  className="w-full flex items-center justify-center gap-2 border-2 border-black bg-white text-black hover:bg-neutral-100 shadow-[3px_3px_0px_#000]"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path
                      fillRule="evenodd"
                      clipRule="evenodd"
                      d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                    />
                  </svg>
                  <span>{socialLoading === "github" ? "Connecting..." : "GitHub"}</span>
                </Button>
              </div>

              {/* Divider */}
              <div className="relative flex py-2 items-center">
                <div className="flex-grow border-t-2 border-neutral-200"></div>
                <span className="flex-shrink mx-3 text-neutral-500 text-xs font-bold uppercase tracking-wider">
                  or email & password
                </span>
                <div className="flex-grow border-t-2 border-neutral-200"></div>
              </div>

              {/* Email / Password Form */}
              <form onSubmit={handleEmailLogin} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5" />
                    <span>Email Address</span>
                  </label>
                  <Input
                    type="email"
                    placeholder="student@university.edu"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="border-2 border-black"
                  />
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5">
                      <Lock className="w-3.5 h-3.5" />
                      <span>Password</span>
                    </label>
                    <Link
                      href="/reset-password"
                      className="text-xs font-black text-neutral-600 hover:text-black hover:underline flex items-center gap-1"
                    >
                      <KeyRound className="w-3 h-3" />
                      <span>Reset Password?</span>
                    </Link>
                  </div>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="border-2 border-black"
                  />
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  disabled={isSubmitting || socialLoading !== null}
                  className="w-full mt-2 bg-black text-white hover:bg-neutral-800 shadow-[4px_4px_0px_#000] flex items-center justify-center gap-2"
                >
                  <span>{isSubmitting ? "Authenticating..." : "Sign In with Password"}</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </form>
            </CardContent>

            <CardFooter className="pt-2 border-t-2 border-neutral-100 flex flex-col gap-2 bg-neutral-50 rounded-b-[5px]">
              <div className="text-center text-xs font-bold text-neutral-600">
                Don't have an account yet?{" "}
                <Link
                  href="/register"
                  className="text-black font-black underline hover:text-neutral-700"
                >
                  Create Student Account
                </Link>
              </div>
            </CardFooter>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
