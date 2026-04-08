"use client";

import { useState } from "react";
import { Download, Loader2 } from "lucide-react";

interface DownloadButtonProps {
  runId: number | null;
}

export default function DownloadButton({ runId }: DownloadButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    if (!runId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/download/${runId}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: "다운로드 실패" }));
        alert(err.error ?? "다운로드에 실패했습니다.");
        return;
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `presentation-${runId}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleDownload}
      disabled={!runId || loading}
      className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-3 font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
    >
      {loading ? (
        <Loader2 className="h-5 w-5 animate-spin" />
      ) : (
        <Download className="h-5 w-5" />
      )}
      PPTX 다운로드
    </button>
  );
}
