"use client";

import { Layers } from "lucide-react";
import StatusTracker from "./StatusTracker";
import DownloadButton from "./DownloadButton";
import SlidePreview from "./SlidePreview";
import type { SessionStatus, SlideData } from "@/lib/types";

interface RenderCanvasProps {
  status: SessionStatus | "idle";
  errorMessage?: string | null;
  runId: number | null;
  slideData?: SlideData[] | null;
  themeId: string;
}

export default function RenderCanvas({
  status,
  errorMessage,
  runId,
  slideData,
  themeId,
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
      <div className="flex h-full flex-col">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-zinc-300">
            &#x2705; {slideData?.length ?? 0}장 생성 완료
          </h2>
          <div className="w-44">
            <DownloadButton runId={runId} />
          </div>
        </div>
        {slideData && slideData.length > 0 ? (
          <div className="flex-1 overflow-hidden rounded-xl border border-zinc-800">
            <SlidePreview slides={slideData} themeId={themeId} />
          </div>
        ) : (
          <div className="flex flex-1 items-center justify-center text-sm text-zinc-500">
            미리보기를 사용할 수 없습니다. PPTX를 다운로드하세요.
          </div>
        )}
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
