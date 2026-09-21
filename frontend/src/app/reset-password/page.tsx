"use client";

import React, { useState, useEffect } from "react";
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
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/firebase/AuthContext";
import { KeyRound, Mail, Lock, CheckCircle2, ArrowLeft, ArrowRight, ShieldAlert } from "lucide-react";

export default function ResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [step, setStep] = useState<1 | 2>(1);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { requestPasswordReset, confirmPasswordReset } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const urlToken = searchParams.get("token");
    if (urlToken) {
      setToken(urlToken);
      setStep(2);
    }
  }, [searchParams]);

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccessMessage("");
    setIsSubmitting(true);

    try {
      const res = await requestPasswordReset(email);
      setSuccessMessage(
        res.message || "A password reset token has been generated."
      );
      if (res.reset_token) {
        setToken(res.reset_token);
      }
      setStep(2);
    } catch (err: any) {
      setError(err.message || "Failed to request password reset.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirmReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccessMessage("");

    if (newPassword !== confirmPassword) {
      setError("New password and confirmation do not match.");
      return;
    }

    if (newPassword.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    setIsSubmitting(true);

    try {
      const res = await confirmPasswordReset(token, newPassword);
      setSuccessMessage(res.message || "Password successfully updated!");
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err: any) {
      setError(err.message || "Invalid or expired reset token.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell>
      <div className="flex items-center justify-center min-h-[calc(100vh-140px)] py-8">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-[5px] bg-black text-white text-xs font-bold uppercase tracking-wider">
              <KeyRound className="w-3.5 h-3.5 text-lime-400" />
              <span>Password Recovery</span>
            </div>
            <h1 className="text-3xl font-black tracking-tight uppercase">
              Reset Password
            </h1>
            <p className="text-sm text-neutral-600">
              {step === 1
                ? "Enter your registered email address to receive a secure recovery token."
                : "Enter your recovery token and set your new account password."}
            </p>
          </div>

          <Card className="border-2 border-black bg-white shadow-[6px_6px_0px_#000]">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl font-black uppercase">
                {step === 1 ? "Step 1: Request Reset" : "Step 2: Update Credentials"}
              </CardTitle>
              <CardDescription>
                {step === 1
                  ? "We'll generate a verification code for your account."
                  : "Choose a strong password with at least 6 characters."}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {error && (
                <div className="bg-red-50 border-2 border-red-500 text-red-700 px-4 py-2.5 rounded-[5px] text-xs font-bold flex items-start gap-2">
                  <ShieldAlert className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              {successMessage && (
                <div className="bg-lime-50 border-2 border-black text-black px-4 py-2.5 rounded-[5px] text-xs font-bold flex items-start gap-2 shadow-[2px_2px_0px_#000]">
                  <CheckCircle2 className="w-4 h-4 text-black flex-shrink-0 mt-0.5" />
                  <span>{successMessage}</span>
                </div>
              )}

              {step === 1 ? (
                <form onSubmit={handleRequestReset} className="space-y-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5">
                      <Mail className="w-3.5 h-3.5" />
                      <span>Account Email</span>
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

                  <Button
                    type="submit"
                    variant="primary"
                    size="md"
                    disabled={isSubmitting}
                    className="w-full bg-black text-white hover:bg-neutral-800 shadow-[4px_4px_0px_#000] flex items-center justify-center gap-2"
                  >
                    <span>{isSubmitting ? "Generating Token..." : "Send Reset Token"}</span>
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </form>
              ) : (
                <form onSubmit={handleConfirmReset} className="space-y-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5">
                      <KeyRound className="w-3.5 h-3.5" />
                      <span>Reset Token</span>
                    </label>
                    <Input
                      type="text"
                      placeholder="Paste your reset token here"
                      value={token}
                      onChange={(e) => setToken(e.target.value)}
                      required
                      className="border-2 border-black font-mono text-xs"
                    />
                    <p className="text-[11px] text-neutral-500">
                      In development mode, token is auto-filled and printed to backend terminal.
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5">
                      <Lock className="w-3.5 h-3.5" />
                      <span>New Password</span>
                    </label>
                    <Input
                      type="password"
                      placeholder="••••••••"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                      minLength={6}
                      className="border-2 border-black"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5">
                      <Lock className="w-3.5 h-3.5" />
                      <span>Confirm New Password</span>
                    </label>
                    <Input
                      type="password"
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      minLength={6}
                      className="border-2 border-black"
                    />
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    size="md"
                    disabled={isSubmitting}
                    className="w-full bg-black text-white hover:bg-neutral-800 shadow-[4px_4px_0px_#000] flex items-center justify-center gap-2"
                  >
                    <span>{isSubmitting ? "Updating Password..." : "Update Password & Log In"}</span>
                    <ArrowRight className="w-4 h-4" />
                  </Button>

                  <div className="text-center pt-2">
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="text-xs font-bold text-neutral-600 hover:text-black underline"
                    >
                      ← Need to change email? Start over
                    </button>
                  </div>
                </form>
              )}
            </CardContent>

            <CardFooter className="pt-2 border-t-2 border-neutral-100 flex items-center justify-center bg-neutral-50 rounded-b-[5px]">
              <Link
                href="/login"
                className="text-xs font-black text-black hover:underline flex items-center gap-1.5"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Return to Login Screen</span>
              </Link>
            </CardFooter>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
