"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { auth } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    company_name: "",
    state: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await auth.register(form);
      login(res.access_token, res.user);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold">
            <span className="text-[var(--accent)]">Niryat</span>{" "}
            <span className="text-[var(--primary-light)]">AI</span>
          </h1>
          <p className="text-[var(--text-secondary)] mt-2">Start your export journey</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-[var(--bg-card)] rounded-xl p-8 border border-[var(--border)] space-y-4"
        >
          <h2 className="text-xl font-semibold text-center">Create Account</h2>

          {error && (
            <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-2 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">Full Name</label>
            <input
              type="text"
              required
              value={form.full_name}
              onChange={(e) => update("full_name", e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">Password</label>
            <input
              type="password"
              required
              minLength={6}
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">
              Company Name (optional)
            </label>
            <input
              type="text"
              value={form.company_name}
              onChange={(e) => update("company_name", e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">
              State (optional)
            </label>
            <input
              type="text"
              value={form.state}
              onChange={(e) => update("state", e.target.value)}
              placeholder="e.g. Maharashtra"
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-[var(--primary)] hover:bg-[var(--primary-light)] text-white font-medium transition-colors disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>

          <p className="text-center text-sm text-[var(--text-secondary)]">
            Already have an account?{" "}
            <Link href="/login" className="text-[var(--primary-light)] hover:underline">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
