import { Metadata } from "next";
import Link from "next/link";
import { Zap } from "lucide-react";
import { AuthForm } from "@/components/auth/auth-form";

export const metadata: Metadata = { title: "Connexion — AITools" };

export default function LoginPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background px-6 py-16">
      <Link href="/" className="flex items-center gap-2 mb-12">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent">
          <Zap className="h-4 w-4 text-white" />
        </div>
        <span className="font-semibold text-foreground">AITools</span>
      </Link>
      <AuthForm mode="login" />
    </div>
  );
}
