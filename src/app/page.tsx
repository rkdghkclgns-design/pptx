"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import SourceUploader from "@/components/SourceUploader";
import NotebookLMButton from "@/components/NotebookLMButton";
import TextSourceInput from "@/components/TextSourceInput";
import SettingsPanel from "@/components/SettingsPanel";
import ThemeSelector from "@/components/ThemeSelector";
import RenderCanvas from "@/components/RenderCanvas";
import { supabase } from "@/lib/supabase";
import { triggerBuild, getSessionStatus } from "@/lib/github";
import { STORAGE_BUCKET, POLL_INTERVAL_MS } from "@/lib/constants";
import { DEFAULT_THEME } from "@/lib/themes";
import type { UploadedFile, SessionSettings, SessionStatus, Session, SlideData } from "@/lib/types";

export default function Home() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [notebookUrl, setNotebookUrl] = useState<string | null>(null);
  const [textSource, setTextSource] = useState("");
  const [themeId, setThemeId] = useState(DEFAULT_THEME.id);
  const [settings, setSettings] = useState<SessionSettings>({
    slideCount: 5,
    duration: 5,
    aiEngine: "gemini-2.5-flash",
  });

  const [buildStatus, setBuildStatus] = useState<SessionStatus | "idle">("idle");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [runId, setRunId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [slideData, setSlideData] = useState<SlideData[] | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  const startPolling = useCallback(
    (sid: string) => {
      stopPolling();
      pollRef.current = setInterval(async () => {
        const session: Session | null = await getSessionStatus(sid);
        if (!session) return;

        setBuildStatus(session.status);
        if (session.github_run_id) setRunId(session.github_run_id);
        if (session.error_message) setErrorMessage(session.error_message);
        if (session.slide_data) setSlideData(session.slide_data);

        if (session.status === "complete" || session.status === "error") {
          stopPolling();
        }
      }, POLL_INTERVAL_MS);
    },
    [stopPolling]
  );

  const hasSources = files.length > 0 || !!notebookUrl || textSource.trim().length > 0;

  const handleGenerate = async () => {
    if (!hasSources) return;
    setIsSubmitting(true);
    setErrorMessage(null);
    setSlideData(null);
    setBuildStatus("uploading");

    try {
      // 1. Create session with text_source
      const { data: session, error: sessionError } = await supabase
        .from("sessions")
        .insert({
          status: "uploading",
          settings,
          notebook_url: notebookUrl,
          text_source: textSource.trim() || null,
          theme: themeId,
        })
        .select("id")
        .single();

      if (sessionError || !session) {
        throw new Error(sessionError?.message ?? "세션 생성에 실패했습니다.");
      }

      const sid = session.id;
      setSessionId(sid);

      // 2. Upload files to Supabase Storage
      const filePaths: string[] = [];
      for (const f of files) {
        const path = `${sid}/${f.name}`;
        const { error: uploadError } = await supabase.storage
          .from(STORAGE_BUCKET)
          .upload(path, f.file);

        if (uploadError) {
          throw new Error(`파일 업로드 실패: ${f.name}`);
        }
        filePaths.push(path);
      }

      // 3. Update session with file paths
      await supabase
        .from("sessions")
        .update({ file_paths: filePaths, status: "triggered" })
        .eq("id", sid);

      setBuildStatus("triggered");

      // 4. Trigger GitHub Actions
      const result = await triggerBuild(sid, settings);
      if (!result.success) {
        throw new Error(result.error ?? "빌드 트리거 실패");
      }

      // 5. Start polling for status
      startPolling(sid);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "알 수 없는 오류";
      setErrorMessage(message);
      setBuildStatus("error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const isBusy =
    isSubmitting || (buildStatus !== "idle" && buildStatus !== "complete" && buildStatus !== "error");

  return (
    <main className="flex min-h-screen">
      {/* Left Panel */}
      <div className="flex w-[420px] shrink-0 flex-col border-r border-zinc-800 bg-zinc-900/50">
        <div className="border-b border-zinc-800 px-6 py-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-cyan-400" />
            <h1 className="text-lg font-bold text-zinc-100">
              워크스페이스: 프로젝트 설정
            </h1>
          </div>
        </div>

        <div className="flex-1 space-y-6 overflow-y-auto px-6 py-6">
          {/* Source Data Section */}
          <div>
            <div className="mb-3 flex items-center justify-between">
              <div />
              <NotebookLMButton
                url={notebookUrl}
                onUrlChange={setNotebookUrl}
                disabled={isBusy}
              />
            </div>
            <SourceUploader
              files={files}
              onFilesChange={setFiles}
              notebookUrl={notebookUrl}
              disabled={isBusy}
            />
          </div>

          {/* Text Source Input */}
          <TextSourceInput
            value={textSource}
            onChange={setTextSource}
            disabled={isBusy}
          />

          {/* Settings Section */}
          <SettingsPanel
            settings={settings}
            onSettingsChange={setSettings}
            disabled={isBusy}
          />

          {/* Theme Section */}
          <ThemeSelector
            selected={themeId}
            onSelect={setThemeId}
            disabled={isBusy}
          />
        </div>

        {/* Generate Button */}
        <div className="border-t border-zinc-800 p-6">
          <button
            onClick={handleGenerate}
            disabled={!hasSources || isBusy}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-3.5 font-semibold text-white transition-all hover:from-cyan-400 hover:to-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Sparkles className="h-5 w-5" />
            )}
            {isSubmitting ? "생성 중..." : "프레젠테이션 생성"}
          </button>
          <p className="mt-2 text-center text-xs text-zinc-500">
            복수의 데이터를 연결하고 생성을 클릭하세요
          </p>
        </div>
      </div>

      {/* Right Panel */}
      <div className="flex flex-1 flex-col bg-zinc-950">
        <div className="border-b border-zinc-800 px-6 py-4">
          <p className="text-sm text-zinc-400">
            <span className="mr-1">&#x2728;</span>
            복수의 데이터를 연결하고 생성을 클릭하세요
          </p>
        </div>
        <div className="flex-1 p-8">
          <RenderCanvas
            status={buildStatus}
            errorMessage={errorMessage}
            runId={runId}
            slideData={slideData}
            themeId={themeId}
          />
        </div>
      </div>
    </main>
  );
}
