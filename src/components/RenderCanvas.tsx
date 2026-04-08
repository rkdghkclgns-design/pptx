"use client";

import { Layers } from "lucide-react";
import StatusTracker from "./StatusTracker";
import DownloadButton from "./DownloadButton";
import type { SessionStatus } from "@/lib/types";

interface RenderCanvasProps {
  status: SessionStatus | "idle";
  errorMessage?: string | null;
  runId: number | null;
}

export default function RenderCanvas({
  status,
  errorMessage,
  runId,
}: RenderCanvasProps) {
  if (status === "idle") {
    return (
      <div className="flex h-full flex-col items-center justify-center text-center">
        <div className="mb-6 rounded-full border border-zinc-700/50 p-6">
          <Layers className="h-12 w-12 text-zinc-600" />
        </div>
        <h2 className="text-xl font-bold text-zinc-400">통합 렌더링 캔버스</h2>
        <p className="mt-2 max-w-sm text-sm text-zinc-500">
          다양한 문서를 병합하여 일관된 디자인의 프레젠테이션을 생성합니다.
        </p>
      </div>
    );
  }

  if (status === "complete") {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-6 text-center">
        <div className="rounded-full border border-emerald-500/30 bg-emerald-500/10 p-6">
          <Layers className="h-12 w-12 text-emerald-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-zinc-200">생성 완료!</h2>
          <p className="mt-1 text-sm text-zinc-400">
            프레젠테이션이 성공적으로 생성되었습니다.
          </p>
        </div>
        <div className="w-64">
          <DownloadButton runId={runId} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col items-center justify-center gap-8">
      <div className="rounded-full border border-cyan-500/30 bg-cyan-500/10 p-6">
        <Layers className="h-12 w-12 text-cyan-400" />
      </div>
      <div className="text-center">
        <h2 className="text-lg font-bold text-zinc-200">프레젠테이션 생성 중</h2>
        <p className="mt-1 text-sm text-zinc-400">잠시만 기다려주세요...</p>
      </div>
      <StatusTracker
        status={status as SessionStatus}
        errorMessage={errorMessage}
      />
    </div>
  );
}
