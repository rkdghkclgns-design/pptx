"use client";

import { Check } from "lucide-react";
import { THEMES, type PptxTheme } from "@/lib/themes";

interface ThemeSelectorProps {
  selected: string;
  onSelect: (themeId: string) => void;
  disabled?: boolean;
}

export default function ThemeSelector({
  selected,
  onSelect,
  disabled,
}: ThemeSelectorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm text-zinc-400">
        <span className="text-base">&#x1F3A8;</span>
        <span className="font-semibold text-zinc-200">테마 선택</span>
      </div>
      <div className="grid grid-cols-5 gap-2">
        {THEMES.map((theme) => (
          <button
            key={theme.id}
            onClick={() => !disabled && onSelect(theme.id)}
            disabled={disabled}
            className={`group relative flex flex-col items-center gap-1.5 rounded-xl border p-2 transition-all disabled:opacity-50 ${
              selected === theme.id
                ? "border-cyan-500 bg-cyan-500/10"
                : "border-zinc-700 bg-zinc-800/50 hover:border-zinc-500"
            }`}
          >
            <ThemeSwatch theme={theme} isSelected={selected === theme.id} />
            <span className="text-[10px] leading-tight text-zinc-400">
              {theme.name}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

function ThemeSwatch({
  theme,
  isSelected,
}: {
  theme: PptxTheme;
  isSelected: boolean;
}) {
  return (
    <div
      className="relative h-8 w-full rounded-md"
      style={{ backgroundColor: theme.colors.bg }}
    >
      <div
        className="absolute bottom-1 left-1 h-2.5 w-4 rounded-sm"
        style={{ backgroundColor: theme.colors.card }}
      />
      <div
        className="absolute bottom-1 right-1 h-1 w-5 rounded-full"
        style={{ backgroundColor: theme.colors.accent }}
      />
      {isSelected && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Check className="h-3.5 w-3.5 text-cyan-400" />
        </div>
      )}
    </div>
  );
}
