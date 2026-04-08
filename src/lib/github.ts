import type { SessionSettings } from "./types";

interface TriggerBuildResponse {
  success: boolean;
  runId?: number;
  error?: string;
}

export async function triggerBuild(
  sessionId: string,
  settings: SessionSettings
): Promise<TriggerBuildResponse> {
  const res = await fetch("/api/trigger-build", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId, settings }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    return { success: false, error: data.error ?? "빌드 트리거에 실패했습니다." };
  }

  return res.json();
}

export async function getSessionStatus(sessionId: string) {
  const res = await fetch(`/api/session-status/${sessionId}`);
  if (!res.ok) return null;
  return res.json();
}

export async function getDownloadUrl(runId: number): Promise<string | null> {
  const res = await fetch(`/api/download/${runId}`);
  if (!res.ok) return null;
  const data = await res.json();
  return data.downloadUrl ?? null;
}
