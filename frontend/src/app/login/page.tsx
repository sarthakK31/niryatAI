"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { auth } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await auth.login({ email, password });
      login(res.access_token, res.user);
      await new Promise((r) => setTimeout(r, 100));
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold">
            <span className="text-[var(--accent)]">Niryat</span>{" "}
            <span className="text-[var(--primary-light)]">AI</span>
          </h1>
          <p className="text-[var(--text-secondary)] mt-2">
            Export Intelligence for Indian MSMEs
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-[var(--bg-card)] rounded-xl p-8 border border-[var(--border)] space-y-5"
        >
          <h2 className="text-xl font-semibold text-center">Sign In12</h2>

          {error && (
            <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-2 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-[var(--primary)] hover:bg-[var(--primary-light)] text-white font-medium transition-colors disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>

          <p className="text-center text-sm text-[var(--text-secondary)]">
            New exporter?{" "}
            <Link href="/register" className="text-[var(--primary-light)] hover:underline">
              Create account
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
