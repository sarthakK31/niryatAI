"use client";
import { useState, useEffect } from "react";
import AuthLayout from "@/components/AuthLayout";
import { readiness } from "@/lib/api";
import { Check, Circle, ChevronDown, ChevronRight } from "lucide-react";

interface Substep {
  id: number;
  substep_number: number;
  title: string;
  description: string | null;
  completed: boolean;
}

interface Step {
  step_number: number;
  title: string;
  description: string | null;
  category: string;
  substeps: Substep[];
  completed_count: number;
  total_count: number;
}

interface Summary {
  total_substeps: number;
  completed_substeps: number;
  percentage: number;
  next_step: string;
}

const categoryColors: Record<string, string> = {
  registration: "text-blue-400",
  compliance: "text-purple-400",
  research: "text-cyan-400",
  documentation: "text-amber-400",
  logistics: "text-emerald-400",
  finance: "text-pink-400",
};

export default function ReadinessPage() {
  const [steps, setSteps] = useState<Step[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  const loadData = () => {
    readiness.steps().then(setSteps).catch(console.error);
    readiness.summary().then(setSummary).catch(console.error);
  };

  useEffect(loadData, []);

  const toggleSubstep = async (substepId: number, currentlyCompleted: boolean) => {
    await readiness.mark(substepId, !currentlyCompleted);
    loadData();
  };

  return (
    <AuthLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Export Readiness Tracker</h1>
          <p className="text-[var(--text-secondary)] mt-1">
            Complete each step to become export-ready
          </p>
        </div>

        {/* Overall Progress */}
        {summary && (
          <div className="bg-[var(--bg-card)] rounded-xl p-6 border border-[var(--border)]">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold">Overall Progress</h3>
              <span className="text-2xl font-bold text-[var(--success)]">
                {summary.percentage}%
              </span>
            </div>
            <div className="w-full bg-[var(--border)] rounded-full h-3">
              <div
                className="bg-gradient-to-r from-[var(--primary-light)] to-[var(--success)] h-3 rounded-full transition-all duration-500"
                style={{ width: `${summary.percentage}%` }}
              />
            </div>
            <p className="text-sm text-[var(--text-secondary)] mt-3">
              {summary.completed_substeps} of {summary.total_substeps} steps completed
              {summary.next_step !== "All complete!" && (
                <span className="text-[var(--accent)]"> — Next: {summary.next_step}</span>
              )}
            </p>
          </div>
        )}

        {/* Steps */}
        <div className="space-y-3">
          {steps.map((step) => {
            const isExpanded = expanded === step.step_number;
            const isComplete = step.completed_count === step.total_count;

            return (
              <div
                key={step.step_number}
                className="bg-[var(--bg-card)] rounded-xl border border-[var(--border)] overflow-hidden"
              >
                {/* Step header */}
                <button
                  onClick={() => setExpanded(isExpanded ? null : step.step_number)}
                  className="w-full flex items-center gap-4 p-5 text-left hover:bg-[var(--border)]/30 transition-colors"
                >
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
                      isComplete
                        ? "bg-[var(--success)] text-white"
                        : "bg-[var(--border)] text-[var(--text-secondary)]"
                    }`}
                  >
                    {isComplete ? <Check size={20} /> : step.step_number}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{step.title}</h3>
                      <span
                        className={`text-xs uppercase tracking-wide ${
                          categoryColors[step.category] || "text-gray-400"
                        }`}
                      >
                        {step.category}
                      </span>
                    </div>
                    <p className="text-sm text-[var(--text-secondary)]">
                      {step.completed_count}/{step.total_count} completed
                    </p>
                  </div>
                  {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                </button>

                {/* Substeps */}
                {isExpanded && (
                  <div className="border-t border-[var(--border)] px-5 py-3 space-y-2">
                    {step.description && (
                      <p className="text-sm text-[var(--text-secondary)] pb-2">
                        {step.description}
                      </p>
                    )}
                    {step.substeps.map((sub) => (
                      <button
                        key={sub.id}
                        onClick={() => toggleSubstep(sub.id, sub.completed)}
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[var(--border)]/30 transition-colors text-left"
                      >
                        {sub.completed ? (
                          <Check size={18} className="text-[var(--success)] shrink-0" />
                        ) : (
                          <Circle size={18} className="text-[var(--text-secondary)] shrink-0" />
                        )}
                        <div>
                          <span
                            className={`text-sm ${
                              sub.completed
                                ? "line-through text-[var(--text-secondary)]"
                                : "text-[var(--text-primary)]"
                            }`}
                          >
                            {sub.title}
                          </span>
                          {sub.description && (
                            <p className="text-xs text-[var(--text-secondary)]">
                              {sub.description}
                            </p>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </AuthLayout>
  );
}
