"use client";

import type { SessionSettings } from "@/lib/types";

interface SettingsPanelProps {
  settings: SessionSettings;
  onSettingsChange: (settings: SessionSettings) => void;
  disabled?: boolean;
}

export default function SettingsPanel({
  settings,
  onSettingsChange,
  disabled,
}: SettingsPanelProps) {
  const handleDurationChange = (value: number) => {
    const clamped = Math.max(1, Math.min(30, value));
    onSettingsChange({
      ...settings,
      duration: clamped,
      slideCount: clamped,
    });
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2 text-sm text-zinc-400">
        <span className="text-base">&#x2699;&#xFE0F;</span>
        <span className="font-semibold text-zinc-200">생성 설정</span>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-zinc-300">
          프레젠테이션 시간 (분)
        </label>
        <div className="flex items-center gap-3">
          <input
            type="number"
            min={1}
            max={30}
            value={settings.duration}
            onChange={(e) => handleDurationChange(Number(e.target.value))}
            disabled={disabled}
            className="w-full rounded-xl border border-zinc-700 bg-zinc-800 px-4 py-3 text-zinc-200 outline-none transition-colors focus:border-cyan-500 disabled:opacity-50"
          />
          <span className="shrink-0 text-sm text-zinc-400">
            분 = {settings.slideCount}장
          </span>
        </div>
        <p className="text-xs text-cyan-400">
          * 1분에 1장의 슬라이드가 생성됩니다. (정확히 매칭됨)
        </p>
      </div>
    </div>
  );
}
