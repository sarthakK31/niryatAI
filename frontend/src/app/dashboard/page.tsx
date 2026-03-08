"use client";
import { useEffect, useState } from "react";
import AuthLayout from "@/components/AuthLayout";
import { dashboard } from "@/lib/api";
import Link from "next/link";
import {
  MessageSquare,
  CheckCircle2,
  Globe2,
  TrendingUp,
  ArrowRight,
} from "lucide-react";

interface DashboardData {
  user: { name: string; company: string | null };
  readiness: {
    total_substeps: number;
    completed_substeps: number;
    percentage: number;
    next_step: string;
  };
  top_markets: Array<{
    country: string;
    hs_code: string;
    opportunity_score: number;
  }>;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);

useEffect(() => {
  const token = localStorage.getItem("niryat_token");

  if (!token) {
    window.location.href = "/login";
    return;
  }

  dashboard.get()
    .then(setData)
    .catch(console.error);
}, []);

  return (
    <AuthLayout>
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">
            Welcome back{data ? `, ${data.user.name}` : ""}
          </h1>
          <p className="text-[var(--text-secondary)] mt-1">
            Here is your export readiness overview
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Readiness Progress */}
          <div className="bg-[var(--bg-card)] rounded-xl p-6 border border-[var(--border)]">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle2 className="text-[var(--success)]" size={24} />
              <h3 className="font-semibold">Export Readiness</h3>
            </div>
            <div className="text-4xl font-bold text-[var(--success)]">
              {data?.readiness.percentage ?? 0}%
            </div>
            <div className="w-full bg-[var(--border)] rounded-full h-2 mt-3">
              <div
                className="bg-[var(--success)] h-2 rounded-full transition-all"
                style={{ width: `${data?.readiness.percentage ?? 0}%` }}
              />
            </div>
            <p className="text-sm text-[var(--text-secondary)] mt-3">
              {data?.readiness.completed_substeps ?? 0} of{" "}
              {data?.readiness.total_substeps ?? 0} steps completed
            </p>
            {data?.readiness.next_step && (
              <p className="text-sm text-[var(--accent)] mt-1">
                Next: {data.readiness.next_step}
              </p>
            )}
          </div>

          {/* Top Market */}
          <div className="bg-[var(--bg-card)] rounded-xl p-6 border border-[var(--border)]">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="text-[var(--primary-light)]" size={24} />
              <h3 className="font-semibold">Top Market</h3>
            </div>
            {data?.top_markets?.[0] ? (
              <>
                <div className="text-3xl font-bold">{data.top_markets[0].country}</div>
                <p className="text-sm text-[var(--text-secondary)] mt-1">
                  HS {data.top_markets[0].hs_code} — Score:{" "}
                  {data.top_markets[0].opportunity_score?.toFixed(2)}
                </p>
              </>
            ) : (
              <p className="text-[var(--text-secondary)]">
                Add your HS codes in profile to see market recommendations
              </p>
            )}
          </div>

          {/* AI Assistant */}
          <Link
            href="/chat"
            className="bg-gradient-to-br from-[var(--primary)] to-[var(--primary-light)] rounded-xl p-6 border border-[var(--border)] hover:opacity-90 transition-opacity"
          >
            <div className="flex items-center gap-3 mb-4">
              <MessageSquare size={24} />
              <h3 className="font-semibold">AI Assistant</h3>
            </div>
            <p className="text-sm text-blue-100">
              Ask questions about exporting, market data, compliance, and more.
            </p>
            <div className="flex items-center gap-2 mt-4 text-sm font-medium">
              Start a conversation <ArrowRight size={16} />
            </div>
          </Link>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            href="/readiness"
            className="bg-[var(--bg-card)] rounded-xl p-6 border border-[var(--border)] hover:border-[var(--primary-light)] transition-colors group"
          >
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-lg">Export Readiness Tracker</h3>
                <p className="text-sm text-[var(--text-secondary)] mt-1">
                  Track your journey from registration to first shipment
                </p>
              </div>
              <ArrowRight
                className="text-[var(--text-secondary)] group-hover:text-white transition-colors"
                size={20}
              />
            </div>
          </Link>

          <Link
            href="/markets"
            className="bg-[var(--bg-card)] rounded-xl p-6 border border-[var(--border)] hover:border-[var(--primary-light)] transition-colors group"
          >
            <div className="flex justify-between items-center">
              <div>
                <div className="flex items-center gap-2">
                  <Globe2 size={20} className="text-[var(--accent)]" />
                  <h3 className="font-semibold text-lg">Market Intelligence</h3>
                </div>
                <p className="text-sm text-[var(--text-secondary)] mt-1">
                  Discover the best export markets for your products
                </p>
              </div>
              <ArrowRight
                className="text-[var(--text-secondary)] group-hover:text-white transition-colors"
                size={20}
              />
            </div>
          </Link>
        </div>
      </div>
    </AuthLayout>
  );
}
