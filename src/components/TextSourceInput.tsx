"use client";

import { useState } from "react";
import { FileText, ChevronDown, ChevronUp } from "lucide-react";

interface TextSourceInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function TextSourceInput({
  value,
  onChange,
  disabled,
}: TextSourceInputProps) {
  const [isOpen, setIsOpen] = useState(!!value);

  return (
    <div className="space-y-2">
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className="flex w-full items-center justify-between rounded-lg border border-zinc-700 bg-zinc-800/50 px-3 py-2 text-left text-sm transition-colors hover:border-zinc-500 disabled:opacity-50"
      >
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-zinc-400" />
          <span className="text-zinc-300">
            텍스트 직접 입력
          </span>
          {value && (
            <span className="rounded bg-cyan-500/15 px-1.5 py-0.5 text-[10px] text-cyan-400">
              {value.length.toLocaleString()}자
            </span>
          )}
        </div>
        {isOpen ? (
          <ChevronUp className="h-4 w-4 text-zinc-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-zinc-500" />
        )}
      </button>

      {isOpen && (
        <div className="space-y-1.5">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            placeholder="NotebookLM 또는 다른 소스에서 복사한 텍스트를 여기에 붙여넣으세요. 이 텍스트가 슬라이드 생성의 핵심 소스로 사용됩니다."
            className="h-40 w-full resize-y rounded-xl border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-200 outline-none placeholder:text-zinc-500 focus:border-cyan-500 disabled:opacity-50"
          />
          <p className="text-[11px] text-zinc-500">
            💡 NotebookLM → 노트북 열기 → 내용 선택 → 복사(Ctrl+C) → 여기에 붙여넣기(Ctrl+V)
          </p>
        </div>
      )}
    </div>
  );
}
