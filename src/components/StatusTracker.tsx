"use client";

import { CheckCircle, Circle, Loader2, XCircle } from "lucide-react";
import { SESSION_STATUS_STEPS } from "@/lib/constants";
import type { SessionStatus } from "@/lib/types";

interface StatusTrackerProps {
  status: SessionStatus;
  errorMessage?: string | null;
}

export default function StatusTracker({ status, errorMessage }: StatusTrackerProps) {
  const currentIndex = SESSION_STATUS_STEPS.findIndex((s) => s.key === status);

  return (
    <div className="space-y-3">
      {SESSION_STATUS_STEPS.map((step, i) => {
        const isComplete = currentIndex > i;
        const isCurrent = step.key === status;
        const isError = status === "error" && isCurrent;

        return (
          <div key={step.key} className="flex items-center gap-3">
            {isError ? (
              <XCircle className="h-5 w-5 text-red-400" />
            ) : isComplete ? (
              <CheckCircle className="h-5 w-5 text-emerald-400" />
            ) : isCurrent ? (
              <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
            ) : (
              <Circle className="h-5 w-5 text-zinc-600" />
            )}
            <span
              className={`text-sm ${
                isError
                  ? "text-red-400"
                  : isComplete
                    ? "text-emerald-400"
                    : isCurrent
                      ? "text-cyan-300"
                      : "text-zinc-500"
              }`}
            >
              {step.label}
            </span>
          </div>
        );
      })}

      {status === "error" && errorMessage && (
        <div className="mt-2 rounded-lg bg-red-500/10 px-3 py-2 text-xs text-red-400">
          {errorMessage}
        </div>
      )}
    </div>
  );
}
